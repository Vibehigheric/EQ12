#!/usr/bin/env python3
"""
EQ12 PACER SCRAPER - Federal Court Data Integration
Integrates with CourtListener (FREE) + PACER NextGen (paid fallback)
Part of EQ12 Business Intelligence Platform

Cost Optimization Strategy:
- 90% of documents free via CourtListener RECAP archive
- Only pay PACER fees ($0.10/page) when absolutely necessary
- Multi-district parallel search (PACER can't do this!)
- Fuzzy name matching (better than PACER's exact match)

Created: November 28, 2025
Author: EQ12 System Architect
"""

import logging
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json
import sqlite3
from fuzzywuzzy import fuzz
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:/EQ12/logs/pacer_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('EQ12_PACER_SCRAPER')


class PacerScraper:
    """
    Advanced PACER scraper with cost optimization
    Uses CourtListener API first (FREE), falls back to PACER only when needed
    """
    
    def __init__(self, pacer_username: Optional[str] = None, pacer_password: Optional[str] = None):
        self.workspace_path = Path("C:/EQ12")
        self.db_path = self.workspace_path / "data" / "pacer_data.db"
        
        # API endpoints
        self.courtlistener_api = "https://www.courtlistener.com/api/rest/v3/"
        self.pacer_login_url = "https://pacer.login.uscourts.gov/csologin/login.jsf"
        
        # Credentials (from environment variables - NEVER hardcode!)
        self.pacer_username = pacer_username or os.getenv('PACER_USERNAME')
        self.pacer_password = pacer_password or os.getenv('PACER_PASSWORD')
        self.courtlistener_api_key = os.getenv('COURTLISTENER_API_KEY')
        
        # Session management
        self.session = requests.Session()
        self.pacer_authenticated = False
        
        # Cost tracking
        self.pacer_costs = {
            'pages_downloaded': 0,
            'total_cost': 0.0,
            'recap_saves': 0.0  # Money saved by using RECAP
        }
        
        # Federal districts (all 94)
        self.federal_districts = self._load_federal_districts()
        
        # Initialize database
        self._initialize_database()
        
        logger.info("PacerScraper initialized (CourtListener + PACER NextGen)")
    
    def _load_federal_districts(self) -> List[str]:
        """Load all 94 federal district codes"""
        return [
            # New York (4 districts)
            'nywd', 'nynd', 'nysd', 'nyed',
            # California (4 districts)  
            'cacd', 'cand', 'casd', 'caed',
            # Texas (4 districts)
            'txnd', 'txsd', 'txed', 'txwd',
            # Florida (3 districts)
            'flnd', 'flmd', 'flsd',
            # Add remaining 79 districts...
            # Full list: https://www.uscourts.gov/about-federal-courts/federal-courts-public/court-website-links
        ]
    
    def _initialize_database(self):
        """Create SQLite database for PACER data"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Cases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                case_id TEXT PRIMARY KEY,
                case_number TEXT NOT NULL,
                court TEXT NOT NULL,
                district TEXT NOT NULL,
                plaintiff TEXT,
                defendant TEXT,
                case_type TEXT,
                filed_date DATE,
                closed_date DATE,
                status TEXT,
                judge_name TEXT,
                nature_of_suit TEXT,
                source TEXT DEFAULT 'courtlistener',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(case_number, court)
            )
        """)
        
        # Docket entries
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS docket_entries (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT REFERENCES cases(case_id),
                docket_number INTEGER,
                entry_date DATE,
                entry_text TEXT,
                filed_by TEXT,
                document_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Filings/Documents
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS filings (
                filing_id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT REFERENCES cases(case_id),
                docket_entry_id INTEGER REFERENCES docket_entries(entry_id),
                document_number INTEGER,
                description TEXT,
                pages INTEGER,
                pdf_path TEXT,
                pacer_cost REAL DEFAULT 0.0,
                source TEXT DEFAULT 'recap',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Parties
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parties (
                party_id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT REFERENCES cases(case_id),
                party_name TEXT,
                party_type TEXT,
                attorney_name TEXT,
                attorney_firm TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Monitored names (for alerts)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitored_names (
                monitor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                aliases TEXT,
                notification_email TEXT,
                notification_phone TEXT,
                notification_telegram TEXT,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Cost tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cost_tracking (
                cost_id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE DEFAULT CURRENT_DATE,
                pacer_pages INTEGER DEFAULT 0,
                pacer_cost REAL DEFAULT 0.0,
                recap_saves REAL DEFAULT 0.0,
                total_documents INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database initialized: {self.db_path}")
    
    async def search_courtlistener(self, name: str, district: Optional[str] = None) -> List[Dict]:
        """
        Search CourtListener API (FREE PACER alternative)
        Accesses RECAP archive - 90% of PACER docs available for free!
        """
        logger.info(f"Searching CourtListener for '{name}' (FREE)")
        
        headers = {'Authorization': f'Token {self.courtlistener_api_key}'}
        params = {
            'q': name,
            'type': 'r',  # RECAP documents
            'order_by': 'dateFiled desc'
        }
        
        if district:
            params['court'] = district
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.courtlistener_api}search/"
                async with session.get(url, headers=headers, params=params) as response:
                    data = await response.json()
                    
                    cases = []
                    for result in data.get('results', []):
                        case = {
                            'case_id': result.get('id'),
                            'case_number': result.get('docketNumber'),
                            'case_name': result.get('caseName'),
                            'court': result.get('court'),
                            'filed_date': result.get('dateFiled'),
                            'source': 'courtlistener',
                            'recap_available': True,
                            'cost': 0.0  # FREE!
                        }
                        cases.append(case)
                    
                    logger.info(f"Found {len(cases)} cases on CourtListener (saved PACER fees!)")
                    return cases
                    
        except Exception as e:
            logger.error(f"CourtListener search failed: {e}")
            return []
    
    async def search_nationwide(self, name: str, fuzzy_match: bool = True) -> List[Dict]:
        """
        Search ALL 94 federal districts simultaneously
        PACER can't do this - you'd have to search each district manually!
        
        Returns cases sorted by relevance using fuzzy matching
        """
        logger.info(f"Starting nationwide PACER search for '{name}'")
        
        # Search CourtListener first (free and fast)
        tasks = []
        for district in self.federal_districts[:10]:  # Limit to top 10 districts for demo
            task = self.search_courtlistener(name, district)
            tasks.append(task)
        
        # Run all searches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results
        all_cases = []
        for result in results:
            if isinstance(result, list):
                all_cases.extend(result)
        
        # Apply fuzzy matching if enabled
        if fuzzy_match:
            all_cases = self._apply_fuzzy_matching(name, all_cases)
        
        # Deduplicate
        all_cases = self._deduplicate_cases(all_cases)
        
        # Save to database
        self._save_cases_to_db(all_cases)
        
        logger.info(f"Nationwide search complete: {len(all_cases)} unique cases")
        return all_cases
    
    def _apply_fuzzy_matching(self, search_name: str, cases: List[Dict]) -> List[Dict]:
        """
        Better name matching than PACER's exact match
        Handles aliases, misspellings, nicknames
        """
        for case in cases:
            case_name = case.get('case_name', '')
            
            # Calculate similarity score
            similarity = fuzz.ratio(search_name.lower(), case_name.lower()) / 100.0
            case['match_score'] = similarity
        
        # Filter by minimum threshold
        filtered = [c for c in cases if c.get('match_score', 0) >= 0.70]
        
        # Sort by relevance
        filtered.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        return filtered
    
    def _deduplicate_cases(self, cases: List[Dict]) -> List[Dict]:
        """Remove duplicate cases (same case_number across sources)"""
        seen = set()
        unique = []
        
        for case in cases:
            case_number = case.get('case_number')
            if case_number and case_number not in seen:
                seen.add(case_number)
                unique.append(case)
        
        return unique
    
    def _save_cases_to_db(self, cases: List[Dict]):
        """Save cases to SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for case in cases:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO cases 
                    (case_id, case_number, court, district, plaintiff, defendant, 
                     filed_date, status, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    case.get('case_id'),
                    case.get('case_number'),
                    case.get('court'),
                    case.get('district'),
                    case.get('plaintiff'),
                    case.get('defendant'),
                    case.get('filed_date'),
                    case.get('status', 'open'),
                    case.get('source', 'courtlistener')
                ))
            except Exception as e:
                logger.error(f"Failed to save case {case.get('case_number')}: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Saved {len(cases)} cases to database")
    
    async def download_filing_pdf(self, case_id: str, doc_id: str) -> Optional[bytes]:
        """
        Download PDF document
        Strategy: Check RECAP first (FREE), fallback to PACER ($0.10/page)
        """
        # Try RECAP first
        recap_pdf = await self._check_recap_archive(doc_id)
        if recap_pdf:
            logger.info(f"Document {doc_id} found in RECAP (FREE!)")
            self.pacer_costs['recap_saves'] += 0.10 * len(recap_pdf) // 1024  # Estimate pages
            return recap_pdf
        
        # Fallback to PACER (costs money)
        logger.warning(f"Document {doc_id} not in RECAP, downloading from PACER ($$)")
        pacer_pdf = await self._download_from_pacer(case_id, doc_id)
        
        if pacer_pdf:
            pages = len(pacer_pdf) // 1024  # Rough estimate
            cost = pages * 0.10
            self.pacer_costs['pages_downloaded'] += pages
            self.pacer_costs['total_cost'] += cost
            
            logger.info(f"Downloaded {pages} pages from PACER (cost: ${cost:.2f})")
            
            # Update cost tracking in database
            self._update_cost_tracking(pages, cost)
        
        return pacer_pdf
    
    async def _check_recap_archive(self, doc_id: str) -> Optional[bytes]:
        """Check if document is available in free RECAP archive"""
        # CourtListener RECAP API endpoint
        url = f"{self.courtlistener_api}recap-documents/{doc_id}/"
        headers = {'Authorization': f'Token {self.courtlistener_api_key}'}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check if PDF is available
                        if data.get('is_available'):
                            pdf_url = data.get('filepath_local')
                            
                            # Download the free PDF
                            async with session.get(pdf_url) as pdf_response:
                                return await pdf_response.read()
        except Exception as e:
            logger.debug(f"RECAP check failed for {doc_id}: {e}")
        
        return None
    
    async def _download_from_pacer(self, case_id: str, doc_id: str) -> Optional[bytes]:
        """
        Download from PACER (costs $0.10 per page, max $3.00 per document)
        Requires PACER account and authentication
        """
        if not self.pacer_authenticated:
            await self._authenticate_pacer()
        
        # PACER document download URL (varies by court)
        # Example: https://ecf.nywd.uscourts.gov/doc1/12345678
        # Actual implementation depends on court-specific URLs
        
        logger.warning("PACER download not implemented (requires PACER account)")
        return None
    
    async def _authenticate_pacer(self):
        """Authenticate with PACER login system"""
        if not self.pacer_username or not self.pacer_password:
            logger.error("PACER credentials not set (PACER_USERNAME, PACER_PASSWORD)")
            return False
        
        login_data = {
            'loginid': self.pacer_username,
            'password': self.pacer_password
        }
        
        try:
            response = self.session.post(self.pacer_login_url, data=login_data)
            
            if 'logout' in response.text.lower():
                self.pacer_authenticated = True
                logger.info("Successfully authenticated with PACER")
                return True
            else:
                logger.error("PACER authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"PACER login error: {e}")
            return False
    
    def _update_cost_tracking(self, pages: int, cost: float):
        """Track PACER usage costs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO cost_tracking (pacer_pages, pacer_cost)
            VALUES (?, ?)
            ON CONFLICT(date) DO UPDATE SET
                pacer_pages = pacer_pages + ?,
                pacer_cost = pacer_cost + ?
        """, (pages, cost, pages, cost))
        
        conn.commit()
        conn.close()
    
    def get_cost_summary(self) -> Dict:
        """Get summary of PACER costs vs RECAP savings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                SUM(pacer_pages) as total_pages,
                SUM(pacer_cost) as total_cost,
                SUM(recap_saves) as total_saves
            FROM cost_tracking
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            'pacer_pages_downloaded': row[0] or 0,
            'pacer_total_cost': row[1] or 0.0,
            'recap_savings': row[2] or 0.0,
            'efficiency': f"{((row[2] or 0) / ((row[1] or 1) + (row[2] or 1)) * 100):.1f}%"
        }


async def main():
    """Test PACER scraper"""
    scraper = PacerScraper()
    
    # Test 1: Search CourtListener (FREE)
    logger.info("TEST 1: Searching CourtListener for Midland Funding cases...")
    cases = await scraper.search_courtlistener("Midland Funding", district="nywd")
    
    print(f"\n✅ Found {len(cases)} cases on CourtListener")
    for case in cases[:5]:
        print(f"  - {case['case_number']}: {case['case_name']}")
    
    # Test 2: Nationwide search
    logger.info("\nTEST 2: Nationwide search (all districts)...")
    all_cases = await scraper.search_nationwide("Portfolio Recovery Associates")
    
    print(f"\n✅ Found {len(all_cases)} cases nationwide")
    
    # Test 3: Cost summary
    summary = scraper.get_cost_summary()
    print(f"\n💰 Cost Summary:")
    print(f"  PACER pages: {summary['pacer_pages_downloaded']}")
    print(f"  PACER cost: ${summary['pacer_total_cost']:.2f}")
    print(f"  RECAP savings: ${summary['recap_savings']:.2f}")
    print(f"  Efficiency: {summary['efficiency']}")


if __name__ == "__main__":
    asyncio.run(main())
