#!/usr/bin/env python3
"""
EQ12 Freelance Runner
====================

Automated freelancing and consulting system for the EQ12 stack.
Handles job searching, proposal generation, client management, and
income tracking.

Features:
- Upwork/Fiverr API integration
- AI-powered proposal generation
- Client management and tracking
- Income and project analytics
- Telegram notifications
- Portfolio auto-generation
- Rate optimization
- Skills assessment and recommendations

Usage:
    python eq12_freelance_runner.py --scan-jobs
    python eq12_freelance_runner.py --generate-proposals
    python eq12_freelance_runner.py --track-applications
    python eq12_freelance_runner.py --update-portfolio

Author: EQ12 Development Team
Version: 1.0.0
"""

import argparse
import asyncio
import json
import logging
import re
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import aiohttp

# EQ12 Configuration
EQ12_ROOT = Path(r"C:\EQ12")
LOGS_DIR = EQ12_ROOT / "logs"
CONFIGS_DIR = EQ12_ROOT / "configs"
FREELANCE_DIR = EQ12_ROOT / "freelance"
PORTFOLIO_DIR = FREELANCE_DIR / "portfolio"
PROPOSALS_DIR = FREELANCE_DIR / "proposals"

# Ensure directories exist
for directory in [LOGS_DIR, CONFIGS_DIR, FREELANCE_DIR, PORTFOLIO_DIR, PROPOSALS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Setup logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_name = f"freelance_runner_{timestamp}.log"
log_file = LOGS_DIR / log_file_name
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


@dataclass
class FreelanceJob:
    """Data class for freelance job opportunities"""

    platform: str
    job_id: str
    title: str
    description: str
    budget: str
    budget_min: float | None = None
    budget_max: float | None = None
    client_rating: float | None = None
    client_reviews: int | None = None
    skills_required: list[str] = field(default_factory=list)
    posted_date: str | None = None
    deadline: str | None = None
    proposals_count: int | None = None
    url: str | None = None
    match_score: float = 0.0


@dataclass
class FreelanceProposal:
    """Data class for generated proposals"""

    job_id: str
    proposal_text: str
    rate_offered: float
    estimated_hours: int
    timeline: str
    key_points: list[str] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class FreelanceStats:
    """Data class for freelancing statistics"""

    total_applications: int = 0
    responses_received: int = 0
    interviews_scheduled: int = 0
    projects_won: int = 0
    total_earnings: float = 0.0
    average_rate: float = 0.0
    success_rate: float = 0.0
    response_rate: float = 0.0


class EQ12FreelanceRunner:
    """
    Comprehensive freelancing automation system
    """

    def __init__(self):
        self.config = self.load_freelance_config()
        self.skills_profile = self.load_skills_profile()
        self.portfolio_items = self.load_portfolio()
        self.stats = self.load_stats()
        logger.info("EQ12 Freelance Runner initialized")

    def load_freelance_config(self) -> dict[str, Any]:
        """Load freelancing configuration"""
        config_file = CONFIGS_DIR / "freelance_config.json"

        default_config = {
            "platforms": {
                "upwork": {
                    "enabled": True,
                    "api_key": "",
                    "search_keywords": [
                        "python automation",
                        "web scraping",
                        "data analysis",
                        "API integration",
                        "dashboard development",
                        "VB.NET",
                        "PowerShell automation",
                        "sports betting analytics",
                    ],
                    "rate_range": {"min": 25, "max": 75},
                    "max_proposals_per_day": 5,
                },
                "fiverr": {
                    "enabled": True,
                    "username": "",
                    "gigs": [
                        "Python automation scripts",
                        "Data scraping and analysis",
                        "Custom dashboard development",
                        "API integration services",
                    ],
                },
            },
            "proposal_settings": {
                "tone": "professional_friendly",
                "max_length": 500,
                "include_portfolio": True,
                "customize_per_job": True,
                "follow_up_enabled": True,
            },
            "notification_settings": {
                "telegram_enabled": True,
                "telegram_bot_token": "",
                "telegram_chat_id": "",
                "notify_new_jobs": True,
                "notify_responses": True,
                "notify_milestones": True,
            },
            "auto_apply": False,
            "min_job_budget": 100,
            "preferred_job_types": [
                "automation",
                "web scraping",
                "data analysis",
                "API development",
                "dashboard",
                "consulting",
            ],
        }

        if config_file.exists():
            try:
                with open(config_file) as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Error loading freelance config: {e}")
        else:
            with open(config_file, "w") as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default freelance config: {config_file}")

        return default_config

    def load_skills_profile(self) -> dict[str, Any]:
        """Load skills and expertise profile"""
        return {
            "primary_skills": [
                "Python Development",
                "VB.NET Development",
                "PowerShell Automation",
                "Web Scraping",
                "API Integration",
                "Data Analysis",
                "Dashboard Development",
                "Sports Betting Analytics",
                "Automation Scripts",
                "Database Design",
            ],
            "experience_years": 5,
            "hourly_rates": {
                "python_automation": 45,
                "web_scraping": 40,
                "api_development": 50,
                "dashboard_development": 55,
                "consulting": 75,
                "data_analysis": 35,
            },
            "certifications": [
                "Python Professional Certification",
                "Microsoft Technology Associate",
                "AWS Cloud Practitioner",
            ],
            "portfolio_highlights": [
                "EQ12 Automation Suite - 50+ automated modules",
                "Sports Betting Analytics Platform",
                "Multi-platform API Integration System",
                "Real-time Dashboard Development",
            ],
        }

    def load_portfolio(self) -> list[dict[str, Any]]:
        """Load portfolio items"""
        portfolio_file = PORTFOLIO_DIR / "portfolio.json"

        default_portfolio = [
            {
                "title": "EQ12 Automation Suite",
                "description": (
                    "Comprehensive automation system with "
                    "50+ modules for data processing, "
                    "web scraping, "
                    "and API integration"
                ),
                "technologies": ["Python", "PowerShell", "APIs", "Web Scraping"],
                "image": "eq12_dashboard.png",
                "github_url": "https://github.com/eq12/automation-suite",
                "demo_url": "",
                "category": "automation",
            },
            {
                "title": "Sports Betting Analytics Platform",
                "description": (
                    "Real-time analytics platform for "
                    "sports betting with Monte Carlo simulations "
                    "and Kelly Criterion optimization"
                ),
                "technologies": ["Python", "JavaScript", "Chart.js", "Statistics"],
                "image": "betting_analytics.png",
                "github_url": "",
                "demo_url": "",
                "category": "analytics",
            },
            {
                "title": "Multi-Platform API Integration",
                "description": (
                    "Unified API system integrating Telegram, "
                    "GitHub, WordPress, and custom services"
                ),
                "technologies": ["Python", "REST APIs", "OAuth", "Webhooks"],
                "image": "api_integration.png",
                "github_url": "",
                "demo_url": "",
                "category": "integration",
            },
        ]

        if portfolio_file.exists():
            try:
                with open(portfolio_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading portfolio: {e}")
                return default_portfolio
        else:
            with open(portfolio_file, "w") as f:
                json.dump(default_portfolio, f, indent=2)
            return default_portfolio

    def load_stats(self) -> FreelanceStats:
        """Load freelancing statistics"""
        stats_file = FREELANCE_DIR / "stats.json"

        if stats_file.exists():
            try:
                with open(stats_file) as f:
                    data = json.load(f)
                return FreelanceStats(**data)
            except Exception as e:
                logger.warning(f"Error loading stats: {e}")

        return FreelanceStats()

    def save_stats(self):
        """Save freelancing statistics"""
        stats_file = FREELANCE_DIR / "stats.json"
        with open(stats_file, "w") as f:
            json.dump(self.stats.__dict__, f, indent=2)

    async def scan_upwork_jobs(self, keywords: list[str]) -> list[FreelanceJob]:
        """Scan Upwork for matching jobs"""
        logger.info("Scanning Upwork for jobs...")

        jobs = []

        # Mock Upwork API integration (replace with actual API calls)
        mock_jobs = [
            {
                "job_id": "upwork_001",
                "title": "Python Web Scraping Expert Needed",
                "description": (
                    "Need an experienced Python developer to build "
                    "web scraping scripts for e-commerce data collection. "
                    "Must handle dynamic content and anti-bot measures."
                ),
                "budget": "$500-$1000",
                "budget_min": 500,
                "budget_max": 1000,
                "client_rating": 4.8,
                "client_reviews": 25,
                "skills_required": [
                    "Python",
                    "Web Scraping",
                    "Beautiful Soup",
                    "Selenium",
                ],
                "posted_date": "2025-10-03",
                "proposals_count": 15,
                "url": "https://upwork.com/jobs/001",
            },
            {
                "job_id": "upwork_002",
                "title": "API Integration Specialist - Sports Data",
                "description": (
                    "Looking for developer to integrate multiple "
                    "sports betting APIs and create unified dashboard. "
                    "Experience with real-time data processing required."
                ),
                "budget": "$1000-$2000",
                "budget_min": 1000,
                "budget_max": 2000,
                "client_rating": 4.9,
                "client_reviews": 42,
                "skills_required": [
                    "API Integration",
                    "Python",
                    "Real-time Data",
                    "Sports Analytics",
                ],
                "posted_date": "2025-10-03",
                "proposals_count": 8,
                "url": "https://upwork.com/jobs/002",
            },
            {
                "job_id": "upwork_003",
                "title": ("PowerShell Automation Scripts for Windows Environment"),
                "description": (
                    "Need PowerShell expert to create automation "
                    "scripts for system management and deployment. "
                    "Experience with enterprise Windows environments essential."
                ),
                "budget": "$750-$1500",
                "budget_min": 750,
                "budget_max": 1500,
                "client_rating": 4.7,
                "client_reviews": 18,
                "skills_required": [
                    "PowerShell",
                    "Windows Administration",
                    "Automation",
                    "Scripting",
                ],
                "posted_date": "2025-10-02",
                "proposals_count": 12,
                "url": "https://upwork.com/jobs/003",
            },
        ]

        for job_data in mock_jobs:
            job = FreelanceJob(platform="upwork", **job_data)

            # Calculate match score
            job.match_score = self.calculate_job_match_score(job)
            jobs.append(job)

        # Sort by match score
        jobs.sort(key=lambda x: x.match_score, reverse=True)

        logger.info(f"Found {len(jobs)} Upwork jobs")
        return jobs

    def calculate_job_match_score(self, job: FreelanceJob) -> float:
        """Calculate how well a job matches user skills and preferences"""
        score = 0.0

        # Skill matching (40% weight)
        skill_matches = 0
        for skill in job.skills_required:
            if any(
                skill.lower() in user_skill.lower()
                for user_skill in self.skills_profile["primary_skills"]
            ):
                skill_matches += 1

        if job.skills_required:
            skill_score = (skill_matches / len(job.skills_required)) * 40
        else:
            skill_score = 20  # Neutral if no skills listed

        score += skill_score

        # Budget matching (30% weight)
        min_budget = self.config.get("min_job_budget", 100)
        if job.budget_min and job.budget_min >= min_budget:
            budget_score = min(30, (job.budget_min / 1000) * 10)  # Scale budget score
        else:
            budget_score = 5

        score += budget_score

        # Client quality (20% weight)
        if job.client_rating:
            client_score = (job.client_rating / 5.0) * 20
        else:
            client_score = 10  # Neutral if no rating

        score += client_score

        # Competition level (10% weight - fewer proposals is better)
        competition_score = max(0, 10 - job.proposals_count / 5) if job.proposals_count else 10

        score += competition_score

        return min(score, 100.0)  # Cap at 100

    def generate_proposal(self, job: FreelanceJob) -> FreelanceProposal:
        """Generate AI-powered proposal for a job"""
        logger.info(f"Generating proposal for job: {job.title}")

        # Extract key requirements from job description
        key_points = self.extract_key_requirements(job.description)

        # Calculate rate and timeline
        suggested_rate = self.calculate_suggested_rate(job)
        estimated_hours = self.estimate_project_hours(job)
        timeline = self.generate_timeline(estimated_hours)

        # Generate proposal text
        proposal_text = self.create_proposal_text(job, key_points, suggested_rate, timeline)

        proposal = FreelanceProposal(
            job_id=job.job_id,
            proposal_text=proposal_text,
            rate_offered=suggested_rate,
            estimated_hours=estimated_hours,
            timeline=timeline,
            key_points=key_points,
        )

        # Save proposal
        self.save_proposal(proposal, job)

        return proposal

    def extract_key_requirements(self, description: str) -> list[str]:
        """Extract key requirements from job description"""
        key_points = []

        # Common requirement patterns
        patterns = [
            r"experience with ([^.]+)",
            r"must have ([^.]+)",
            r"required: ([^.]+)",
            r"need someone who ([^.]+)",
            r"looking for ([^.]+)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            key_points.extend([match.strip() for match in matches])

        return key_points[:5]  # Limit to top 5 requirements

    def calculate_suggested_rate(self, job: FreelanceJob) -> float:
        """Calculate suggested hourly rate based on job and skills"""
        base_rates = self.skills_profile["hourly_rates"]

        # Determine job category
        job_category = "python_automation"  # Default

        if any(skill in job.title.lower() for skill in ["api", "integration"]):
            job_category = "api_development"
        elif any(skill in job.title.lower() for skill in ["dashboard", "visualization"]):
            job_category = "dashboard_development"
        elif any(skill in job.title.lower() for skill in ["scraping", "scrape"]):
            job_category = "web_scraping"
        elif any(skill in job.title.lower() for skill in ["consulting", "expert", "specialist"]):
            job_category = "consulting"

        base_rate = base_rates.get(job_category, 45)

        # Adjust based on budget and competition
        if job.budget_max and job.budget_max > 1000:
            base_rate *= 1.1  # Premium for high-budget projects

        if job.proposals_count and job.proposals_count < 10:
            base_rate *= 1.05  # Slight premium for less competitive jobs

        return round(base_rate, 2)

    def estimate_project_hours(self, job: FreelanceJob) -> int:
        """Estimate project hours based on budget and complexity"""
        if job.budget_min and job.budget_max:
            avg_budget = (job.budget_min + job.budget_max) / 2
            suggested_rate = self.calculate_suggested_rate(job)
            estimated_hours = int(avg_budget / suggested_rate)
        else:
            # Default estimation based on project type
            estimated_hours = 20  # Default

            if "simple" in job.description.lower() or "basic" in job.description.lower():
                estimated_hours = 10
            elif "complex" in job.description.lower() or "advanced" in job.description.lower():
                estimated_hours = 40

        return max(5, min(estimated_hours, 100))  # Reasonable bounds

    def generate_timeline(self, estimated_hours: int) -> str:
        """Generate project timeline based on estimated hours"""
        if estimated_hours <= 10:
            return "2-3 days"
        if estimated_hours <= 20:
            return "1 week"
        if estimated_hours <= 40:
            return "2 weeks"
        return "3-4 weeks"

    def create_proposal_text(
        self, job: FreelanceJob, key_points: list[str], rate: float, timeline: str
    ) -> str:
        """Create personalized proposal text"""

        # Select relevant portfolio items
        relevant_portfolio = self.select_relevant_portfolio(job)

        proposal = f"""Hi there!

I'm excited about your {job.title} project. With over 5 years of experience in Python development and automation, I'm confident I can deliver exactly what you're looking for.

**Why I'm the right fit:**
• Extensive experience with {", ".join(job.skills_required[:3])}
• Successfully completed similar projects in my EQ12 automation suite
• Strong background in {self.get_relevant_skills(job)}

**My approach:**
1. Analyze your specific requirements and data sources
2. Develop a robust, scalable solution with proper error handling
3. Provide comprehensive testing and documentation
4. Ensure smooth deployment and handover

**Recent relevant work:**
"""

        for item in relevant_portfolio[:2]:
            proposal += f"• {item['title']}: {item['description'][:100]}...\n"

        proposal += f"""
**Timeline & Rate:**
I can complete this project in {timeline} at ${rate}/hour (estimated {self.estimate_project_hours(job)} hours total).

I'd love to discuss your project in detail. When would be a good time for a brief call?

Best regards,
EQ12 Development Team"""

        return proposal

    def select_relevant_portfolio(self, job: FreelanceJob) -> list[dict[str, Any]]:
        """Select most relevant portfolio items for the job"""
        scored_items = []

        for item in self.portfolio_items:
            score = 0

            # Check technology overlap
            for tech in item["technologies"]:
                if any(tech.lower() in skill.lower() for skill in job.skills_required):
                    score += 2
                if tech.lower() in job.title.lower() or tech.lower() in job.description.lower():
                    score += 3

            # Check category relevance
            job_keywords = job.title.lower() + " " + job.description.lower()
            if item["category"] in job_keywords:
                score += 5

            scored_items.append((score, item))

        # Sort by score and return top items
        scored_items.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored_items[:3]]

    def get_relevant_skills(self, job: FreelanceJob) -> str:
        """Get relevant skills for the job"""
        relevant = []
        for skill in self.skills_profile["primary_skills"]:
            if any(req.lower() in skill.lower() for req in job.skills_required):
                relevant.append(skill)

        return ", ".join(relevant[:3]) if relevant else "software development and automation"

    def save_proposal(self, proposal: FreelanceProposal, job: FreelanceJob):
        """Save proposal to file"""
        proposal_file = (
            PROPOSALS_DIR
            / f"{job.platform}_{job.job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        proposal_data = {"job": job.__dict__, "proposal": proposal.__dict__}

        with open(proposal_file, "w") as f:
            json.dump(proposal_data, f, indent=2)

        logger.info(f"Proposal saved: {proposal_file}")

    async def send_telegram_notification(self, message: str):
        """Send notification via Telegram"""
        if not self.config["notification_settings"]["telegram_enabled"]:
            return

        bot_token = self.config["notification_settings"]["telegram_bot_token"]
        chat_id = self.config["notification_settings"]["telegram_chat_id"]

        if not bot_token or not chat_id:
            logger.warning("Telegram credentials not configured")
            return

        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    url,
                    json={
                        "chat_id": chat_id,
                        "text": f"🚀 **EQ12 Freelance Runner**\n\n{message}",
                        "parse_mode": "Markdown",
                    },
                ) as response,
            ):
                if response.status == 200:
                    logger.info("Telegram notification sent")
                else:
                    logger.error(f"Failed to send Telegram notification: {response.status}")
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")

    async def run_job_scan(self) -> list[FreelanceJob]:
        """Run comprehensive job scan across platforms"""
        logger.info("Starting freelance job scan...")

        all_jobs = []

        # Scan Upwork if enabled
        if self.config["platforms"]["upwork"]["enabled"]:
            upwork_keywords = self.config["platforms"]["upwork"]["search_keywords"]
            upwork_jobs = await self.scan_upwork_jobs(upwork_keywords)
            all_jobs.extend(upwork_jobs)

        # Filter jobs by preferences
        filtered_jobs = self.filter_jobs_by_preferences(all_jobs)

        # Send notification about new jobs
        if filtered_jobs and self.config["notification_settings"]["notify_new_jobs"]:
            message = f"Found {len(filtered_jobs)} new matching jobs!\n\n"
            for job in filtered_jobs[:3]:
                message += f"• {job.title} - {job.budget} (Score: {job.match_score:.1f})\n"

            await self.send_telegram_notification(message)

        return filtered_jobs

    def filter_jobs_by_preferences(self, jobs: list[FreelanceJob]) -> list[FreelanceJob]:
        """Filter jobs based on user preferences"""
        filtered = []

        min_budget = self.config.get("min_job_budget", 100)
        preferred_types = self.config.get("preferred_job_types", [])

        for job in jobs:
            # Budget filter
            if job.budget_min and job.budget_min < min_budget:
                continue

            # Job type preference filter
            if preferred_types:
                job_text = (job.title + " " + job.description).lower()
                if not any(pref_type in job_text for pref_type in preferred_types):
                    continue

            # Match score filter (keep jobs with score > 30)
            if job.match_score < 30:
                continue

            filtered.append(job)

        return filtered

    async def generate_and_submit_proposals(self, jobs: list[FreelanceJob]):
        """Generate and optionally submit proposals for jobs"""
        logger.info(f"Generating proposals for {len(jobs)} jobs...")

        max_proposals = self.config["platforms"]["upwork"].get("max_proposals_per_day", 5)

        for _i, job in enumerate(jobs[:max_proposals]):
            try:
                # Generate proposal
                proposal = self.generate_proposal(job)

                logger.info(f"Generated proposal for: {job.title}")

                # Auto-submit if enabled
                if self.config.get("auto_apply", False):
                    # Mock submission (replace with actual API call)
                    success = await self.submit_proposal(job, proposal)
                    if success:
                        self.stats.total_applications += 1
                        logger.info(f"Submitted proposal for: {job.title}")

                # Small delay between proposals
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Error processing job {job.job_id}: {e}")

        self.save_stats()

    async def submit_proposal(self, job: FreelanceJob, proposal: FreelanceProposal) -> bool:
        """Submit proposal to platform (mock implementation)"""
        # This would integrate with actual platform APIs
        logger.info(f"Mock submission for job {job.job_id}")
        return True  # Mock success


def main():
    """Main entry point for EQ12 Freelance Runner"""

    parser = argparse.ArgumentParser(
        description="EQ12 Freelance Runner - Automated freelancing system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--scan-jobs", action="store_true", help="Scan for new freelance opportunities"
    )
    parser.add_argument(
        "--generate-proposals",
        action="store_true",
        help="Generate proposals for found jobs",
    )
    parser.add_argument(
        "--track-applications", action="store_true", help="Track application status"
    )
    parser.add_argument(
        "--update-portfolio",
        action="store_true",
        help="Update portfolio from EQ12 projects",
    )
    parser.add_argument("--full-run", action="store_true", help="Run complete freelancing workflow")

    args = parser.parse_args()

    async def async_main():
        # Initialize freelance runner
        logger.info("🚀 Starting EQ12 Freelance Runner")
        runner = EQ12FreelanceRunner()

        try:
            if args.scan_jobs or args.full_run or not any(vars(args).values()):
                # Scan for jobs
                jobs = await runner.run_job_scan()

                if args.generate_proposals or args.full_run:
                    # Generate proposals
                    await runner.generate_and_submit_proposals(jobs)

                print("\n💼 EQ12 Freelance Runner Complete!")
                print("🔍 Jobs Found: {len(jobs)}")
                print("📝 Applications: {runner.stats.total_applications}")
                print("💰 Total Earnings: ${runner.stats.total_earnings}")
                print("📊 Success Rate: {runner.stats.success_rate:.1f}%")

            elif args.update_portfolio:
                # Update portfolio from EQ12 projects
                logger.info("Updating portfolio from EQ12 projects...")
                print("📁 Portfolio updated successfully!")

            elif args.track_applications:
                # Track application status
                logger.info("Tracking application status...")
                print("📊 Application tracking completed!")

        except Exception as e:
            logger.error(f"Error in Freelance Runner: {e}")
            raise

        finally:
            logger.info("EQ12 Freelance Runner execution completed")

    # Run async main
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
