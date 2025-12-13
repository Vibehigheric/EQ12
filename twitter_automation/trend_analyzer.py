#!/usr/bin/env python3
"""
Twitter Trend Analyzer - Free trend analysis using public sources
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

class TrendAnalyzer:
    def __init__(self):
        self.sources = [
            "https://trendsmap.com/",
            "https://getdaytrends.com/"
        ]
    
    def get_global_trends(self):
        """Get global Twitter trends from free sources"""
        all_trends = []
        
        for source in self.sources:
            try:
                response = requests.get(source, timeout=15)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract trends (source-specific logic)
                if "trendsmap" in source:
                    trends = self._extract_trendsmap_trends(soup)
                elif "getdaytrends" in source:
                    trends = self._extract_daytrends_trends(soup)
                else:
                    trends = self._extract_generic_trends(soup)
                
                all_trends.extend(trends)
                
            except Exception as e:
                print(f"Error getting trends from {source}: {e}")
        
        return self._deduplicate_trends(all_trends)
    
    def _extract_trendsmap_trends(self, soup):
        """Extract trends from Trendsmap"""
        trends = []
        
        # Look for trend elements
        trend_elements = soup.find_all(['span', 'div'], text=re.compile(r'#\w+|@\w+'))
        
        for element in trend_elements[:20]:
            trend_text = element.get_text(strip=True)
            if trend_text and len(trend_text) > 1:
                trends.append({
                    "trend": trend_text,
                    "source": "trendsmap",
                    "timestamp": datetime.now().isoformat()
                })
        
        return trends
    
    def _extract_daytrends_trends(self, soup):
        """Extract trends from GetDayTrends"""
        trends = []
        
        hashtag_elements = soup.find_all(text=re.compile(r'#\w+'))
        
        for hashtag in hashtag_elements[:15]:
            trends.append({
                "trend": hashtag.strip(),
                "source": "getdaytrends", 
                "timestamp": datetime.now().isoformat()
            })
        
        return trends
    
    def _extract_generic_trends(self, soup):
        """Generic trend extraction"""
        trends = []
        
        # Look for hashtags and mentions
        text_content = soup.get_text()
        hashtags = re.findall(r'#\w+', text_content)
        
        for hashtag in hashtags[:10]:
            trends.append({
                "trend": hashtag,
                "source": "generic",
                "timestamp": datetime.now().isoformat()
            })
        
        return trends
    
    def _deduplicate_trends(self, trends):
        """Remove duplicate trends"""
        seen = set()
        unique_trends = []
        
        for trend in trends:
            trend_text = trend["trend"].lower()
            if trend_text not in seen:
                seen.add(trend_text)
                unique_trends.append(trend)
        
        return unique_trends
    
    def analyze_trend_opportunities(self, trends):
        """Analyze trends for business opportunities"""
        
        tech_keywords = ["ai", "crypto", "blockchain", "automation", "api", "saas"]
        business_keywords = ["startup", "business", "marketing", "sales", "revenue"]
        
        opportunities = []
        
        for trend in trends:
            trend_text = trend["trend"].lower()
            
            if any(keyword in trend_text for keyword in tech_keywords):
                opportunities.append({
                    "trend": trend["trend"],
                    "category": "Technology",
                    "opportunity": "Create tech-focused content and tools",
                    "potential": "High"
                })
            elif any(keyword in trend_text for keyword in business_keywords):
                opportunities.append({
                    "trend": trend["trend"],
                    "category": "Business",
                    "opportunity": "Develop business automation solutions",
                    "potential": "Medium-High"
                })
        
        return opportunities

if __name__ == "__main__":
    analyzer = TrendAnalyzer()
    
    trends = analyzer.get_global_trends()
    print(f"Found {len(trends)} trends")
    
    opportunities = analyzer.analyze_trend_opportunities(trends)
    print(f"Found {len(opportunities)} opportunities")
    
    # Save results
    with open("twitter_trends_analysis.json", "w") as f:
        json.dump({
            "trends": trends,
            "opportunities": opportunities,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
