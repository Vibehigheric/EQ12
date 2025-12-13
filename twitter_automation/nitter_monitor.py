#!/usr/bin/env python3
"""
Twitter Nitter Monitor - Free Twitter monitoring using Nitter instances
"""

import requests
import feedparser
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

class NitterMonitor:
    def __init__(self, nitter_instance="nitter.net"):
        self.nitter_instance = nitter_instance
        self.base_url = f"https://{nitter_instance}"
    
    def monitor_user(self, username, check_interval=300):
        """Monitor user tweets via Nitter RSS"""
        rss_url = f"{self.base_url}/{username}/rss"
        
        while True:
            try:
                feed = feedparser.parse(rss_url)
                
                for entry in feed.entries:
                    tweet_data = {
                        "username": username,
                        "title": entry.title,
                        "link": entry.link,
                        "published": entry.published,
                        "content": entry.summary if hasattr(entry, 'summary') else "",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    self.process_tweet(tweet_data)
                    
            except Exception as e:
                print(f"Error monitoring {username}: {e}")
            
            time.sleep(check_interval)
    
    def process_tweet(self, tweet_data):
        """Process detected tweet"""
        print(f"New tweet from @{tweet_data['username']}: {tweet_data['title']}")
        
        # Save to file
        with open(f"tweets_{tweet_data['username']}.json", "a") as f:
            f.write(json.dumps(tweet_data) + "\n")
    
    def get_profile_info(self, username):
        """Get profile information via Nitter"""
        try:
            response = requests.get(f"{self.base_url}/{username}")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract profile stats
            stats = {}
            stat_elements = soup.find_all(['span'], class_='profile-stat-num')
            
            for i, element in enumerate(stat_elements):
                if i == 0:
                    stats['tweets'] = element.get_text(strip=True)
                elif i == 1:
                    stats['following'] = element.get_text(strip=True)
                elif i == 2:
                    stats['followers'] = element.get_text(strip=True)
            
            return stats
            
        except Exception as e:
            print(f"Error getting profile for {username}: {e}")
            return {}

if __name__ == "__main__":
    monitor = NitterMonitor()
    
    # Example usage
    # monitor.monitor_user("elonmusk")
    profile = monitor.get_profile_info("elonmusk")
    print(f"Profile stats: {profile}")
