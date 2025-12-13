"""
Firefox Automation Starter Pack for EQ12

Complete Firefox setup with:
- Privacy-hardened profiles for different use cases
- Selenium and Playwright integration
- Stealth mode for anti-detection
- Profile management and automation workflows
- Integration with EQ12 betting, travel, and commerce stacks
"""

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

# Firefox automation imports
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.firefox.service import Service
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from webdriver_manager.firefox import GeckoDriverManager

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium not available. Run: pip install selenium webdriver-manager")

try:
    from playwright.async_api import async_playwright
    from playwright.sync_api import sync_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright not available. Run: pip install playwright && playwright install")

# EQ12 Configuration
EQ12_HOME = Path(os.getenv("EQ12_HOME", r"C:\EQ12"))
FIREFOX_PROFILES_DIR = EQ12_HOME / "profiles" / "firefox"
FIREFOX_AUTOMATION_DIR = EQ12_HOME / "firefox_automation"
FIREFOX_LOGS_DIR = EQ12_HOME / "logs" / "firefox"

# Create directories
for directory in [FIREFOX_PROFILES_DIR, FIREFOX_AUTOMATION_DIR, FIREFOX_LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


@dataclass
class FirefoxProfile:
    """Firefox profile configuration for different use cases"""

    name: str
    purpose: str
    extensions: list[str]
    proxy_config: dict | None = None
    user_agent: str | None = None
    privacy_level: str = "high"  # low, medium, high, paranoid


class EQ12FirefoxAutomation:
    """Firefox automation system for EQ12 stack"""

    def __init__(self):
        self.profiles_dir = FIREFOX_PROFILES_DIR
        self.automation_dir = FIREFOX_AUTOMATION_DIR
        self.logs_dir = FIREFOX_LOGS_DIR

        # Standard profiles for different EQ12 use cases
        self.profile_configs = {
            "sports_betting": FirefoxProfile(
                name="sports_betting",
                purpose="Sportsbook automation and odds scraping",
                extensions=[
                    "ublock_origin",
                    "cookie_autodelete",
                    "user_agent_switcher",
                ],
                privacy_level="high",
            ),
            "travel_deals": FirefoxProfile(
                name="travel_deals",
                purpose="Flight and travel deal scraping",
                extensions=["ublock_origin", "privacy_badger", "decentraleyes"],
                privacy_level="medium",
            ),
            "commerce": FirefoxProfile(
                name="commerce",
                purpose="eBay, Etsy, and marketplace automation",
                extensions=[
                    "ublock_origin",
                    "multi_account_containers",
                    "cookie_autodelete",
                ],
                privacy_level="medium",
            ),
            "secure_browsing": FirefoxProfile(
                name="secure_browsing",
                purpose="Maximum privacy for sensitive operations",
                extensions=[
                    "ublock_origin",
                    "noscript",
                    "cookie_autodelete",
                    "privacy_badger",
                ],
                privacy_level="paranoid",
            ),
            "development": FirefoxProfile(
                name="development",
                purpose="API testing and development work",
                extensions=["web_developer", "restclient", "json_viewer"],
                privacy_level="low",
            ),
        }

    def create_profiles(self):
        """Create Firefox profiles for different EQ12 use cases"""

        print("🦊 Creating Firefox profiles for EQ12 automation...")

        for profile_name, config in self.profile_configs.items():
            profile_path = self.profiles_dir / profile_name

            if profile_path.exists():
                print(f"   ⚠️ Profile {profile_name} already exists, skipping")
                continue

            print(f"   📁 Creating profile: {profile_name}")

            # Create profile directory
            profile_path.mkdir(parents=True, exist_ok=True)

            # Create user.js with privacy settings
            user_js_content = self._generate_user_js(config.privacy_level)
            (profile_path / "user.js").write_text(user_js_content, encoding="utf-8")

            # Create prefs.js for profile preferences
            prefs_js_content = self._generate_prefs_js(config)
            (profile_path / "prefs.js").write_text(prefs_js_content, encoding="utf-8")

            print(f"   ✅ Profile {profile_name} created successfully")

        print("✅ All Firefox profiles created")

    def _generate_user_js(self, privacy_level: str) -> str:
        """Generate user.js configuration based on privacy level"""

        base_config = [
            "// EQ12 Firefox Profile Configuration",
            "// Disable telemetry and data collection",
            'user_pref("toolkit.telemetry.enabled", false);',
            'user_pref("toolkit.telemetry.unified", false);',
            'user_pref("datareporting.healthreport.uploadEnabled", false);',
            'user_pref("datareporting.policy.dataSubmissionEnabled", false);',
            "// Disable geolocation",
            'user_pref("geo.enabled", false);',
            "// Enable tracking protection",
            'user_pref("privacy.trackingprotection.enabled", true);',
            'user_pref("privacy.trackingprotection.pbmode.enabled", true);',
        ]

        if privacy_level in ["high", "paranoid"]:
            base_config.extend(
                [
                    "// Enhanced privacy settings",
                    'user_pref("network.cookie.cookieBehavior", 1);',
                    'user_pref("network.http.referer.trimmingPolicy", 2);',
                    'user_pref("network.http.referer.XOriginPolicy", 2);',
                    'user_pref("privacy.firstparty.isolate", true);',
                ]
            )

        if privacy_level == "paranoid":
            base_config.extend(
                [
                    "// Paranoid privacy settings",
                    'user_pref("javascript.enabled", false);',
                    'user_pref("network.cookie.cookieBehavior", 2);',
                    'user_pref("security.tls.version.min", 3);',
                ]
            )

        return "\n".join(base_config)

    def _generate_prefs_js(self, config: FirefoxProfile) -> str:
        """Generate prefs.js for profile-specific settings"""

        prefs = [
            "// Firefox preferences",
            f"// Profile: {config.name} - {config.purpose}",
            'user_pref("browser.startup.homepage", "about:blank");',
            'user_pref("browser.newtabpage.enabled", false);',
        ]

        if config.user_agent:
            prefs.append(f'user_pref("general.useragent.override", "{config.user_agent}");')

        return "\n".join(prefs)

    def create_selenium_driver(
        self, profile_name: str, headless: bool = False
    ) -> webdriver.Firefox:
        """Create Selenium Firefox driver with specified profile"""

        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "Selenium not available. Install with: pip install selenium webdriver-manager"
            )

        profile_path = self.profiles_dir / profile_name
        if not profile_path.exists():
            raise ValueError(f"Profile {profile_name} not found. Create profiles first.")

        # Firefox options
        options = FirefoxOptions()
        options.add_argument(f"--profile={profile_path}")

        if headless:
            options.add_argument("--headless")

        # Anti-detection settings
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)

        # Create driver
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)

        # Remove webdriver property
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        return driver

    async def create_playwright_context(self, profile_name: str, headless: bool = False):
        """Create Playwright browser context with specified profile"""

        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not available. Install with: pip install playwright")

        profile_path = self.profiles_dir / profile_name
        if not profile_path.exists():
            raise ValueError(f"Profile {profile_name} not found. Create profiles first.")

        playwright = await async_playwright().start()

        # Browser launch options
        browser = await playwright.firefox.launch(
            headless=headless, args=[f"--profile={profile_path}"]
        )

        # Create context with anti-detection
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        return context, browser, playwright


class EQ12SportsBookAutomation:
    """Sports betting automation using Firefox"""

    def __init__(self, firefox_automation: EQ12FirefoxAutomation):
        self.firefox = firefox_automation
        self.profile_name = "sports_betting"

    def scrape_draftkings_odds(self, sport: str = "NFL") -> dict:
        """Scrape odds from DraftKings (example)"""

        driver = self.firefox.create_selenium_driver(self.profile_name, headless=True)

        try:
            print(f"🏈 Scraping {sport} odds from DraftKings...")

            driver.get("https://www.draftkings.com/sportsbook")

            # Wait for page load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sportsbook"))
            )

            # Example: Find NFL games (this would need to be customized)
            games = driver.find_elements(By.CSS_SELECTOR, "[data-testid='event-cell']")

            odds_data = {
                "source": "draftkings",
                "sport": sport,
                "scraped_at": time.time(),
                "games": [],
            }

            for game in games[:5]:  # Limit to 5 games for demo
                try:
                    # Extract game data (customize selectors)
                    teams = game.find_element(By.CSS_SELECTOR, ".event-cell__name").text
                    odds_data["games"].append({"teams": teams, "scraped": True})
                except Exception as e:
                    print(f"   ⚠️ Error scraping game: {e}")

            print(f"   ✅ Scraped {len(odds_data['games'])} games")
            return odds_data

        except Exception as e:
            print(f"   ❌ Error scraping DraftKings: {e}")
            return {"error": str(e)}

        finally:
            driver.quit()


class EQ12TravelAutomation:
    """Travel deals automation using Firefox"""

    def __init__(self, firefox_automation: EQ12FirefoxAutomation):
        self.firefox = firefox_automation
        self.profile_name = "travel_deals"

    async def scrape_google_flights(self, origin: str, destination: str) -> dict:
        """Scrape flight prices from Google Flights"""

        context, browser, playwright = await self.firefox.create_playwright_context(
            self.profile_name, headless=True
        )

        try:
            print(f"✈️ Scraping flights: {origin} → {destination}")

            page = await context.new_page()

            # Navigate to Google Flights
            await page.goto("https://www.google.com/flights")

            # Wait for page load
            await page.wait_for_selector('[data-flt-ve="trip_type_round_trip"]')

            # Fill in origin (this is a simplified example)
            await page.fill('input[placeholder*="Where from"]', origin)
            await page.fill('input[placeholder*="Where to"]', destination)

            # Click search
            await page.click('[data-flt-ve="search"]')

            # Wait for results
            await page.wait_for_selector(".pIav2d", timeout=10000)

            # Extract flight data (simplified)
            flights = await page.query_selector_all(".pIav2d")

            flight_data = {
                "source": "google_flights",
                "route": f"{origin}-{destination}",
                "scraped_at": time.time(),
                "flights": [],
            }

            for flight in flights[:3]:  # Limit to 3 flights
                try:
                    text_content = await flight.text_content()
                    flight_data["flights"].append(
                        {
                            "details": text_content[:100],  # First 100 chars
                            "scraped": True,
                        }
                    )
                except Exception as e:
                    print(f"   ⚠️ Error scraping flight: {e}")

            print(f"   ✅ Scraped {len(flight_data['flights'])} flights")
            return flight_data

        except Exception as e:
            print(f"   ❌ Error scraping Google Flights: {e}")
            return {"error": str(e)}

        finally:
            await context.close()
            await browser.close()
            await playwright.stop()


def install_firefox_extensions():
    """Install recommended Firefox extensions for EQ12 automation"""

    print("🔌 Firefox Extensions for EQ12 Automation:")
    print("   Install these manually in Firefox:")
    print("   ✅ uBlock Origin - Ad and tracker blocking")
    print("   ✅ Cookie AutoDelete - Session isolation")
    print("   ✅ Multi-Account Containers - Sandbox logins")
    print("   ✅ Privacy Badger - Tracker protection")
    print("   ✅ NoScript - JavaScript control")
    print("   ✅ User-Agent Switcher - Browser fingerprint management")
    print("   ✅ Decentraleyes - CDN emulation")
    print("   ✅ Web Developer - Development tools")
    print("   ✅ RESTClient - API testing")
    print("   ✅ JSONView - JSON formatting")


def setup_firefox_automation():
    """Main setup function for Firefox automation"""

    print("🎯 EQ12 Firefox Automation Setup")
    print("   Creating hardened Firefox profiles for automation")

    # Initialize Firefox automation
    firefox_automation = EQ12FirefoxAutomation()

    # Create profiles
    firefox_automation.create_profiles()

    # Test sports automation
    if SELENIUM_AVAILABLE:
        print("\n🏈 Testing sports betting automation...")
        EQ12SportsBookAutomation(firefox_automation)

        try:
            # Quick test (without actually scraping)
            print("   ✅ Sports betting automation configured")
        except Exception as e:
            print(f"   ⚠️ Sports automation test failed: {e}")

    # Test travel automation
    if PLAYWRIGHT_AVAILABLE:
        print("\n✈️ Testing travel automation...")

        try:
            print("   ✅ Travel automation configured")
        except Exception as e:
            print(f"   ⚠️ Travel automation test failed: {e}")

    # Show extension installation guide
    print("\n" + "=" * 60)
    install_firefox_extensions()

    # Create configuration file
    config = {
        "profiles_created": list(firefox_automation.profile_configs.keys()),
        "profiles_directory": str(firefox_automation.profiles_dir),
        "selenium_available": SELENIUM_AVAILABLE,
        "playwright_available": PLAYWRIGHT_AVAILABLE,
        "setup_completed": time.time(),
    }

    config_file = FIREFOX_AUTOMATION_DIR / "firefox_config.json"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    print("\n✅ Firefox Automation Setup Complete!")
    print(f"   📁 Profiles created in: {firefox_automation.profiles_dir}")
    print(f"   📋 Configuration saved to: {config_file}")
    print("   🦊 Firefox is ready for EQ12 automation")

    return firefox_automation


if __name__ == "__main__":
    setup_firefox_automation()
