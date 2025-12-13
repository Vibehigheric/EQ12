#!/usr/bin/env python3
"""
EQ12 eBay Intelligence & Business Analytics Module
Advanced marketplace intelligence system with SCADA integration

This module provides:
- eBay marketplace analysis and intelligence
- Competitive product research
- Revenue optimization algorithms
- Digital product opportunity identification
- SCADA data feeds for HMI dashboard integration
"""

import os
import sys
import json
import time
import logging
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import sqlite3
from urllib.parse import urlparse, parse_qs
import re

# Web scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Data analysis
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            f'C:\\EQ12\\logs\\ebay_intelligence_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class eBayProduct:
    """eBay product data structure"""

    product_id: str
    title: str
    price: float
    shipping_cost: float
    total_cost: float
    seller_name: str
    seller_rating: float
    seller_feedback_count: int
    listing_type: str  # auction, buy_it_now, etc.
    condition: str
    location: str
    watchers: int
    bids: int
    time_left: str
    image_url: str
    product_url: str
    category: str
    subcategory: str
    description_length: int
    listing_features: List[str]
    sold_count: int  # for sold listings analysis
    view_count: int
    scraped_date: datetime


@dataclass
class MarketIntelligence:
    """Market intelligence data structure"""

    category: str
    avg_price: float
    median_price: float
    price_range: tuple
    competition_level: str  # low, medium, high
    demand_indicator: float
    supply_indicator: float
    revenue_opportunity: float
    top_sellers: List[str]
    trending_keywords: List[str]
    recommended_price_point: float
    market_saturation: float
    entry_barrier: str  # low, medium, high


class eBayIntelligenceEngine:
    """
    Advanced eBay marketplace intelligence and analytics engine
    Integrates with EQ12 systems for comprehensive market analysis
    """

    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace = Path(workspace_path)
        self.db_path = self.workspace / "data" / "ebay_intelligence.db"
        self.reports_dir = self.workspace / "dashboard"
        self.data_dir = self.workspace / "data"

        # Create directories
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self.init_database()

        # Browser for scraping
        self.driver = None

        # Market intelligence cache
        self.market_cache = {}

    def init_database(self):
        """Initialize SQLite database for eBay intelligence"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ebay_products (
                    product_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    price REAL,
                    shipping_cost REAL,
                    total_cost REAL,
                    seller_name TEXT,
                    seller_rating REAL,
                    seller_feedback_count INTEGER,
                    listing_type TEXT,
                    condition TEXT,
                    location TEXT,
                    watchers INTEGER,
                    bids INTEGER,
                    time_left TEXT,
                    image_url TEXT,
                    product_url TEXT,
                    category TEXT,
                    subcategory TEXT,
                    description_length INTEGER,
                    listing_features TEXT,  -- JSON array
                    sold_count INTEGER,
                    view_count INTEGER,
                    scraped_date TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS market_intelligence (
                    category TEXT PRIMARY KEY,
                    avg_price REAL,
                    median_price REAL,
                    price_range_min REAL,
                    price_range_max REAL,
                    competition_level TEXT,
                    demand_indicator REAL,
                    supply_indicator REAL,
                    revenue_opportunity REAL,
                    top_sellers TEXT,  -- JSON array
                    trending_keywords TEXT,  -- JSON array
                    recommended_price_point REAL,
                    market_saturation REAL,
                    entry_barrier TEXT,
                    analysis_date TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS opportunity_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    opportunity_score REAL,
                    revenue_potential REAL,
                    competition_score REAL,
                    market_trend TEXT,
                    recommended_action TEXT,
                    analysis_date TEXT
                )
            """
            )

        logger.info(" eBay intelligence database initialized")

    def init_browser(self) -> bool:
        """Initialize Chrome browser for eBay scraping"""
        try:
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)

            # Stealth user agent
            options.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            logger.info(" Browser initialized for eBay intelligence gathering")
            return True

        except Exception as e:
            logger.error(f" Failed to initialize browser: {e}")
            return False

    def scrape_category_data(self, category: str, max_pages: int = 5) -> List[eBayProduct]:
        """Scrape eBay data for specific category"""
        products = []

        if not self.driver:
            if not self.init_browser():
                return products

        try:
            # Search for category
            search_url = f"https://www.ebay.com/sch/i.html?_nkw={category.replace(' ', '+')}&_sacat=0&_ipg=200"
            self.driver.get(search_url)

            for page in range(max_pages):
                logger.info(f" Scraping page {page + 1} for category: {category}")

                # Wait for results to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".s-item"))
                )

                # Extract product data
                items = self.driver.find_elements(By.CSS_SELECTOR, ".s-item")

                for item in items[:50]:  # Limit per page
                    try:
                        product = self.extract_product_data(item, category)
                        if product:
                            products.append(product)
                    except Exception as e:
                        logger.warning(f" Failed to extract product data: {e}")
                        continue

                # Go to next page
                try:
                    next_btn = self.driver.find_element(By.CSS_SELECTOR, ".pagination__next")
                    if next_btn.is_enabled():
                        next_btn.click()
                        time.sleep(3)
                    else:
                        break
                except NoSuchElementException:
                    break

            logger.info(f" Scraped {len(products)} products for category: {category}")

        except Exception as e:
            logger.error(f" Failed to scrape category {category}: {e}")

        return products

    def extract_product_data(self, item_element, category: str) -> Optional[eBayProduct]:
        """Extract product data from eBay item element"""
        try:
            # Title
            title_elem = item_element.find_element(By.CSS_SELECTOR, ".s-item__title")
            title = title_elem.text.strip()

            # Price
            price_elem = item_element.find_element(By.CSS_SELECTOR, ".s-item__price")
            price_text = price_elem.text.strip()
            price = self.parse_price(price_text)

            # Shipping
            shipping_cost = 0.0
            try:
                shipping_elem = item_element.find_element(By.CSS_SELECTOR, ".s-item__shipping")
                shipping_text = shipping_elem.text.strip()
                shipping_cost = self.parse_price(shipping_text)
            except NoSuchElementException:
                pass

            # Product URL
            link_elem = item_element.find_element(By.CSS_SELECTOR, ".s-item__link")
            product_url = link_elem.get_attribute("href")

            # Image URL
            img_elem = item_element.find_element(By.CSS_SELECTOR, ".s-item__image img")
            image_url = img_elem.get_attribute("src")

            # Seller info
            seller_name = ""
            seller_rating = 0.0
            try:
                seller_elem = item_element.find_element(By.CSS_SELECTOR, ".s-item__seller-info")
                seller_name = seller_elem.text.strip()
                # Extract rating if available
                rating_elem = item_element.find_element(
                    By.CSS_SELECTOR, ".s-item__seller-info .clipped"
                )
                rating_text = rating_elem.text
                seller_rating = (
                    float(re.search(r"(\d+\.?\d*)%", rating_text).group(1))
                    if re.search(r"(\d+\.?\d*)%", rating_text)
                    else 0.0
                )
            except NoSuchElementException:
                pass

            # Generate product ID from URL
            product_id = self.extract_product_id(product_url)

            product = eBayProduct(
                product_id=product_id,
                title=title,
                price=price,
                shipping_cost=shipping_cost,
                total_cost=price + shipping_cost,
                seller_name=seller_name,
                seller_rating=seller_rating,
                seller_feedback_count=0,  # Would need detailed scraping
                listing_type="buy_it_now",  # Default assumption
                condition="unknown",
                location="unknown",
                watchers=0,
                bids=0,
                time_left="",
                image_url=image_url,
                product_url=product_url,
                category=category,
                subcategory="",
                description_length=len(title),
                listing_features=[],
                sold_count=0,
                view_count=0,
                scraped_date=datetime.now(),
            )

            return product

        except Exception as e:
            logger.warning(f" Failed to extract product data: {e}")
            return None

    def parse_price(self, price_text: str) -> float:
        """Parse price from eBay price text"""
        try:
            # Remove currency symbols and extra text
            price_clean = re.sub(r"[^\d.,]", "", price_text.replace(",", ""))
            if price_clean:
                return float(price_clean)
            return 0.0
        except:
            return 0.0

    def extract_product_id(self, url: str) -> str:
        """Extract product ID from eBay URL"""
        try:
            # eBay URLs contain item ID after /itm/
            match = re.search(r"/itm/(\d+)", url)
            if match:
                return match.group(1)
            # Fallback to hash of URL
            return str(hash(url))
        except:
            return str(hash(url))

    def analyze_market_intelligence(
        self, category: str, products: List[eBayProduct]
    ) -> MarketIntelligence:
        """Analyze market intelligence for category"""
        if not products:
            return None

        # Price analysis
        prices = [p.total_cost for p in products if p.total_cost > 0]
        avg_price = np.mean(prices) if prices else 0
        median_price = np.median(prices) if prices else 0
        price_range = (min(prices), max(prices)) if prices else (0, 0)

        # Competition analysis
        sellers = [p.seller_name for p in products if p.seller_name]
        unique_sellers = len(set(sellers))
        competition_level = (
            "high" if unique_sellers > 50 else "medium" if unique_sellers > 20 else "low"
        )

        # Demand indicators
        total_watchers = sum(p.watchers for p in products)
        total_bids = sum(p.bids for p in products)
        demand_indicator = (total_watchers + total_bids * 2) / len(products) if products else 0

        # Supply indicators
        supply_indicator = len(products)

        # Revenue opportunity calculation
        # Higher prices + lower competition + higher demand = better opportunity
        price_score = min(avg_price / 100, 10)  # Normalize to 0-10
        competition_score = 10 - min(unique_sellers / 10, 10)  # Inverse of competition
        demand_score = min(demand_indicator, 10)
        revenue_opportunity = (price_score + competition_score + demand_score) / 3

        # Top sellers
        seller_counts = {}
        for product in products:
            if product.seller_name:
                seller_counts[product.seller_name] = seller_counts.get(product.seller_name, 0) + 1
        top_sellers = sorted(seller_counts.keys(), key=lambda x: seller_counts[x], reverse=True)[:5]

        # Trending keywords (extract from titles)
        all_words = []
        for product in products:
            words = re.findall(r"\b[a-zA-Z]+\b", product.title.lower())
            all_words.extend([w for w in words if len(w) > 3])

        word_counts = {}
        for word in all_words:
            word_counts[word] = word_counts.get(word, 0) + 1
        trending_keywords = sorted(word_counts.keys(), key=lambda x: word_counts[x], reverse=True)[
            :10
        ]

        # Recommended price point (sweet spot analysis)
        if prices:
            # Find price point with good volume
            price_bins = np.histogram(prices, bins=10)
            max_volume_idx = np.argmax(price_bins[0])
            recommended_price_point = (
                price_bins[1][max_volume_idx] + price_bins[1][max_volume_idx + 1]
            ) / 2
        else:
            recommended_price_point = 0

        # Market saturation
        market_saturation = min(supply_indicator / 1000, 1.0)  # 0-1 scale

        # Entry barrier
        entry_barrier = (
            "high"
            if avg_price > 500 and competition_level == "high"
            else "medium" if avg_price > 100 else "low"
        )

        intelligence = MarketIntelligence(
            category=category,
            avg_price=avg_price,
            median_price=median_price,
            price_range=price_range,
            competition_level=competition_level,
            demand_indicator=demand_indicator,
            supply_indicator=supply_indicator,
            revenue_opportunity=revenue_opportunity,
            top_sellers=top_sellers,
            trending_keywords=trending_keywords,
            recommended_price_point=recommended_price_point,
            market_saturation=market_saturation,
            entry_barrier=entry_barrier,
        )

        return intelligence

    def save_products_to_db(self, products: List[eBayProduct]):
        """Save scraped products to database"""
        with sqlite3.connect(self.db_path) as conn:
            for product in products:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO ebay_products VALUES 
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        product.product_id,
                        product.title,
                        product.price,
                        product.shipping_cost,
                        product.total_cost,
                        product.seller_name,
                        product.seller_rating,
                        product.seller_feedback_count,
                        product.listing_type,
                        product.condition,
                        product.location,
                        product.watchers,
                        product.bids,
                        product.time_left,
                        product.image_url,
                        product.product_url,
                        product.category,
                        product.subcategory,
                        product.description_length,
                        json.dumps(product.listing_features),
                        product.sold_count,
                        product.view_count,
                        product.scraped_date.isoformat(),
                    ),
                )

        logger.info(f" Saved {len(products)} products to database")

    def save_intelligence_to_db(self, intelligence: MarketIntelligence):
        """Save market intelligence to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO market_intelligence VALUES 
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    intelligence.category,
                    intelligence.avg_price,
                    intelligence.median_price,
                    intelligence.price_range[0],
                    intelligence.price_range[1],
                    intelligence.competition_level,
                    intelligence.demand_indicator,
                    intelligence.supply_indicator,
                    intelligence.revenue_opportunity,
                    json.dumps(intelligence.top_sellers),
                    json.dumps(intelligence.trending_keywords),
                    intelligence.recommended_price_point,
                    intelligence.market_saturation,
                    intelligence.entry_barrier,
                    datetime.now().isoformat(),
                ),
            )

        logger.info(f" Saved market intelligence for category: {intelligence.category}")

    def generate_business_report(self, categories: List[str]) -> str:
        """Generate comprehensive business intelligence report"""
        report_data = {
            "generated_date": datetime.now().isoformat(),
            "categories_analyzed": len(categories),
            "total_products_analyzed": 0,
            "top_opportunities": [],
            "market_insights": {},
            "revenue_projections": {},
        }

        # Load intelligence data from database
        with sqlite3.connect(self.db_path) as conn:
            for category in categories:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT * FROM market_intelligence 
                    WHERE category = ? 
                    ORDER BY analysis_date DESC 
                    LIMIT 1
                """,
                    (category,),
                )

                row = cursor.fetchone()
                if row:
                    intelligence = {
                        "category": row[0],
                        "avg_price": row[1],
                        "median_price": row[2],
                        "competition_level": row[5],
                        "revenue_opportunity": row[8],
                        "recommended_price_point": row[11],
                        "market_saturation": row[12],
                        "entry_barrier": row[13],
                    }

                    report_data["market_insights"][category] = intelligence

                    # Count products for this category
                    cursor.execute(
                        "SELECT COUNT(*) FROM ebay_products WHERE category = ?", (category,)
                    )
                    product_count = cursor.fetchone()[0]
                    report_data["total_products_analyzed"] += product_count

                    # Add to opportunities if score is high
                    if intelligence["revenue_opportunity"] > 6.0:
                        report_data["top_opportunities"].append(
                            {
                                "category": category,
                                "opportunity_score": intelligence["revenue_opportunity"],
                                "estimated_monthly_revenue": intelligence["avg_price"]
                                * 30
                                * (1 - intelligence["market_saturation"]),
                                "entry_barrier": intelligence["entry_barrier"],
                            }
                        )

        # Sort opportunities by score
        report_data["top_opportunities"].sort(key=lambda x: x["opportunity_score"], reverse=True)

        # Generate HTML report
        html_report = self.create_html_business_report(report_data)

        # Save report
        report_path = (
            self.reports_dir
            / f"ebay_business_intelligence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_report)

        logger.info(f" Business intelligence report generated: {report_path}")
        return str(report_path)

    def create_html_business_report(self, data: Dict) -> str:
        """Create HTML business intelligence report"""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EQ12 eBay Business Intelligence Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #fff;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        h1 {{
            text-align: center;
            color: #00ff7f;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            margin-bottom: 30px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background: rgba(255, 255, 255, 0.15);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #00ff7f;
        }}
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.8;
            margin-top: 5px;
        }}
        .opportunities {{
            margin-bottom: 40px;
        }}
        .opportunity-item {{
            background: rgba(0, 255, 127, 0.1);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #00ff7f;
        }}
        .opportunity-score {{
            font-weight: bold;
            color: #00ff7f;
        }}
        .market-insights {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .insight-card {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .insight-title {{
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #00bfff;
        }}
        .insight-detail {{
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
        }}
        .insight-label {{
            opacity: 0.8;
        }}
        .insight-value {{
            font-weight: bold;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            opacity: 0.7;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1> EQ12 eBay Business Intelligence Report</h1>
        
        <div class="summary">
            <div class="metric-card">
                <div class="metric-value">{data['categories_analyzed']}</div>
                <div class="metric-label">Categories Analyzed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{data['total_products_analyzed']:,}</div>
                <div class="metric-label">Products Analyzed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(data['top_opportunities'])}</div>
                <div class="metric-label">High-Value Opportunities</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${sum(opp.get('estimated_monthly_revenue', 0) for opp in data['top_opportunities'][:3]):,.0f}</div>
                <div class="metric-label">Est. Monthly Revenue (Top 3)</div>
            </div>
        </div>
        
        <div class="opportunities">
            <h2> Top Revenue Opportunities</h2>
"""

        for opp in data["top_opportunities"][:5]:
            html += f"""
            <div class="opportunity-item">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{opp['category']}</strong>
                        <div>Opportunity Score: <span class="opportunity-score">{opp['opportunity_score']:.1f}/10</span></div>
                        <div>Entry Barrier: {opp['entry_barrier'].title()}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.2em; font-weight: bold; color: #00ff7f;">
                            ${opp.get('estimated_monthly_revenue', 0):,.0f}/month
                        </div>
                        <div style="font-size: 0.9em; opacity: 0.8;">Estimated Revenue</div>
                    </div>
                </div>
            </div>
"""

        html += """
        </div>
        
        <div class="market-insights">
            <h2> Market Intelligence by Category</h2>
"""

        for category, insight in data["market_insights"].items():
            html += f"""
            <div class="insight-card">
                <div class="insight-title">{category}</div>
                <div class="insight-detail">
                    <span class="insight-label">Average Price:</span>
                    <span class="insight-value">${insight['avg_price']:.2f}</span>
                </div>
                <div class="insight-detail">
                    <span class="insight-label">Competition Level:</span>
                    <span class="insight-value">{insight['competition_level'].title()}</span>
                </div>
                <div class="insight-detail">
                    <span class="insight-label">Revenue Opportunity:</span>
                    <span class="insight-value">{insight['revenue_opportunity']:.1f}/10</span>
                </div>
                <div class="insight-detail">
                    <span class="insight-label">Recommended Price:</span>
                    <span class="insight-value">${insight['recommended_price_point']:.2f}</span>
                </div>
                <div class="insight-detail">
                    <span class="insight-label">Market Saturation:</span>
                    <span class="insight-value">{insight['market_saturation']:.1%}</span>
                </div>
                <div class="insight-detail">
                    <span class="insight-label">Entry Barrier:</span>
                    <span class="insight-value">{insight['entry_barrier'].title()}</span>
                </div>
            </div>
"""

        html += f"""
        </div>
        
        <div class="footer">
            <p>Generated by EQ12 eBay Intelligence Engine on {data['generated_date']}</p>
            <p> Industrial-grade marketplace intelligence for digital entrepreneurs</p>
        </div>
    </div>
</body>
</html>
"""

        return html

    def close_browser(self):
        """Close browser session"""
        if self.driver:
            self.driver.quit()
            self.driver = None


def main():
    """Main execution function for eBay intelligence"""
    logger.info(" Starting EQ12 eBay Intelligence Engine")

    # Initialize intelligence engine
    engine = eBayIntelligenceEngine()

    # Target categories for analysis (high-value digital products)
    target_categories = [
        "information products",
        "digital downloads",
        "software",
        "online courses",
        "ebooks",
        "templates",
        "spreadsheets",
        "business tools",
        "productivity software",
        "educational materials",
    ]

    all_intelligence = []

    # Analyze each category
    for category in target_categories:
        logger.info(f" Analyzing category: {category}")

        # Scrape product data
        products = engine.scrape_category_data(category, max_pages=3)

        if products:
            # Save products to database
            engine.save_products_to_db(products)

            # Analyze market intelligence
            intelligence = engine.analyze_market_intelligence(category, products)
            if intelligence:
                engine.save_intelligence_to_db(intelligence)
                all_intelligence.append(intelligence)

        # Delay between categories to avoid rate limiting
        time.sleep(5)

    # Generate comprehensive business report
    if all_intelligence:
        report_path = engine.generate_business_report(target_categories)
        logger.info(f" Business intelligence report generated: {report_path}")

    # Close browser
    engine.close_browser()

    logger.info(" EQ12 eBay Intelligence Engine analysis complete")
    logger.info(
        f" Analyzed {len(all_intelligence)} categories with actionable market intelligence"
    )


if __name__ == "__main__":
    main()
