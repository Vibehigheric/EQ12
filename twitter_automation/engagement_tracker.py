#!/usr/bin/env python3
"""
Twitter Engagement Tracker - Free engagement analytics
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

class EngagementTracker:
    def __init__(self):
        self.nitter_instances = ["nitter.net", "nitter.it", "nitter.cc"]
    
    def track_user_engagement(self, username):
        """Track user engagement using free methods"""
        
        engagement_data = {
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "metrics": {},
            "recent_tweets": []
        }
        
        # Try different Nitter instances
        for instance in self.nitter_instances:
            try:
                profile_url = f"https://{instance}/{username}"
                response = requests.get(profile_url, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract profile metrics
                    metrics = self._extract_profile_metrics(soup)
                    if metrics:
                        engagement_data["metrics"] = metrics
                    
                    # Extract recent tweet engagement
                    tweets = self._extract_recent_tweets(soup)
                    if tweets:
                        engagement_data["recent_tweets"] = tweets
                    
                    break  # Success, no need to try other instances
                    
            except Exception as e:
                print(f"Failed to get data from {instance}: {e}")
                continue
        
        return engagement_data
    
    def _extract_profile_metrics(self, soup):
        """Extract profile metrics from Nitter page"""
        metrics = {}
        
        try:
            # Look for stat elements
            stat_elements = soup.find_all(['span', 'div'], class_=re.compile(r'stat'))
            
            for element in stat_elements:
                text = element.get_text(strip=True).lower()
                numbers = re.findall(r'[\d,]+', text)
                
                if 'tweet' in text and numbers:
                    metrics['tweets'] = numbers[0].replace(',', '')
                elif 'following' in text and numbers:
                    metrics['following'] = numbers[0].replace(',', '')
                elif 'follower' in text and numbers:
                    metrics['followers'] = numbers[0].replace(',', '')
            
            # Calculate engagement rate estimate
            if 'followers' in metrics and 'tweets' in metrics:
                try:
                    followers = int(metrics['followers'].replace(',', ''))
                    tweets = int(metrics['tweets'].replace(',', ''))
                    
                    if followers > 0:
                        metrics['tweet_frequency'] = tweets / max(followers / 1000, 1)
                        
                except ValueError:
                    pass
                    
        except Exception as e:
            print(f"Error extracting profile metrics: {e}")
        
        return metrics
    
    def _extract_recent_tweets(self, soup):
        """Extract recent tweets and their engagement"""
        tweets = []
        
        try:
            # Find tweet elements
            tweet_elements = soup.find_all(['div'], class_=re.compile(r'tweet'))
            
            for tweet_element in tweet_elements[:10]:  # Last 10 tweets
                tweet_data = {}
                
                # Extract tweet text
                text_element = tweet_element.find(['div'], class_=re.compile(r'tweet-content'))
                if text_element:
                    tweet_data['content'] = text_element.get_text(strip=True)[:200]
                
                # Extract engagement numbers
                engagement_elements = tweet_element.find_all(['span'], class_=re.compile(r'tweet-stat'))
                
                for element in engagement_elements:
                    text = element.get_text(strip=True)
                    numbers = re.findall(r'\d+', text)
                    
                    if numbers:
                        if 'retweet' in text.lower():
                            tweet_data['retweets'] = numbers[0]
                        elif 'like' in text.lower():
                            tweet_data['likes'] = numbers[0]
                        elif 'comment' in text.lower():
                            tweet_data['comments'] = numbers[0]
                
                if tweet_data:
                    tweets.append(tweet_data)
                    
        except Exception as e:
            print(f"Error extracting tweets: {e}")
        
        return tweets
    
    def calculate_engagement_score(self, engagement_data):
        """Calculate overall engagement score"""
        
        try:
            metrics = engagement_data.get('metrics', {})
            tweets = engagement_data.get('recent_tweets', [])
            
            if not metrics.get('followers') or not tweets:
                return 0
            
            followers = int(metrics['followers'].replace(',', ''))
            
            # Calculate average engagement per tweet
            total_engagement = 0
            tweet_count = 0
            
            for tweet in tweets:
                tweet_engagement = 0
                
                if 'likes' in tweet:
                    tweet_engagement += int(tweet['likes'])
                if 'retweets' in tweet:
                    tweet_engagement += int(tweet['retweets']) * 2  # Retweets worth more
                if 'comments' in tweet:
                    tweet_engagement += int(tweet['comments']) * 3  # Comments worth most
                
                total_engagement += tweet_engagement
                tweet_count += 1
            
            if tweet_count > 0 and followers > 0:
                avg_engagement = total_engagement / tweet_count
                engagement_rate = (avg_engagement / followers) * 100
                return round(engagement_rate, 2)
            
        except Exception as e:
            print(f"Error calculating engagement score: {e}")
        
        return 0

if __name__ == "__main__":
    tracker = EngagementTracker()
    
    # Example usage
    username = "elonmusk"
    data = tracker.track_user_engagement(username)
    score = tracker.calculate_engagement_score(data)
    
    print(f"Engagement data for @{username}:")
    print(f"Followers: {data['metrics'].get('followers', 'N/A')}")
    print(f"Engagement Score: {score}%")
    
    # Save to file
    with open(f"engagement_{username}.json", "w") as f:
        json.dump(data, f, indent=2)
