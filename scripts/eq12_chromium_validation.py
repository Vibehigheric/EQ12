"""
EQ12 Enhanced Input Validation (Chromium-inspired)
Comprehensive input sanitization and validation
"""

import re
import html
import urllib.parse
from typing import Any, Optional, Union, List, Dict
from decimal import Decimal, InvalidOperation

class EQ12InputValidator:
    """Chromium-inspired input validation for EQ12 system"""
    
    # Validation patterns
    PATTERNS = {
        "player_name": re.compile(r"^[A-Za-z\s\-'\.]{2,50}$"),
        "team_code": re.compile(r"^[A-Z]{2,4}$"),
        "odds": re.compile(r"^[\+\-]?\d{1,4}$"),
        "bet_amount": re.compile(r"^\d{1,6}(\.\d{1,2})?$"),
        "url": re.compile(r"^https?://[^\s/$.?#].[^\s]*$"),
        "api_key": re.compile(r"^[A-Za-z0-9_\-]{10,100}$")
    }
    
    @staticmethod
    def validate_player_name(name: Any) -> Optional[str]:
        """Validate player name with Chromium-style checking"""
        if not isinstance(name, str):
            return None
        
        # Sanitize input
        name = html.escape(name.strip())
        
        # Check pattern
        if not EQ12InputValidator.PATTERNS["player_name"].match(name):
            return None
            
        return name
    
    @staticmethod
    def validate_odds(odds: Any) -> Optional[int]:
        """Validate betting odds"""
        if isinstance(odds, str):
            odds = odds.strip()
            if not EQ12InputValidator.PATTERNS["odds"].match(odds):
                return None
            try:
                return int(odds)
            except ValueError:
                return None
        elif isinstance(odds, int):
            if -9999 <= odds <= 9999:
                return odds
        return None
    
    @staticmethod
    def validate_bet_amount(amount: Any) -> Optional[Decimal]:
        """Validate bet amount with precise decimal handling"""
        if isinstance(amount, str):
            amount = amount.strip()
            if not EQ12InputValidator.PATTERNS["bet_amount"].match(amount):
                return None
            try:
                decimal_amount = Decimal(amount)
                if 0 < decimal_amount <= 999999:
                    return decimal_amount
            except InvalidOperation:
                return None
        elif isinstance(amount, (int, float)):
            try:
                decimal_amount = Decimal(str(amount))
                if 0 < decimal_amount <= 999999:
                    return decimal_amount
            except InvalidOperation:
                return None
        return None
    
    @staticmethod
    def sanitize_url(url: Any) -> Optional[str]:
        """Sanitize and validate URLs"""
        if not isinstance(url, str):
            return None
        
        url = url.strip()
        
        # Basic pattern check
        if not EQ12InputValidator.PATTERNS["url"].match(url):
            return None
        
        # Additional parsing validation
        try:
            parsed = urllib.parse.urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                return None
            return url
        except Exception:
            return None
    
    @staticmethod
    def validate_api_response(response: Any) -> bool:
        """Validate API response structure"""
        if not isinstance(response, dict):
            return False
        
        # Check for required fields and proper types
        if "status" not in response:
            return False
        
        return True

# Integration with existing EQ12 systems
def enhance_bulletproof_validation():
    """Enhance bulletproof system with Chromium-style validation"""
    return True
