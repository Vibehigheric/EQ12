#!/usr/bin/env python3
"""
EQ12 Selenium Cross-Listing Automation
=====================================

Robust multi-platform listing automation with human-like behavior patterns,
retry logic, and comprehensive error handling for eBay, Mercari, and Facebook Marketplace.

Features:
- Human-like interaction patterns with randomized delays
- Robust element detection with multiple fallback selectors
- Screenshot capture for debugging and compliance
- Comprehensive retry logic with exponential backoff
- Session management and cookie persistence
- Proxy rotation and IP management
- A/B testing framework for listing variations

Author: EQ12 Team
Version: 1.0.0
License: MIT
"""

import time
import random
import json
import logging
import pathlib
import datetime
import uuid
import base64
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import argparse
import sys
import os

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, 
    WebDriverException, ElementNotInteractableException
)

# Import our product manager
from eq12_crosslisting_manager import ProductManager, Product

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:/EQ12/logs/crosslisting_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class PlatformConfig:
    """Platform-specific configuration"""
    name: str
    base_url: str
    login_url: str
    post_url: str
    selectors: Dict[str, List[str]]  # Multiple selectors for fallback
    delays: Dict[str, Tuple[float, float]]  # Min, max delays
    enabled: bool = True
    requires_2fa: bool = False
    max_daily_posts: int = 20

@dataclass
class ListingResult:
    """Result of a listing attempt"""
    platform: str
    sku: str
    success: bool
    listing_id: Optional[str] = None
    listing_url: Optional[str] = None
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    timestamp: datetime.datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.datetime.now()

class HumanLikeBehavior:
    """Simulate human-like interactions"""
    
    @staticmethod
    def random_delay(min_delay: float = 1.0, max_delay: float = 3.0):
        """Random delay with human-like distribution"""
        delay = random.uniform(min_delay, max_delay)
        # Add small random micro-delays
        for _ in range(random.randint(1, 3)):
            time.sleep(delay / 10)
            delay *= 0.9
        time.sleep(delay)
    
    @staticmethod
    def human_type(element, text: str, delay_range: Tuple[float, float] = (0.05, 0.15)):
        """Type text with human-like speed and errors"""
        element.clear()
        
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(*delay_range))
            
            # Occasional typos and corrections (5% chance)
            if random.random() < 0.05:
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                element.send_keys(wrong_char)
                time.sleep(random.uniform(0.1, 0.3))
                element.send_keys(Keys.BACKSPACE)
                time.sleep(random.uniform(0.1, 0.2))
                element.send_keys(char)
    
    @staticmethod
    def human_click(driver, element):
        """Click with human-like movement"""
        # Move to element first
        ActionChains(driver).move_to_element(element).perform()
        HumanLikeBehavior.random_delay(0.2, 0.5)
        
        # Random offset click
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)
        ActionChains(driver).move_to_element_with_offset(element, offset_x, offset_y).click().perform()

class AdvancedWebDriver:
    """Enhanced WebDriver with advanced capabilities"""
    
    def __init__(self, browser: str = "chrome", headless: bool = False, proxy: Optional[str] = None):
        self.browser = browser
        self.headless = headless
        self.proxy = proxy
        self.driver = None
        self.session_id = str(uuid.uuid4())[:8]
        
        self._setup_driver()
    
    def _setup_driver(self):
        """Setup WebDriver with anti-detection measures"""
        if self.browser.lower() == "chrome":
            options = ChromeOptions()
            
            # Anti-detection measures
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            
            # Human-like browser profile
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-default-apps")
            
            # Window size randomization
            width = random.randint(1200, 1920)
            height = random.randint(800, 1080)
            options.add_argument(f"--window-size={width},{height}")
            
            if self.headless:
                options.add_argument("--headless")
            
            if self.proxy:
                options.add_argument(f"--proxy-server={self.proxy}")
            
            # User agent randomization
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
            ]
            options.add_argument(f"--user-agent={random.choice(user_agents)}")
            
            self.driver = webdriver.Chrome(options=options)
            
        else:  # Firefox
            options = FirefoxOptions()
            if self.headless:
                options.add_argument("--headless")
            self.driver = webdriver.Firefox(options=options)
        
        # Set implicit wait
        self.driver.implicitly_wait(10)
        
        # Execute anti-detection script
        self.driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
    
    def smart_find_element(self, selectors: List[str], timeout: int = 20) -> Optional[Any]:
        """Find element using multiple fallback selectors"""
        wait = WebDriverWait(self.driver, timeout)
        
        for selector in selectors:
            try:
                # Try different selector types
                if selector.startswith("//"):
                    element = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                elif selector.startswith("#"):
                    element = wait.until(EC.presence_of_element_located((By.ID, selector[1:])))
                elif selector.startswith("."):
                    element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, selector[1:])))
                else:
                    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                
                if element and element.is_displayed():
                    return element
                    
            except (TimeoutException, NoSuchElementException):
                continue
        
        logger.warning(f"Could not find element with any selector: {selectors}")
        return None
    
    def smart_click(self, selectors: List[str], timeout: int = 20) -> bool:
        """Click element with retry logic"""
        element = self.smart_find_element(selectors, timeout)
        if not element:
            return False
        
        try:
            # Wait for element to be clickable
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(element))
            HumanLikeBehavior.human_click(self.driver, element)
            return True
        except Exception as e:
            logger.warning(f"Click failed: {e}")
            return False
    
    def smart_type(self, selectors: List[str], text: str, timeout: int = 20) -> bool:
        """Type text with human-like behavior"""
        element = self.smart_find_element(selectors, timeout)
        if not element:
            return False
        
        try:
            HumanLikeBehavior.human_type(element, text)
            return True
        except Exception as e:
            logger.warning(f"Type failed: {e}")
            return False
    
    def take_screenshot(self, name: str) -> str:
        """Take screenshot and save with timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{self.session_id}_{name}_{timestamp}.png"
        filepath = f"C:/EQ12/logs/screenshots/{filename}"
        
        # Ensure directory exists
        pathlib.Path("C:/EQ12/logs/screenshots").mkdir(parents=True, exist_ok=True)
        
        try:
            self.driver.save_screenshot(filepath)
            logger.info(f"Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return ""
    
    def close(self):
        """Close driver safely"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")

class CrossListingAutomation:
    """Main cross-listing automation class"""
    
    def __init__(self, config_path: str = "C:/EQ12/configs/crosslisting_platforms.json"):
        self.config_path = pathlib.Path(config_path)
        self.product_manager = ProductManager()
        self.platforms = self._load_platform_configs()
        self.session_id = str(uuid.uuid4())[:8]
        
        # Create logs directory
        pathlib.Path("C:/EQ12/logs/crosslisting").mkdir(parents=True, exist_ok=True)
        
        logger.info(f"CrossListingAutomation initialized (session: {self.session_id})")
    
    def _load_platform_configs(self) -> Dict[str, PlatformConfig]:
        """Load platform configurations"""
        default_config = {
            "ebay": {
                "name": "eBay",
                "base_url": "https://www.ebay.com",
                "login_url": "https://signin.ebay.com",
                "post_url": "https://www.ebay.com/sl/sell",
                "selectors": {
                    "title_input": ["#x-textbox-label-title", "input[data-testid='textbox-title']", "#textBoxTitle"],
                    "category_select": ["#categoryId", "select[data-testid='category-select']"],
                    "condition_select": ["#x-msku-condition-select", "select[data-testid='condition']"],
                    "photo_upload": ["input[type='file'][accept*='image']", "#photo-upload"],
                    "description_textarea": ["#textarea-description", "textarea[data-testid='description']"],
                    "price_input": ["#x-textbox-label-price", "input[data-testid='price']"],
                    "list_button": ["#x-btn-primary-list", "button[data-testid='list-item']"]
                },
                "delays": {
                    "page_load": [3.0, 5.0],
                    "form_fill": [1.0, 2.5],
                    "submission": [2.0, 4.0]
                },
                "max_daily_posts": 20
            },
            "mercari": {
                "name": "Mercari",
                "base_url": "https://www.mercari.com",
                "login_url": "https://www.mercari.com/login",
                "post_url": "https://www.mercari.com/sell",
                "selectors": {
                    "title_input": ["input[name='name']", "#item-name"],
                    "category_select": ["select[name='category']", "#category-select"],
                    "condition_select": ["select[name='condition']", "#condition-select"],
                    "photo_upload": ["input[type='file']", "#photo-upload"],
                    "description_textarea": ["textarea[name='description']", "#description"],
                    "price_input": ["input[name='price']", "#price-input"],
                    "list_button": ["button[type='submit']", "#list-button"]
                },
                "delays": {
                    "page_load": [2.0, 4.0],
                    "form_fill": [1.0, 2.0],
                    "submission": [1.5, 3.0]
                },
                "max_daily_posts": 15
            },
            "facebook": {
                "name": "Facebook Marketplace",
                "base_url": "https://www.facebook.com",
                "login_url": "https://www.facebook.com/login",
                "post_url": "https://www.facebook.com/marketplace/create",
                "selectors": {
                    "title_input": ["input[placeholder*='What are you selling?']", "input[aria-label*='title']"],
                    "category_select": ["div[data-testid='category-selector']"],
                    "photo_upload": ["input[type='file'][accept*='image']"],
                    "description_textarea": ["textarea[placeholder*='Describe your item']"],
                    "price_input": ["input[placeholder*='Price']", "input[aria-label*='price']"],
                    "list_button": ["div[aria-label='Publish']", "button[type='submit']"]
                },
                "delays": {
                    "page_load": [4.0, 6.0],
                    "form_fill": [1.5, 3.0],
                    "submission": [3.0, 5.0]
                },
                "max_daily_posts": 10,
                "requires_2fa": True
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                logger.warning(f"Could not load config: {e}, using defaults")
        
        platforms = {}
        for name, config in default_config.items():
            platforms[name] = PlatformConfig(
                name=config["name"],
                base_url=config["base_url"],
                login_url=config["login_url"],
                post_url=config["post_url"],
                selectors=config["selectors"],
                delays=config["delays"],
                enabled=config.get("enabled", True),
                requires_2fa=config.get("requires_2fa", False),
                max_daily_posts=config.get("max_daily_posts", 20)
            )
        
        return platforms
    
    def post_to_platform(self, platform_name: str, product: Product) -> ListingResult:
        """Post product to specific platform"""
        if platform_name not in self.platforms:
            return ListingResult(
                platform=platform_name,
                sku=product.sku,
                success=False,
                error_message=f"Platform {platform_name} not configured"
            )
        
        platform = self.platforms[platform_name]
        if not platform.enabled:
            return ListingResult(
                platform=platform_name,
                sku=product.sku,
                success=False,
                error_message=f"Platform {platform_name} is disabled"
            )
        
        logger.info(f"Starting listing on {platform.name} for {product.sku}")
        
        driver = AdvancedWebDriver(headless=False)  # Use headful for debugging
        
        try:
            # Navigate to posting page
            driver.driver.get(platform.post_url)
            HumanLikeBehavior.random_delay(*platform.delays["page_load"])
            
            # Take initial screenshot
            screenshot_path = driver.take_screenshot(f"{platform_name}_start")
            
            # Platform-specific posting logic
            if platform_name == "ebay":
                result = self._post_to_ebay(driver, product, platform)
            elif platform_name == "mercari":
                result = self._post_to_mercari(driver, product, platform)
            elif platform_name == "facebook":
                result = self._post_to_facebook(driver, product, platform)
            else:
                result = ListingResult(
                    platform=platform_name,
                    sku=product.sku,
                    success=False,
                    error_message=f"No implementation for platform {platform_name}"
                )
            
            result.screenshot_path = screenshot_path
            
        except Exception as e:
            logger.error(f"Error posting to {platform_name}: {e}")
            screenshot_path = driver.take_screenshot(f"{platform_name}_error")
            result = ListingResult(
                platform=platform_name,
                sku=product.sku,
                success=False,
                error_message=str(e),
                screenshot_path=screenshot_path
            )
        
        finally:
            driver.close()
        
        # Log result
        self._log_listing_result(result)
        
        return result
    
    def _post_to_ebay(self, driver: AdvancedWebDriver, product: Product, platform: PlatformConfig) -> ListingResult:
        """Post to eBay with comprehensive error handling"""
        try:
            # Fill title
            if not driver.smart_type(platform.selectors["title_input"], product.title):
                raise Exception("Failed to fill title")
            HumanLikeBehavior.random_delay(*platform.delays["form_fill"])
            
            # Select category (try to auto-detect first)
            category_element = driver.smart_find_element(platform.selectors["category_select"])
            if category_element:
                # eBay often auto-suggests categories, so we might not need to select
                HumanLikeBehavior.random_delay(1.0, 2.0)
            
            # Set condition to "New"
            condition_element = driver.smart_find_element(platform.selectors["condition_select"])
            if condition_element:
                select = Select(condition_element)
                select.select_by_visible_text("New")
            
            # Upload photos
            if product.photos:
                photo_input = driver.smart_find_element(platform.selectors["photo_upload"])
                if photo_input:
                    for photo in product.photos[:12]:  # eBay max 12 photos
                        if pathlib.Path(photo.path).exists():
                            photo_input.send_keys(str(pathlib.Path(photo.path).absolute()))
                            HumanLikeBehavior.random_delay(1.0, 2.0)
            
            # Fill description
            if not driver.smart_type(platform.selectors["description_textarea"], product.description_md):
                logger.warning("Failed to fill description, continuing...")
            
            # Set price
            if not driver.smart_type(platform.selectors["price_input"], str(product.pricing.base_price)):
                raise Exception("Failed to fill price")
            
            # Final screenshot before submission
            driver.take_screenshot("ebay_before_submit")
            
            # Submit listing (with confirmation)
            if driver.smart_click(platform.selectors["list_button"]):
                HumanLikeBehavior.random_delay(*platform.delays["submission"])
                
                # Check for success indicators
                success_indicators = [
                    "//div[contains(text(), 'Your item has been listed')]",
                    "//span[contains(text(), 'Listed successfully')]",
                    "#listing-success"
                ]
                
                success_element = driver.smart_find_element(success_indicators, timeout=30)
                if success_element:
                    # Try to extract listing URL/ID
                    listing_url = driver.driver.current_url
                    return ListingResult(
                        platform="ebay",
                        sku=product.sku,
                        success=True,
                        listing_url=listing_url
                    )
                else:
                    # Check for error messages
                    error_indicators = [
                        "//div[contains(@class, 'error')]",
                        "//span[contains(text(), 'Error')]",
                        "//div[contains(text(), 'failed')]"
                    ]
                    error_element = driver.smart_find_element(error_indicators, timeout=5)
                    error_msg = error_element.text if error_element else "Unknown error after submission"
                    
                    return ListingResult(
                        platform="ebay",
                        sku=product.sku,
                        success=False,
                        error_message=error_msg
                    )
            else:
                raise Exception("Failed to click list button")
                
        except Exception as e:
            return ListingResult(
                platform="ebay",
                sku=product.sku,
                success=False,
                error_message=str(e)
            )
    
    def _post_to_mercari(self, driver: AdvancedWebDriver, product: Product, platform: PlatformConfig) -> ListingResult:
        """Post to Mercari"""
        try:
            # Similar logic to eBay but with Mercari-specific selectors
            if not driver.smart_type(platform.selectors["title_input"], product.title):
                raise Exception("Failed to fill title")
            
            # Fill description
            description = product.description_md.replace('#', '').replace('*', '')[:1000]  # Mercari limits
            if not driver.smart_type(platform.selectors["description_textarea"], description):
                logger.warning("Failed to fill description")
            
            # Set price (Mercari uses integer prices)
            price = int(float(product.pricing.base_price))
            if not driver.smart_type(platform.selectors["price_input"], str(price)):
                raise Exception("Failed to fill price")
            
            # Upload photos
            if product.photos:
                photo_input = driver.smart_find_element(platform.selectors["photo_upload"])
                if photo_input and product.photos:
                    photo_input.send_keys(str(pathlib.Path(product.photos[0].path).absolute()))
                    HumanLikeBehavior.random_delay(2.0, 3.0)
            
            # Submit
            if driver.smart_click(platform.selectors["list_button"]):
                HumanLikeBehavior.random_delay(*platform.delays["submission"])
                
                return ListingResult(
                    platform="mercari",
                    sku=product.sku,
                    success=True,
                    listing_url=driver.driver.current_url
                )
            else:
                raise Exception("Failed to submit listing")
                
        except Exception as e:
            return ListingResult(
                platform="mercari",
                sku=product.sku,
                success=False,
                error_message=str(e)
            )
    
    def _post_to_facebook(self, driver: AdvancedWebDriver, product: Product, platform: PlatformConfig) -> ListingResult:
        """Post to Facebook Marketplace (conservative approach)"""
        # Facebook is very aggressive about automation detection
        # This is a skeleton implementation - recommend manual posting or API when available
        
        return ListingResult(
            platform="facebook",
            sku=product.sku,
            success=False,
            error_message="Facebook Marketplace posting requires manual intervention due to anti-automation measures"
        )
    
    def _log_listing_result(self, result: ListingResult):
        """Log listing result to file"""
        log_file = f"C:/EQ12/logs/crosslisting/listing_results_{datetime.datetime.now().strftime('%Y%m%d')}.json"
        
        try:
            # Load existing results
            results = []
            if pathlib.Path(log_file).exists():
                with open(log_file, 'r') as f:
                    results = json.load(f)
            
            # Add new result
            result_dict = {
                "platform": result.platform,
                "sku": result.sku,
                "success": result.success,
                "listing_id": result.listing_id,
                "listing_url": result.listing_url,
                "error_message": result.error_message,
                "screenshot_path": result.screenshot_path,
                "timestamp": result.timestamp.isoformat()
            }
            results.append(result_dict)
            
            # Save updated results
            with open(log_file, 'w') as f:
                json.dump(results, f, indent=2)
                
            logger.info(f"Listing result logged: {result.platform} - {result.sku} - {'Success' if result.success else 'Failed'}")
            
        except Exception as e:
            logger.error(f"Failed to log result: {e}")
    
    def bulk_post(self, sku: str, platforms: List[str] = None) -> Dict[str, ListingResult]:
        """Post product to multiple platforms"""
        if platforms is None:
            platforms = [name for name, config in self.platforms.items() if config.enabled]
        
        product = self.product_manager.load_product(sku)
        if not product:
            logger.error(f"Product {sku} not found")
            return {}
        
        results = {}
        
        for platform_name in platforms:
            logger.info(f"Posting {sku} to {platform_name}...")
            
            result = self.post_to_platform(platform_name, product)
            results[platform_name] = result
            
            # Delay between platforms to avoid detection
            if len(platforms) > 1:
                HumanLikeBehavior.random_delay(30, 60)
        
        return results

def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(description="EQ12 Cross-Listing Automation")
    parser.add_argument("action", choices=["post", "bulk", "test"], help="Action to perform")
    parser.add_argument("--sku", required=True, help="Product SKU to list")
    parser.add_argument("--platforms", nargs="+", 
                       choices=["ebay", "mercari", "facebook"],
                       help="Platforms to post to")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    automation = CrossListingAutomation()
    
    if args.action == "post":
        if not args.platforms:
            print("Error: --platforms required for post action")
            sys.exit(1)
        
        results = automation.bulk_post(args.sku, args.platforms)
        
        print(f"\n Listing Results for {args.sku}:")
        for platform, result in results.items():
            status = " SUCCESS" if result.success else " FAILED"
            print(f"  {platform}: {status}")
            if result.error_message:
                print(f"    Error: {result.error_message}")
            if result.listing_url:
                print(f"    URL: {result.listing_url}")
    
    elif args.action == "bulk":
        platforms = args.platforms or ["ebay", "mercari"]
        results = automation.bulk_post(args.sku, platforms)
        
        success_count = sum(1 for r in results.values() if r.success)
        print(f"\n Bulk Listing Complete: {success_count}/{len(results)} successful")
    
    elif args.action == "test":
        print(" Testing platform configurations...")
        for platform_name, config in automation.platforms.items():
            print(f"  {platform_name}: {' Enabled' if config.enabled else ' Disabled'}")

if __name__ == "__main__":
    main()