#!/usr/bin/env python3
"""
Twitter Automation Controller - Orchestrates all free Twitter tools
"""

import json
import time
from datetime import datetime
from pathlib import Path
import argparse

from nitter_monitor import NitterMonitor
from trend_analyzer import TrendAnalyzer
from engagement_tracker import EngagementTracker

class TwitterAutomationController:
    def __init__(self, workspace_path="C:/EQ12"):
        self.workspace_path = Path(workspace_path)
        self.data_dir = self.workspace_path / "data" / "twitter"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.monitor = NitterMonitor()
        self.trend_analyzer = TrendAnalyzer()
        self.engagement_tracker = EngagementTracker()
    
    def run_comprehensive_analysis(self):
        """Run comprehensive Twitter analysis"""
        
        print(" Starting comprehensive Twitter analysis...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "trends": {},
            "opportunities": {},
            "monitoring": {},
            "engagement": {}
        }
        
        # 1. Analyze trends
        print(" Analyzing trends...")
        trends = self.trend_analyzer.get_global_trends()
        opportunities = self.trend_analyzer.analyze_trend_opportunities(trends)
        
        results["trends"] = {
            "total_trends": len(trends),
            "trends": trends[:20],  # Top 20
            "sources": list(set([t["source"] for t in trends]))
        }
        
        results["opportunities"] = {
            "total_opportunities": len(opportunities),
            "high_potential": [o for o in opportunities if o["potential"] == "High"],
            "opportunities": opportunities
        }
        
        # 2. Monitor key accounts
        print(" Analyzing key accounts...")
        key_accounts = ["elonmusk", "naval", "balajis", "sama", "paulg"]
        
        engagement_data = {}
        for account in key_accounts:
            try:
                data = self.engagement_tracker.track_user_engagement(account)
                score = self.engagement_tracker.calculate_engagement_score(data)
                
                engagement_data[account] = {
                    "engagement_score": score,
                    "followers": data["metrics"].get("followers", "N/A"),
                    "recent_tweet_count": len(data["recent_tweets"])
                }
                
                print(f"   @{account}: {score}% engagement, {data['metrics'].get('followers', 'N/A')} followers")
                
            except Exception as e:
                print(f"   Failed to analyze @{account}: {e}")
            
            time.sleep(2)  # Rate limiting
        
        results["engagement"] = engagement_data
        
        # 3. Generate recommendations
        print(" Generating recommendations...")
        recommendations = self._generate_recommendations(results)
        results["recommendations"] = recommendations
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = self.data_dir / f"twitter_analysis_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f" Analysis complete! Results saved to {results_file}")
        
        return results
    
    def _generate_recommendations(self, analysis_results):
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Trend-based recommendations
        high_potential = analysis_results["opportunities"]["high_potential"]
        if high_potential:
            recommendations.append({
                "type": "Trend Opportunity",
                "action": f"Create content around {len(high_potential)} high-potential trends",
                "trends": [o["trend"] for o in high_potential[:5]],
                "priority": "High"
            })
        
        # Engagement-based recommendations
        top_performers = [(k, v) for k, v in analysis_results["engagement"].items() 
                         if v["engagement_score"] > 1.0]
        
        if top_performers:
            recommendations.append({
                "type": "Engagement Strategy", 
                "action": f"Study and model top performers",
                "accounts": [acc[0] for acc in top_performers],
                "priority": "Medium"
            })
        
        # Automation recommendations
        recommendations.append({
            "type": "Automation Setup",
            "action": "Implement automated monitoring and content creation",
            "tools": ["Nitter RSS monitoring", "Trend-based content", "Engagement tracking"],
            "priority": "High"
        })
        
        return recommendations
    
    def monitor_competitors(self, usernames, duration_hours=24):
        """Monitor competitor accounts for specified duration"""
        
        print(f" Monitoring {len(usernames)} accounts for {duration_hours} hours...")
        
        monitoring_data = {
            "start_time": datetime.now().isoformat(),
            "usernames": usernames,
            "duration_hours": duration_hours,
            "updates": []
        }
        
        end_time = time.time() + (duration_hours * 3600)
        
        while time.time() < end_time:
            for username in usernames:
                try:
                    # Check for new tweets via RSS
                    profile_info = self.monitor.get_profile_info(username)
                    
                    if profile_info:
                        update = {
                            "timestamp": datetime.now().isoformat(),
                            "username": username,
                            "stats": profile_info
                        }
                        
                        monitoring_data["updates"].append(update)
                        print(f" Update for @{username}: {profile_info}")
                
                except Exception as e:
                    print(f" Error monitoring @{username}: {e}")
                
                time.sleep(60)  # Check every minute
            
            time.sleep(300)  # Wait 5 minutes between full cycles
        
        # Save monitoring data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        monitoring_file = self.data_dir / f"competitor_monitoring_{timestamp}.json"
        
        with open(monitoring_file, 'w') as f:
            json.dump(monitoring_data, f, indent=2)
        
        print(f" Monitoring complete! Data saved to {monitoring_file}")
        
        return monitoring_data

def main():
    parser = argparse.ArgumentParser(description=" Twitter Automation Controller")
    parser.add_argument("--action", choices=["analyze", "monitor", "trends"], 
                       default="analyze", help="Action to perform")
    parser.add_argument("--accounts", nargs="+", help="Accounts to monitor")
    parser.add_argument("--duration", type=int, default=24, help="Monitoring duration in hours")
    
    args = parser.parse_args()
    
    controller = TwitterAutomationController()
    
    if args.action == "analyze":
        results = controller.run_comprehensive_analysis()
        
        print("\n KEY INSIGHTS:")
        print(f"    Trends Found: {results['trends']['total_trends']}")
        print(f"    Opportunities: {results['opportunities']['total_opportunities']}")
        print(f"    Accounts Analyzed: {len(results['engagement'])}")
        print(f"    Recommendations: {len(results['recommendations'])}")
        
    elif args.action == "monitor" and args.accounts:
        controller.monitor_competitors(args.accounts, args.duration)
        
    elif args.action == "trends":
        analyzer = TrendAnalyzer()
        trends = analyzer.get_global_trends()
        opportunities = analyzer.analyze_trend_opportunities(trends)
        
        print(f" Found {len(trends)} trends:")
        for trend in trends[:10]:
            print(f"   {trend['trend']} ({trend['source']})")
        
        print(f"\n Found {len(opportunities)} opportunities:")
        for opp in opportunities[:5]:
            print(f"   {opp['trend']} - {opp['opportunity']}")

if __name__ == "__main__":
    main()
