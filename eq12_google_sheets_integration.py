#!/usr/bin/env python3
"""
EQ12 Google Sheets Integration - Advanced Sports Betting Automation
==================================================================

Professional integration combining:
1. EQ12 Enhanced OpenAI SDK for AI-powered betting analysis
2. The Odds API for real-time sports data
3. Google Sheets Apps Script for automated data visualization and tracking
4. Advanced betting workflows with spreadsheet-based analytics

This module provides Python-based Google Sheets integration to complement
the Apps Script functionality, enabling:
- Automated bet tracking and performance analytics
- Real-time odds monitoring with Google Sheets dashboards
- AI recommendations exported to collaborative spreadsheets
- Arbitrage opportunity tracking with visual alerts
- Multi-sport parlay analysis with spreadsheet calculators

Author: EQ12 Development Team
Date: October 5, 2025
Version: 1.0.0
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import gspread
    from google.oauth2.service_account import Credentials

    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    print("⚠️ Google Sheets integration requires: pip install gspread google-auth")
    GOOGLE_SHEETS_AVAILABLE = False

# EQ12 Integration
try:
    from eq12_enhanced_openai_sdk import EQ12EnhancedOpenAIClient
    from eq12_odds_api_client import (
        ArbitrageOpportunity,
        EQ12OddsAPIClient,
        GameEvent,
        Market,
        Region,
    )

    EQ12_INTEGRATION = True
except ImportError:
    print("⚠️ EQ12 modules not available - running in standalone mode")
    EQ12_INTEGRATION = False

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class EQ12GoogleSheetsIntegration:
    """Advanced Google Sheets integration for EQ12 betting platform"""

    def __init__(self, credentials_path: str | None = None):
        """Initialize Google Sheets integration"""
        self.credentials_path = credentials_path or "C:/EQ12/configs/google_sheets_credentials.json"
        self.sheets_client = None
        self.workbook = None

        # EQ12 clients
        self.odds_client = None
        self.ai_client = None

        if EQ12_INTEGRATION:
            try:
                self.odds_client = EQ12OddsAPIClient()
                self.ai_client = EQ12EnhancedOpenAIClient()
                logger.info("✅ EQ12 clients initialized")
            except Exception as e:
                logger.warning(f"⚠️ EQ12 client initialization failed: {e}")

        self._setup_google_sheets()

        # Data directories
        self.data_dir = Path("C:/EQ12/data/sheets_integration")
        self.templates_dir = Path("C:/EQ12/configs/sheets_templates")

        for dir_path in [self.data_dir, self.templates_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        logger.info("🏆 EQ12 Google Sheets Integration initialized")

    def _setup_google_sheets(self):
        """Setup Google Sheets authentication"""
        if not GOOGLE_SHEETS_AVAILABLE:
            logger.warning("⚠️ Google Sheets libraries not available")
            return

        try:
            if os.path.exists(self.credentials_path):
                # Use service account credentials
                scope = [
                    "https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/drive",
                ]
                creds = Credentials.from_service_account_file(self.credentials_path, scopes=scope)
                self.sheets_client = gspread.authorize(creds)
                logger.info("✅ Google Sheets authentication successful")
            else:
                logger.warning(f"⚠️ Credentials file not found: {self.credentials_path}")
                self._create_credentials_template()

        except Exception as e:
            logger.error(f"❌ Google Sheets setup failed: {e}")

    def _create_credentials_template(self):
        """Create template for Google Sheets credentials"""
        template = {
            "type": "service_account",
            "project_id": "your-project-id",
            "private_key_id": "your-private-key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n",
            "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
            "client_id": "your-client-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        }

        with open(self.credentials_path, "w") as f:
            json.dump(template, f, indent=2)

        logger.info(f"📝 Created credentials template: {self.credentials_path}")
        print(
            f"""
🔧 Google Sheets Setup Instructions:
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable Google Sheets API and Google Drive API
4. Create service account credentials
5. Download the JSON credentials file
6. Replace the template at: {self.credentials_path}
7. Share your Google Sheets with the service account email
"""
        )

    def create_betting_dashboard(
        self, spreadsheet_name: str = "EQ12 Sports Betting Dashboard"
    ) -> str | None:
        """Create comprehensive betting dashboard spreadsheet"""
        if not self.sheets_client:
            logger.error("❌ Google Sheets not available")
            return None

        try:
            # Create new spreadsheet
            spreadsheet = self.sheets_client.create(spreadsheet_name)
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"

            logger.info(f"📊 Created betting dashboard: {spreadsheet_url}")

            # Setup worksheets
            self._setup_dashboard_sheets(spreadsheet)

            return spreadsheet_url

        except Exception as e:
            logger.error(f"❌ Failed to create dashboard: {e}")
            return None

    def _setup_dashboard_sheets(self, spreadsheet):
        """Setup dashboard worksheet structure"""
        try:
            # Rename default sheet
            default_sheet = spreadsheet.sheet1
            default_sheet.update_title("Live Odds")

            # Add additional sheets
            sheets_to_create = [
                "Arbitrage Opportunities",
                "AI Recommendations",
                "Player Props",
                "Bet Tracking",
                "Performance Analytics",
                "Parlay Builder",
            ]

            for sheet_name in sheets_to_create:
                spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)

            # Setup headers for each sheet
            self._setup_live_odds_headers(default_sheet)
            self._setup_arbitrage_headers(spreadsheet.worksheet("Arbitrage Opportunities"))
            self._setup_ai_recommendations_headers(spreadsheet.worksheet("AI Recommendations"))
            self._setup_bet_tracking_headers(spreadsheet.worksheet("Bet Tracking"))
            self._setup_performance_headers(spreadsheet.worksheet("Performance Analytics"))

            logger.info("✅ Dashboard sheets configured")

        except Exception as e:
            logger.error(f"❌ Dashboard setup failed: {e}")

    def _setup_live_odds_headers(self, sheet):
        """Setup Live Odds sheet headers"""
        headers = [
            "Event ID",
            "Start Time",
            "Home Team",
            "Away Team",
            "Sport",
            "Bookmaker",
            "Market",
            "Outcome",
            "Odds",
            "Last Updated",
        ]
        sheet.insert_row(headers, 1)

    def _setup_arbitrage_headers(self, sheet):
        """Setup Arbitrage Opportunities sheet headers"""
        headers = [
            "Opportunity ID",
            "Game",
            "Market",
            "Profit %",
            "Total Stake",
            "Expected Return",
            "Bookmaker 1",
            "Odds 1",
            "Stake 1",
            "Bookmaker 2",
            "Odds 2",
            "Stake 2",
            "Status",
            "Detected At",
        ]
        sheet.insert_row(headers, 1)

    def _setup_ai_recommendations_headers(self, sheet):
        """Setup AI Recommendations sheet headers"""
        headers = [
            "Recommendation ID",
            "Game",
            "Market",
            "Recommended Bet",
            "Confidence %",
            "Expected Value",
            "Risk Level",
            "Optimal Stake",
            "AI Reasoning",
            "Generated At",
        ]
        sheet.insert_row(headers, 1)

    def _setup_bet_tracking_headers(self, sheet):
        """Setup Bet Tracking sheet headers"""
        headers = [
            "Bet ID",
            "Date",
            "Sport",
            "Game",
            "Market",
            "Selection",
            "Odds",
            "Stake",
            "Potential Return",
            "Result",
            "Actual Return",
            "Profit/Loss",
            "Notes",
        ]
        sheet.insert_row(headers, 1)

    def _setup_performance_headers(self, sheet):
        """Setup Performance Analytics sheet headers"""
        headers = [
            "Date",
            "Total Bets",
            "Winning Bets",
            "Win Rate %",
            "Total Staked",
            "Total Returned",
            "Net Profit",
            "ROI %",
            "Best Sport",
            "Worst Sport",
        ]
        sheet.insert_row(headers, 1)

    def update_live_odds(self, spreadsheet_url: str, sport: str = "upcoming"):
        """Update live odds in Google Sheets"""
        if not self.odds_client or not self.sheets_client:
            logger.error("❌ Required clients not available")
            return

        try:
            # Get spreadsheet
            spreadsheet = self.sheets_client.open_by_url(spreadsheet_url)
            live_odds_sheet = spreadsheet.worksheet("Live Odds")

            # Fetch latest odds
            events = self.odds_client.get_odds(
                sport=sport,
                markets=[Market.H2H, Market.SPREADS, Market.TOTALS],
                regions=[Region.US],
            )

            # Clear existing data (keep headers)
            live_odds_sheet.clear()
            self._setup_live_odds_headers(live_odds_sheet)

            # Prepare data rows
            rows_data = []
            for event in events:
                for bookmaker in event.bookmakers:
                    for market in bookmaker.markets:
                        for outcome in market.outcomes:
                            row = [
                                event.id,
                                event.commence_time.isoformat(),
                                event.home_team,
                                event.away_team,
                                event.sport_title,
                                bookmaker.title,
                                market.key,
                                outcome.name,
                                outcome.price,
                                bookmaker.last_update.isoformat(),
                            ]
                            rows_data.append(row)

            # Update spreadsheet
            if rows_data:
                live_odds_sheet.insert_rows(rows_data, 2)
                logger.info(f"✅ Updated {len(rows_data)} odds entries")

        except Exception as e:
            logger.error(f"❌ Failed to update live odds: {e}")

    def update_arbitrage_opportunities(self, spreadsheet_url: str):
        """Update arbitrage opportunities in Google Sheets"""
        if not self.odds_client or not self.sheets_client:
            logger.error("❌ Required clients not available")
            return

        try:
            spreadsheet = self.sheets_client.open_by_url(spreadsheet_url)
            arb_sheet = spreadsheet.worksheet("Arbitrage Opportunities")

            # Get upcoming events
            events = self.odds_client.get_odds(
                sport="upcoming", markets=[Market.H2H, Market.SPREADS, Market.TOTALS]
            )

            # Find arbitrage opportunities
            arb_ops = self.odds_client.find_arbitrage_opportunities(events, min_profit=0.01)

            # Clear and update
            arb_sheet.clear()
            self._setup_arbitrage_headers(arb_sheet)

            rows_data = []
            for i, opp in enumerate(arb_ops):
                # Get best bookmakers for each outcome
                bookmakers = list(opp.bookmakers.keys())
                stakes = list(opp.stakes.values())

                row = [
                    f"ARB_{i + 1}",
                    f"{opp.event.away_team} @ {opp.event.home_team}",
                    opp.market.upper(),
                    round(opp.profit_percentage, 2),
                    round(opp.total_stake, 2),
                    round(opp.expected_return, 2),
                    bookmakers[0] if len(bookmakers) > 0 else "N/A",
                    "N/A",  # Would need to extract from opp data
                    round(stakes[0], 2) if len(stakes) > 0 else 0,
                    bookmakers[1] if len(bookmakers) > 1 else "N/A",
                    "N/A",  # Would need to extract from opp data
                    round(stakes[1], 2) if len(stakes) > 1 else 0,
                    "Active",
                    datetime.now().isoformat(),
                ]
                rows_data.append(row)

            if rows_data:
                arb_sheet.insert_rows(rows_data, 2)
                logger.info(f"✅ Updated {len(rows_data)} arbitrage opportunities")
            else:
                arb_sheet.insert_row(["No arbitrage opportunities found"], 2)

        except Exception as e:
            logger.error(f"❌ Failed to update arbitrage opportunities: {e}")

    async def update_ai_recommendations(self, spreadsheet_url: str):
        """Update AI recommendations in Google Sheets"""
        if not self.ai_client or not self.odds_client or not self.sheets_client:
            logger.error("❌ Required clients not available")
            return

        try:
            spreadsheet = self.sheets_client.open_by_url(spreadsheet_url)
            ai_sheet = spreadsheet.worksheet("AI Recommendations")

            # Get events for AI analysis
            events = self.odds_client.get_odds(
                sport="upcoming", markets=[Market.H2H, Market.SPREADS, Market.TOTALS]
            )[
                :5
            ]  # Limit for API quota

            # Get AI recommendations
            recommendations = await self.odds_client.get_ai_betting_recommendations(events)

            # Clear and update
            ai_sheet.clear()
            self._setup_ai_recommendations_headers(ai_sheet)

            rows_data = []
            for i, rec in enumerate(recommendations):
                row = [
                    f"AI_{i + 1}",
                    f"{rec.event.away_team} @ {rec.event.home_team}",
                    rec.market.upper(),
                    rec.recommended_bet,
                    round(rec.confidence * 100, 1),
                    round(rec.expected_value, 3),
                    rec.risk_assessment,
                    round(rec.optimal_stake, 2),
                    rec.reasoning[:100] + "..." if len(rec.reasoning) > 100 else rec.reasoning,
                    datetime.now().isoformat(),
                ]
                rows_data.append(row)

            if rows_data:
                ai_sheet.insert_rows(rows_data, 2)
                logger.info(f"✅ Updated {len(rows_data)} AI recommendations")

        except Exception as e:
            logger.error(f"❌ Failed to update AI recommendations: {e}")

    def add_bet_tracking_entry(self, spreadsheet_url: str, bet_data: dict[str, Any]):
        """Add new bet to tracking sheet"""
        if not self.sheets_client:
            logger.error("❌ Google Sheets not available")
            return

        try:
            spreadsheet = self.sheets_client.open_by_url(spreadsheet_url)
            tracking_sheet = spreadsheet.worksheet("Bet Tracking")

            # Prepare bet row
            bet_row = [
                bet_data.get("bet_id", f"BET_{int(time.time())}"),
                bet_data.get("date", datetime.now().strftime("%Y-%m-%d")),
                bet_data.get("sport", "Unknown"),
                bet_data.get("game", "Unknown"),
                bet_data.get("market", "Unknown"),
                bet_data.get("selection", "Unknown"),
                bet_data.get("odds", 0),
                bet_data.get("stake", 0),
                bet_data.get("potential_return", 0),
                bet_data.get("result", "Pending"),
                bet_data.get("actual_return", 0),
                bet_data.get("profit_loss", 0),
                bet_data.get("notes", ""),
            ]

            tracking_sheet.append_row(bet_row)
            logger.info(f"✅ Added bet tracking entry: {bet_data.get('bet_id')}")

        except Exception as e:
            logger.error(f"❌ Failed to add bet tracking entry: {e}")

    def generate_performance_report(self, spreadsheet_url: str):
        """Generate performance analytics report"""
        if not self.sheets_client:
            logger.error("❌ Google Sheets not available")
            return

        try:
            spreadsheet = self.sheets_client.open_by_url(spreadsheet_url)
            tracking_sheet = spreadsheet.worksheet("Bet Tracking")
            performance_sheet = spreadsheet.worksheet("Performance Analytics")

            # Get all bet data (skip header row)
            bet_data = tracking_sheet.get_all_values()[1:]

            if not bet_data:
                logger.info("ℹ️ No bet data available for performance report")
                return

            # Calculate performance metrics
            total_bets = len(bet_data)
            winning_bets = sum(1 for bet in bet_data if bet[9] == "Win")
            win_rate = (winning_bets / total_bets) * 100 if total_bets > 0 else 0

            total_staked = sum(
                float(bet[7]) for bet in bet_data if bet[7].replace(".", "").isdigit()
            )
            total_returned = sum(
                float(bet[10]) for bet in bet_data if bet[10].replace(".", "").isdigit()
            )
            net_profit = total_returned - total_staked
            roi = (net_profit / total_staked) * 100 if total_staked > 0 else 0

            # Sport analysis
            sports_data = {}
            for bet in bet_data:
                sport = bet[2]
                if sport not in sports_data:
                    sports_data[sport] = {"bets": 0, "wins": 0, "profit": 0}
                sports_data[sport]["bets"] += 1
                if bet[9] == "Win":
                    sports_data[sport]["wins"] += 1
                if bet[11].replace(".", "").replace("-", "").isdigit():
                    sports_data[sport]["profit"] += float(bet[11])

            best_sport = (
                max(sports_data.items(), key=lambda x: x[1]["profit"])[0] if sports_data else "N/A"
            )
            worst_sport = (
                min(sports_data.items(), key=lambda x: x[1]["profit"])[0] if sports_data else "N/A"
            )

            # Update performance sheet
            performance_row = [
                datetime.now().strftime("%Y-%m-%d"),
                total_bets,
                winning_bets,
                round(win_rate, 2),
                round(total_staked, 2),
                round(total_returned, 2),
                round(net_profit, 2),
                round(roi, 2),
                best_sport,
                worst_sport,
            ]

            # Clear and add headers if empty
            if len(performance_sheet.get_all_values()) <= 1:
                performance_sheet.clear()
                self._setup_performance_headers(performance_sheet)

            performance_sheet.append_row(performance_row)
            logger.info("✅ Performance report updated")

        except Exception as e:
            logger.error(f"❌ Failed to generate performance report: {e}")

    def create_apps_script_integration(self, spreadsheet_url: str):
        """Generate Apps Script code for the spreadsheet"""
        apps_script_code = self._generate_apps_script_code()

        # Save to file
        apps_script_file = self.data_dir / "eq12_betting_apps_script.gs"
        with open(apps_script_file, "w") as f:
            f.write(apps_script_code)

        logger.info(f"📝 Apps Script code saved: {apps_script_file}")
        print(
            f"""
🔧 Apps Script Integration Instructions:
1. Open your spreadsheet: {spreadsheet_url}
2. Go to Extensions → Apps Script
3. Copy the code from: {apps_script_file}
4. Set up triggers for automatic updates:
   - Manual: Create button triggers
   - Automatic: Set time-driven triggers (every 5-15 minutes)
5. Configure API keys in the script
"""
        )

    def _generate_apps_script_code(self) -> str:
        """Generate comprehensive Apps Script code"""
        return """
function updateEQ12Dashboard() {
  /**
   * EQ12 Sports Betting Dashboard - Automated Updates
   * Integrates with The Odds API for real-time data
   */

  // Configuration
  const API_KEY = 'YOUR_ODDS_API_KEY' // Set your Odds API key
  const SPORT = 'upcoming' // Or specific sport like 'americanfootball_nfl'
  const MARKETS = 'h2h,spreads,totals'
  const REGIONS = 'us'
  const ODDS_FORMAT = 'american'

  try {
    // Update Live Odds
    updateLiveOdds(API_KEY, SPORT, MARKETS, REGIONS, ODDS_FORMAT)

    // Update Arbitrage Scan
    updateArbitrageOpportunities(API_KEY, SPORT, MARKETS, REGIONS, ODDS_FORMAT)

    Logger.log('EQ12 Dashboard updated successfully')

  } catch (error) {
    Logger.log('EQ12 Dashboard update failed: ' + error.toString())
  }
}

function updateLiveOdds(apiKey, sport, markets, regions, oddsFormat) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Live Odds')

  // Clear existing data (keep headers)
  if (sheet.getLastRow() > 1) {
    sheet.deleteRows(2, sheet.getLastRow() - 1)
  }

  // Fetch odds data
  const url = `https://api.the-odds-api.com/v4/sports/${sport}/odds?apiKey=${apiKey}&regions=${regions}&markets=${markets}&oddsFormat=${oddsFormat}`
  const response = UrlFetchApp.fetch(url)
  const data = JSON.parse(response.getContentText())

  // Process and insert data
  const rows = []
  data.forEach(event => {
    event.bookmakers.forEach(bookmaker => {
      bookmaker.markets.forEach(market => {
        market.outcomes.forEach(outcome => {
          rows.push([
            event.id,
            event.commence_time,
            event.home_team,
            event.away_team,
            event.sport_title,
            bookmaker.title,
            market.key,
            outcome.name,
            outcome.price,
            bookmaker.last_update
          ])
        })
      })
    })
  })

  if (rows.length > 0) {
    sheet.getRange(2, 1, rows.length, 10).setValues(rows)
  }
}

function updateArbitrageOpportunities(apiKey, sport, markets, regions, oddsFormat) {
  // Simplified arbitrage detection for Apps Script
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Arbitrage Opportunities')

  // This would need more complex logic for full arbitrage detection
  // For now, just add a timestamp showing last scan
  const timestamp = new Date().toISOString()
  sheet.getRange('A2').setValue('Last scan: ' + timestamp)
}

// Trigger functions
function onEdit(e) {
  // Optional: Add custom logic when cells are edited
}

function onOpen() {
  // Add custom menu
  const ui = SpreadsheetApp.getUi()
  ui.createMenu('EQ12 Betting')
    .addItem('Update Dashboard', 'updateEQ12Dashboard')
    .addItem('Refresh Odds', 'updateLiveOdds')
    .addToUi()
}
"""


async def demo_sheets_integration():
    """Demonstrate EQ12 Google Sheets integration"""
    print("🚀 EQ12 Google Sheets Integration Demo")
    print("=" * 50)

    try:
        # Initialize integration
        sheets_integration = EQ12GoogleSheetsIntegration()

        if not sheets_integration.sheets_client:
            print("ℹ️ Google Sheets not configured - showing setup instructions")
            return

        # Create dashboard
        print("📊 Creating betting dashboard...")
        dashboard_url = sheets_integration.create_betting_dashboard("EQ12 Betting Demo")

        if dashboard_url:
            print(f"✅ Dashboard created: {dashboard_url}")

            # Update with live data
            print("🔄 Updating live odds...")
            sheets_integration.update_live_odds(dashboard_url)

            print("🔍 Scanning arbitrage opportunities...")
            sheets_integration.update_arbitrage_opportunities(dashboard_url)

            if sheets_integration.ai_client:
                print("🤖 Generating AI recommendations...")
                await sheets_integration.update_ai_recommendations(dashboard_url)

            # Add sample bet
            print("📝 Adding sample bet tracking...")
            sample_bet = {
                "sport": "NFL",
                "game": "Bills @ Chiefs",
                "market": "Moneyline",
                "selection": "Bills +165",
                "odds": 165,
                "stake": 100,
                "potential_return": 265,
                "notes": "Demo bet entry",
            }
            sheets_integration.add_bet_tracking_entry(dashboard_url, sample_bet)

            # Generate performance report
            print("📈 Generating performance report...")
            sheets_integration.generate_performance_report(dashboard_url)

            # Create Apps Script integration
            print("🔧 Generating Apps Script integration...")
            sheets_integration.create_apps_script_integration(dashboard_url)

            print("✅ Demo completed successfully!")
            print(f"🔗 Your dashboard: {dashboard_url}")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    import asyncio

    asyncio.run(demo_sheets_integration())
