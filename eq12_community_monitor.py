"""
EQ12 OpenAI Community Forum Monitor
==================================

Monitors OpenAI Community forum for relevant updates and signals
Pipes notifications to Slack/Teams and creates GitHub issues for actionable items
"""

import json
import logging
import os
import time
from datetime import UTC, datetime, timedelta

import feedparser

try:
    import requests
except ImportError:
    requests = None

try:
    from github import Github
except ImportError:
    Github = None

logger = logging.getLogger(__name__)

# Configuration
FEEDS = {
    "announcements": "https://community.openai.com/c/announcements.rss",
    "api": "https://community.openai.com/c/api.rss",
    "responses": "https://community.openai.com/tag/responses-api.rss",
    "function_calling": "https://community.openai.com/c/function-calling.rss",
    "realtime": "https://community.openai.com/tag/realtime.rss",
    "webhooks": "https://community.openai.com/tag/webhooks.rss",
    "azure": "https://community.openai.com/c/azure-openai.rss",
    "cost_limits": "https://community.openai.com/tag/rate-limits.rss",
    "deprecations": "https://community.openai.com/tag/deprecation.rss"
}

KEYWORDS_HIGH_PRIORITY = [
    "rate limit", "429", "insufficient_quota", "deprecation",
    "webhook", "signature", "responses api", "azure openai",
    "model unavailable", "quota exceeded", "pricing change"
]

KEYWORDS_ACTIONABLE = [
    "best practice", "playbook", "configuration", "troubleshooting",
    "authentication", "retry", "backoff", "idempotency"
]


class OpenAICommunityMonitor:
    """Monitor OpenAI Community forum for EQ12-relevant updates"""

    def __init__(self):
        self.seen_items: set[str] = set()
        self.state_file = "C:/EQ12/logs/community_monitor_state.json"
        self.log_file = "C:/EQ12/logs/community_monitor.log"

        # Webhook/notification configuration
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        self.teams_webhook = os.getenv("TEAMS_WEBHOOK_URL")
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_repo = os.getenv("GITHUB_REPO", "EQ12/community-intel")

        # Load previous state
        self.load_state()

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )

    def load_state(self):
        """Load previously seen items from state file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file) as f:
                    data = json.load(f)
                    self.seen_items = set(data.get('seen_items', []))
                    logger.info(f"Loaded {len(self.seen_items)} seen items from state")
        except Exception as e:
            logger.warning(f"Could not load state: {e}")
            self.seen_items = set()

    def save_state(self):
        """Save current state to file"""
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump({
                    'seen_items': list(self.seen_items),
                    'last_update': datetime.now(UTC).isoformat()
                }, f)
        except Exception as e:
            logger.error(f"Could not save state: {e}")

    def classify_post(self, title: str, content: str = "") -> dict[str, any]:
        """Classify forum post by priority and actionability"""
        title_lower = title.lower()
        content_lower = content.lower()
        full_text = f"{title_lower} {content_lower}"

        classification = {
            'priority': 'low',
            'actionable': False,
            'categories': [],
            'keywords_matched': []
        }

        # Check for high priority indicators
        for keyword in KEYWORDS_HIGH_PRIORITY:
            if keyword in full_text:
                classification['priority'] = 'high'
                classification['keywords_matched'].append(keyword)

        # Check for actionable content
        for keyword in KEYWORDS_ACTIONABLE:
            if keyword in full_text:
                classification['actionable'] = True
                classification['keywords_matched'].append(keyword)

        # Categorize by content type
        if any(word in full_text for word in ['webhook', 'signature', 'hmac']):
            classification['categories'].append('webhooks')
        if any(word in full_text for word in ['rate limit', '429', 'quota']):
            classification['categories'].append('rate_limits')
        if any(word in full_text for word in ['responses api', 'structured output']):
            classification['categories'].append('responses_api')
        if any(word in full_text for word in ['azure openai', 'deployment']):
            classification['categories'].append('azure')
        if any(word in full_text for word in ['cost', 'pricing', 'billing']):
            classification['categories'].append('cost')

        return classification

    def notify_slack(self, title: str, link: str, category: str, priority: str):
        """Send notification to Slack"""
        if not self.slack_webhook or not requests:
            return

        emoji = "🚨" if priority == "high" else "🛰️"
        color = "#ff0000" if priority == "high" else "#36a64f"

        payload = {
            "text": f"{emoji} OpenAI Community Alert",
            "attachments": [{
                "color": color,
                "title": title,
                "title_link": link,
                "fields": [
                    {"title": "Category", "value": category, "short": True},
                    {"title": "Priority", "value": priority.upper(), "short": True}
                ],
                "footer": "EQ12 Community Monitor"
            }]
        }

        try:
            response = requests.post(self.slack_webhook, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"Slack notification sent: {title}")
            else:
                logger.warning(f"Slack notification failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Slack notification error: {e}")

    def create_github_issue(
        self, title: str, link: str, content: str, classification: dict
    ):
        """Create GitHub issue for actionable items"""
        if not self.github_token or not Github:
            return

        try:
            g = Github(self.github_token)
            repo = g.get_repo(self.github_repo)

            issue_title = f"[Community Intel] {title}"
            issue_body = f"""
**Source**: OpenAI Community Forum
**Link**: {link}
**Priority**: {classification['priority']}
**Categories**: {', '.join(classification['categories'])}

**Matched Keywords**: {', '.join(classification['keywords_matched'])}

**Content Summary**:
{content[:500]}{'...' if len(content) > 500 else ''}

---
*This issue was automatically created by EQ12 Community Monitor*
"""

            labels = ['community-intel', f"priority-{classification['priority']}"]
            labels.extend(classification['categories'])

            issue = repo.create_issue(title=issue_title, body=issue_body, labels=labels)
            logger.info(f"GitHub issue created: {issue.html_url}")

        except Exception as e:
            logger.error(f"GitHub issue creation error: {e}")

    def process_feed_entry(self, entry, feed_name: str):
        """Process a single feed entry"""
        entry_id = entry.id if hasattr(entry, 'id') else entry.link

        if entry_id in self.seen_items:
            return

        self.seen_items.add(entry_id)

        title = entry.title
        content = getattr(entry, 'summary', '')
        link = entry.link

        # Classify the post
        classification = self.classify_post(title, content)

        priority = classification['priority']
        logger.info(f"New post [{feed_name}]: {title} (Priority: {priority})")

        # Send notifications based on priority/actionability
        if classification['priority'] == 'high' or classification['actionable']:
            # Slack notification
            category = ', '.join(classification['categories']) or feed_name
            self.notify_slack(title, link, category, classification['priority'])

            # GitHub issue for actionable items
            if classification['actionable']:
                self.create_github_issue(title, link, content, classification)

        # Log to file
        log_entry = {
            'timestamp': datetime.now(UTC).isoformat(),
            'feed': feed_name,
            'title': title,
            'link': link,
            'classification': classification
        }

        date_str = datetime.now().strftime('%Y%m%d')
        log_file = f"C:/EQ12/logs/community_posts_{date_str}.jsonl"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def monitor_feeds(self):
        """Monitor all configured feeds for new posts"""
        logger.info("Starting community forum monitoring cycle")

        new_posts_count = 0

        for feed_name, feed_url in FEEDS.items():
            try:
                logger.debug(f"Checking feed: {feed_name}")
                feed = feedparser.parse(feed_url)

                if hasattr(feed, 'entries'):
                    # Process recent entries (last 10)
                    for entry in feed.entries[:10]:
                        self.process_feed_entry(entry, feed_name)
                        new_posts_count += 1

                else:
                    logger.warning(f"No entries in feed: {feed_name}")

            except Exception as e:
                logger.error(f"Error processing feed {feed_name}: {e}")

        self.save_state()
        logger.info(f"Monitoring complete. Processed {new_posts_count} new posts")

    def run_continuous(self, interval_minutes: int = 15):
        """Run continuous monitoring"""
        msg = f"Starting continuous monitoring (interval: {interval_minutes} minutes)"
        logger.info(msg)

        while True:
            try:
                self.monitor_feeds()
                time.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

    def generate_report(self, days: int = 7) -> dict:
        """Generate report of recent community activity"""
        report = {
            'period_days': days,
            'total_posts': 0,
            'high_priority': 0,
            'actionable': 0,
            'categories': {},
            'top_keywords': {}
        }

        # Read recent log files
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            log_file = f"C:/EQ12/logs/community_posts_{date.strftime('%Y%m%d')}.jsonl"

            if os.path.exists(log_file):
                with open(log_file) as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                            report['total_posts'] += 1

                            classification = entry['classification']
                            if classification['priority'] == 'high':
                                report['high_priority'] += 1
                            if classification['actionable']:
                                report['actionable'] += 1

                            # Count categories
                            for category in classification['categories']:
                                cats = report['categories']
                                cats[category] = cats.get(category, 0) + 1

                            # Count keywords
                            for keyword in classification['keywords_matched']:
                                keys = report['top_keywords']
                                keys[keyword] = keys.get(keyword, 0) + 1

                        except json.JSONDecodeError:
                            continue

        return report


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 OpenAI Community Monitor")
    parser.add_argument(
        "--continuous", action="store_true", help="Run continuous monitoring"
    )
    parser.add_argument(
        "--interval", type=int, default=15,
        help="Monitoring interval in minutes (default: 15)"
    )
    parser.add_argument(
        "--report", type=int, help="Generate report for last N days"
    )
    parser.add_argument(
        "--single", action="store_true", help="Run single monitoring cycle"
    )

    args = parser.parse_args()

    monitor = OpenAICommunityMonitor()

    if args.report:
        report = monitor.generate_report(args.report)
        print(json.dumps(report, indent=2))
    elif args.continuous:
        monitor.run_continuous(args.interval)
    elif args.single:
        monitor.monitor_feeds()
    else:
        print("Use --continuous, --single, or --report <days>")


if __name__ == "__main__":
    main()
 
 
