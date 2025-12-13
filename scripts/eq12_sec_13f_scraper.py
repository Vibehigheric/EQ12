"""
EQ12 SEC 13F Hedge Fund Scraper
Tracks Citadel and other major hedge funds' holdings via SEC EDGAR API

Author: EQ12 System
Created: 2025-11-27
License: MIT
"""

import json
import sqlite3
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import requests
import time
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# SEC EDGAR API Configuration
SEC_BASE_URL = "https://data.sec.gov"
USER_AGENT = "EQ12Bot/1.0 (ricoj100@gmail.com)"  # SEC requires user agent with contact

# Major hedge funds to track (CIK numbers)
HEDGE_FUNDS = {
    "Citadel Advisors LLC": "0001423053",
    "Bridgewater Associates": "0001350694",
    "Renaissance Technologies": "0001037389",
    "Two Sigma Investments": "0001448206",
    "Millennium Management": "0001040273",
    "Point72 Asset Management": "0001603466",
    "Elliott Management": "0001067983",
    "DE Shaw & Co": "0001009207",
    "Viking Global Investors": "0001103804",
    "Tiger Global Management": "0001167483"
}

class SEC13FScraper:
    """Scraper for SEC 13F filings (hedge fund holdings)"""
    
    def __init__(self, db_path: str = None):
        """
        Initialize scraper
        
        Args:
            db_path: Path to SQLite database (default: ../logs/sec_13f_holdings.db)
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent / "logs" / "sec_13f_holdings.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "application/json"
        })
        
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Filings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS filings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_name TEXT NOT NULL,
                cik TEXT NOT NULL,
                filing_date DATE NOT NULL,
                period_end DATE NOT NULL,
                accession_number TEXT UNIQUE NOT NULL,
                form_type TEXT NOT NULL,
                file_number TEXT,
                total_value REAL,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(cik, accession_number)
            )
        """)
        
        # Holdings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filing_id INTEGER NOT NULL,
                cusip TEXT NOT NULL,
                issuer_name TEXT NOT NULL,
                ticker TEXT,
                shares BIGINT,
                market_value REAL,
                percentage REAL,
                position_type TEXT,
                FOREIGN KEY (filing_id) REFERENCES filings(id),
                UNIQUE(filing_id, cusip)
            )
        """)
        
        # Position changes table (quarter-over-quarter)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS position_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_name TEXT NOT NULL,
                cusip TEXT NOT NULL,
                issuer_name TEXT NOT NULL,
                ticker TEXT,
                prev_shares BIGINT,
                new_shares BIGINT,
                shares_change BIGINT,
                shares_pct_change REAL,
                prev_value REAL,
                new_value REAL,
                value_change REAL,
                change_type TEXT,
                prev_filing_date DATE,
                new_filing_date DATE,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_filings_cik ON filings(cik)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_filings_date ON filings(filing_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_holdings_ticker ON holdings(ticker)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_changes_ticker ON position_changes(ticker)")
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {self.db_path}")
    
    def fetch_fund_filings(self, cik: str, fund_name: str, max_filings: int = 10) -> List[Dict]:
        """
        Fetch 13F filings for a specific fund
        
        Args:
            cik: Central Index Key (SEC identifier)
            fund_name: Name of hedge fund
            max_filings: Maximum number of filings to retrieve
            
        Returns:
            List of filing metadata dictionaries
        """
        url = f"{SEC_BASE_URL}/submissions/CIK{cik}.json"
        
        try:
            logger.info(f"Fetching filings for {fund_name} (CIK: {cik})...")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract recent 13F filings
            filings = []
            recent = data.get("filings", {}).get("recent", {})
            
            for i in range(len(recent.get("accessionNumber", []))):
                form_type = recent["form"][i]
                
                # Only 13F-HR forms (holdings reports)
                if form_type == "13F-HR":
                    filing = {
                        "fund_name": fund_name,
                        "cik": cik,
                        "accession_number": recent["accessionNumber"][i],
                        "filing_date": recent["filingDate"][i],
                        "form_type": form_type,
                        "file_number": recent.get("fileNumber", [None])[i],
                        "primary_document": recent.get("primaryDocument", [None])[i]
                    }
                    filings.append(filing)
                    
                    if len(filings) >= max_filings:
                        break
            
            logger.info(f"Found {len(filings)} 13F-HR filings for {fund_name}")
            return filings
            
        except Exception as e:
            logger.error(f"Error fetching filings for {fund_name}: {e}")
            return []
    
    def parse_13f_filing(self, accession_number: str) -> Optional[Dict]:
        """
        Parse 13F filing to extract holdings
        
        Args:
            accession_number: SEC accession number (with dashes removed)
            
        Returns:
            Dictionary with holdings data
        """
        # Remove dashes from accession number for URL
        acc_no_dashes = accession_number.replace("-", "")
        
        # 13F information table URL
        url = f"{SEC_BASE_URL}/Archives/edgar/data/{acc_no_dashes.split('-')[0]}/{acc_no_dashes}/{accession_number}.txt"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # TODO: Parse XML/SGML 13F information table
            # This is simplified - real implementation needs XML parsing
            logger.warning("13F parsing not fully implemented - placeholder")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing 13F filing {accession_number}: {e}")
            return None
    
    def save_filing(self, filing: Dict) -> int:
        """
        Save filing metadata to database
        
        Args:
            filing: Filing metadata dictionary
            
        Returns:
            Filing ID from database
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO filings 
                (fund_name, cik, filing_date, period_end, accession_number, form_type, file_number)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                filing["fund_name"],
                filing["cik"],
                filing["filing_date"],
                filing.get("period_end", filing["filing_date"]),  # Use filing date if period_end missing
                filing["accession_number"],
                filing["form_type"],
                filing.get("file_number")
            ))
            
            conn.commit()
            filing_id = cursor.lastrowid
            
            logger.info(f"Saved filing {filing['accession_number']} for {filing['fund_name']}")
            return filing_id
            
        except sqlite3.IntegrityError:
            # Filing already exists
            cursor.execute(
                "SELECT id FROM filings WHERE accession_number = ?",
                (filing["accession_number"],)
            )
            filing_id = cursor.fetchone()[0]
            logger.debug(f"Filing {filing['accession_number']} already exists (ID: {filing_id})")
            return filing_id
            
        finally:
            conn.close()
    
    def scrape_all_funds(self, max_filings_per_fund: int = 5):
        """
        Scrape 13F filings for all tracked hedge funds
        
        Args:
            max_filings_per_fund: Maximum filings to retrieve per fund
        """
        logger.info(f"Starting scrape for {len(HEDGE_FUNDS)} hedge funds...")
        
        for fund_name, cik in HEDGE_FUNDS.items():
            filings = self.fetch_fund_filings(cik, fund_name, max_filings_per_fund)
            
            for filing in filings:
                self.save_filing(filing)
            
            # Be respectful to SEC servers
            time.sleep(0.5)
        
        logger.info("Scrape complete!")
    
    def get_latest_filings(self, limit: int = 20) -> List[Dict]:
        """
        Get most recent filings across all funds
        
        Args:
            limit: Maximum number of filings to return
            
        Returns:
            List of filing dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM filings 
            ORDER BY filing_date DESC 
            LIMIT ?
        """, (limit,))
        
        filings = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return filings
    
    def export_to_json(self, output_path: str = None):
        """
        Export all filings to JSON
        
        Args:
            output_path: Output file path (default: ../reports/sec_13f_export.json)
        """
        if output_path is None:
            output_path = Path(__file__).parent.parent / "reports" / "sec_13f_export.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        filings = self.get_latest_filings(limit=1000)
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_filings": len(filings),
            "filings": filings
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"Exported {len(filings)} filings to {output_path}")
        return output_path


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description="EQ12 SEC 13F Hedge Fund Scraper - Track Citadel and major funds"
    )
    parser.add_argument(
        "--scrape",
        action="store_true",
        help="Scrape latest 13F filings for all tracked funds"
    )
    parser.add_argument(
        "--max-filings",
        type=int,
        default=5,
        help="Maximum filings to retrieve per fund (default: 5)"
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export filings to JSON"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List recent filings"
    )
    parser.add_argument(
        "--db",
        type=str,
        help="Custom database path"
    )
    
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = SEC13FScraper(db_path=args.db)
    
    if args.scrape:
        scraper.scrape_all_funds(max_filings_per_fund=args.max_filings)
    
    if args.export:
        scraper.export_to_json()
    
    if args.list:
        filings = scraper.get_latest_filings(limit=20)
        print("\n=== Latest 13F Filings ===\n")
        for f in filings:
            print(f"{f['filing_date']} | {f['fund_name']:<30} | {f['accession_number']}")
    
    if not any([args.scrape, args.export, args.list]):
        parser.print_help()


if __name__ == "__main__":
    main()
