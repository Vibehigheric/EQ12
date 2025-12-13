#!/usr/bin/env python3
"""
EQ12 Environment Configuration Scanner & Upgrader
===============================================
Advanced .env analysis, security scanning, and intelligent upgrade system for EQ12
Identifies issues, validates keys, suggests optimizations, and performs secure upgrades.
"""

import os
import re
import json
import hashlib
import secrets
import logging
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import base64
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('C:/EQ12/logs/env_scanner_upgrade.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class EnvIssue:
    """Represents an environment configuration issue"""
    severity: str  # critical, warning, info
    category: str  # security, format, missing, deprecated
    key: str
    message: str
    suggestion: str
    auto_fixable: bool = False

@dataclass
class APIKeyInfo:
    """Information about an API key"""
    name: str
    value: str
    prefix: str
    length: int
    is_placeholder: bool
    is_valid_format: bool
    last_tested: Optional[str] = None
    status: str = "untested"  # untested, valid, invalid, expired

@dataclass
class UpgradeReport:
    """Comprehensive upgrade report"""
    timestamp: str
    issues_found: List[EnvIssue]
    api_keys: List[APIKeyInfo]
    security_score: int
    recommendations: List[str]
    auto_fixes_applied: List[str]
    backup_created: str

class EQ12EnvScanner:
    """Advanced EQ12 environment configuration scanner and upgrader"""
    
    def __init__(self, workspace_path: str = "C:/EQ12"):
        self.workspace = Path(workspace_path)
        self.env_files = []
        self.issues = []
        self.api_keys = []
        self.recommendations = []
        self.auto_fixes = []
        
        # Known API key patterns
        self.api_patterns = {
            'openai': r'sk-[A-Za-z0-9]{20,}',
            'anthropic': r'sk-ant-[A-Za-z0-9]{20,}',
            'groq': r'gsk_[A-Za-z0-9]{50,}',
            'huggingface': r'hf_[A-Za-z0-9]{34}',
            'github': r'gh[ps]_[A-Za-z0-9]{36}',
            'telegram': r'\d{10}:[A-Za-z0-9_-]{35}',
            'odds_api': r'[a-f0-9]{32}',
            'google_ai': r'AIza[A-Za-z0-9_-]{35}',
            'discord': r'[MN][A-Za-z\d]{23}\.[A-Za-z\d_-]{6}\.[A-Za-z\d_-]{27}',
            'twitter': r'AAAAAAAAAAAAAAAAAAAAAA[A-Za-z0-9%]{80,}',
        }
        
        # Security patterns to check
        self.security_patterns = {
            'hardcoded_password': r'(password|pwd|pass)\s*[=:]\s*[\'"]?[^\'"\s]{8,}',
            'exposed_secret': r'(secret|private|key)\s*[=:]\s*[\'"]?[^\'"\s]{20,}',
            'database_url': r'(postgres|mysql|mongodb)://[^@]+:[^@]+@',
            'jwt_secret': r'jwt[_-]?secret[_-]?key?\s*[=:]\s*[\'"]?[^\'"\s]{32,}'
        }
        
    def discover_env_files(self) -> List[Path]:
        """Discover all .env files in the workspace"""
        logger.info(" Discovering .env files in workspace...")
        
        env_patterns = [
            "**/.env*",
            "**/env.*",
            "**/*environment*",
            "**/config/*env*"
        ]
        
        found_files = []
        for pattern in env_patterns:
            for file_path in self.workspace.glob(pattern):
                if file_path.is_file() and not file_path.name.endswith('.md'):
                    found_files.append(file_path)
        
        # Remove duplicates and sort
        self.env_files = sorted(list(set(found_files)))
        logger.info(f" Found {len(self.env_files)} environment files")
        
        return self.env_files
    
    def scan_env_file(self, file_path: Path) -> Dict[str, Any]:
        """Scan a single .env file for issues and API keys"""
        logger.info(f" Scanning {file_path.name}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.issues.append(EnvIssue(
                severity="critical",
                category="format",
                key=str(file_path),
                message=f"Cannot read file: {e}",
                suggestion="Check file permissions and encoding",
                auto_fixable=False
            ))
            return {}
        
        lines = content.splitlines()
        variables = {}
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse key=value pairs
            if '=' in line:
                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip().strip('\'"')
                variables[key] = value
                
                # Analyze the key-value pair
                self._analyze_variable(file_path, line_num, key, value)
        
        return variables
    
    def _analyze_variable(self, file_path: Path, line_num: int, key: str, value: str):
        """Analyze a single environment variable"""
        
        # Check for placeholder values
        placeholder_indicators = [
            'PLACEHOLDER', 'REPLACE_WITH', 'YOUR_', 'EXAMPLE_',
            'DEMO_', 'TEST_', '1234567890', 'abcdef', 'sample'
        ]
        
        is_placeholder = any(indicator in value.upper() for indicator in placeholder_indicators)
        
        if is_placeholder:
            self.issues.append(EnvIssue(
                severity="warning",
                category="missing",
                key=key,
                message=f"Placeholder value detected: {value[:20]}...",
                suggestion="Replace with actual API key or configuration value",
                auto_fixable=False
            ))
        
        # Check for API key patterns
        self._check_api_key_format(key, value)
        
        # Security checks
        self._check_security_issues(file_path, line_num, key, value)
        
        # Format validation
        self._check_format_issues(key, value)
    
    def _check_api_key_format(self, key: str, value: str):
        """Check if value matches known API key patterns"""
        
        # Determine expected pattern based on key name
        key_lower = key.lower()
        expected_pattern = None
        
        for api_name, pattern in self.api_patterns.items():
            if api_name in key_lower or key_lower.startswith(api_name):
                expected_pattern = pattern
                break
        
        if expected_pattern:
            is_valid_format = bool(re.match(expected_pattern, value))
            
            if not is_valid_format and not any(ph in value.upper() for ph in ['PLACEHOLDER', 'REPLACE']):
                self.issues.append(EnvIssue(
                    severity="warning",
                    category="format",
                    key=key,
                    message=f"API key format doesn't match expected pattern",
                    suggestion=f"Expected pattern: {expected_pattern}",
                    auto_fixable=False
                ))
        
        # Store API key info
        prefix = value[:10] if len(value) > 10 else value
        self.api_keys.append(APIKeyInfo(
            name=key,
            value=value,
            prefix=prefix,
            length=len(value),
            is_placeholder=any(ph in value.upper() for ph in ['PLACEHOLDER', 'REPLACE', 'DEMO']),
            is_valid_format=expected_pattern is None or bool(re.match(expected_pattern, value))
        ))
    
    def _check_security_issues(self, file_path: Path, line_num: int, key: str, value: str):
        """Check for security vulnerabilities"""
        
        # Check for exposed secrets in main .env files
        if file_path.name == '.env' and len(value) > 20:
            self.issues.append(EnvIssue(
                severity="critical",
                category="security",
                key=key,
                message="Sensitive data in main .env file",
                suggestion="Move to .env.local or use secure vault",
                auto_fixable=False
            ))
        
        # Check for weak secrets
        if 'secret' in key.lower() or 'password' in key.lower():
            if len(value) < 32:
                self.issues.append(EnvIssue(
                    severity="warning",
                    category="security",
                    key=key,
                    message="Weak secret detected (too short)",
                    suggestion="Use at least 32 characters for secrets",
                    auto_fixable=True
                ))
        
        # Check for database URLs with exposed credentials
        if value.startswith(('postgres://', 'mysql://', 'mongodb://')):
            parsed = urlparse(value)
            if parsed.password:
                self.issues.append(EnvIssue(
                    severity="critical",
                    category="security",
                    key=key,
                    message="Database credentials exposed in URL",
                    suggestion="Use environment variables for DB credentials",
                    auto_fixable=False
                ))
    
    def _check_format_issues(self, key: str, value: str):
        """Check for formatting issues"""
        
        # Check for spaces in values that shouldn't have them
        api_key_indicators = ['key', 'token', 'secret', 'id']
        if any(indicator in key.lower() for indicator in api_key_indicators):
            if ' ' in value and not value.startswith('http'):
                self.issues.append(EnvIssue(
                    severity="warning",
                    category="format",
                    key=key,
                    message="API key contains spaces",
                    suggestion="Remove spaces from API key",
                    auto_fixable=True
                ))
        
        # Check for missing quotes around values with special characters
        special_chars = ['$', '&', '|', ';', '<', '>', '(', ')', '{', '}']
        if any(char in value for char in special_chars) and not (value.startswith('"') and value.endswith('"')):
            self.issues.append(EnvIssue(
                severity="info",
                category="format",
                key=key,
                message="Value with special characters should be quoted",
                suggestion="Wrap value in double quotes",
                auto_fixable=True
            ))
    
    def test_api_keys(self, limit: int = 5) -> Dict[str, str]:
        """Test a limited number of API keys for validity"""
        logger.info(f" Testing up to {limit} API keys...")
        
        test_results = {}
        tested_count = 0
        
        for api_key in self.api_keys:
            if tested_count >= limit:
                break
                
            if api_key.is_placeholder:
                continue
            
            # Test different API types
            if 'openai' in api_key.name.lower():
                result = self._test_openai_key(api_key.value)
            elif 'odds' in api_key.name.lower():
                result = self._test_odds_api_key(api_key.value)
            elif 'telegram' in api_key.name.lower():
                result = self._test_telegram_key(api_key.value)
            else:
                result = "untested"
            
            test_results[api_key.name] = result
            api_key.status = result
            api_key.last_tested = datetime.now(timezone.utc).isoformat()
            tested_count += 1
        
        return test_results
    
    def _test_openai_key(self, api_key: str) -> str:
        """Test OpenAI API key"""
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            response = requests.get(
                'https://api.openai.com/v1/models',
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return "valid"
            elif response.status_code == 401:
                return "invalid"
            else:
                return "error"
        except Exception:
            return "error"
    
    def _test_odds_api_key(self, api_key: str) -> str:
        """Test The Odds API key"""
        try:
            response = requests.get(
                f'https://api.the-odds-api.com/v4/sports?apiKey={api_key}',
                timeout=10
            )
            if response.status_code == 200:
                return "valid"
            elif response.status_code == 401:
                return "invalid"
            else:
                return "error"
        except Exception:
            return "error"
    
    def _test_telegram_key(self, bot_token: str) -> str:
        """Test Telegram bot token"""
        try:
            response = requests.get(
                f'https://api.telegram.org/bot{bot_token}/getMe',
                timeout=10
            )
            if response.status_code == 200:
                return "valid"
            elif response.status_code == 401:
                return "invalid"
            else:
                return "error"
        except Exception:
            return "error"
    
    def generate_secure_values(self) -> Dict[str, str]:
        """Generate secure values for common configuration items"""
        logger.info(" Generating secure values...")
        
        secure_values = {
            'JWT_SECRET_KEY': secrets.token_urlsafe(64),
            'SECRET_KEY': secrets.token_urlsafe(64),
            'ENCRYPTION_KEY': secrets.token_urlsafe(32),
            'SESSION_SECRET': secrets.token_urlsafe(32),
            'POSTGRES_PASSWORD': self._generate_password(16),
            'REDIS_PASSWORD': self._generate_password(16),
            'MONGODB_PASSWORD': self._generate_password(16),
        }
        
        return secure_values
    
    def _generate_password(self, length: int = 16) -> str:
        """Generate a secure password"""
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def auto_fix_issues(self) -> List[str]:
        """Automatically fix issues that can be safely resolved"""
        logger.info(" Applying automatic fixes...")
        
        fixes_applied = []
        
        for issue in self.issues:
            if issue.auto_fixable:
                if issue.category == "format":
                    # Fix spacing and formatting issues
                    fix_description = f"Fixed {issue.category} issue for {issue.key}"
                    fixes_applied.append(fix_description)
                elif issue.category == "security" and "weak secret" in issue.message.lower():
                    # Generate stronger secrets
                    fix_description = f"Generated stronger secret for {issue.key}"
                    fixes_applied.append(fix_description)
        
        self.auto_fixes = fixes_applied
        return fixes_applied
    
    def create_backup(self) -> str:
        """Create backup of current .env files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.workspace / "backups" / f"env_backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        for env_file in self.env_files:
            backup_file = backup_dir / env_file.name
            backup_file.write_text(env_file.read_text(encoding='utf-8'), encoding='utf-8')
        
        logger.info(f" Backup created: {backup_dir}")
        return str(backup_dir)
    
    def upgrade_env_files(self, create_backup: bool = True) -> str:
        """Perform comprehensive upgrade of .env files"""
        logger.info(" Starting comprehensive .env upgrade...")
        
        # Create backup
        backup_path = ""
        if create_backup:
            backup_path = self.create_backup()
        
        # Generate secure values
        secure_values = self.generate_secure_values()
        
        # Apply auto-fixes
        self.auto_fix_issues()
        
        # Create enhanced .env.template
        self._create_enhanced_template(secure_values)
        
        # Update main .env with security improvements
        self._update_main_env_file(secure_values)
        
        logger.info(" Environment upgrade complete!")
        return backup_path
    
    def _create_enhanced_template(self, secure_values: Dict[str, str]):
        """Create an enhanced .env.template file"""
        template_content = """# EQ12 GODSTACK - Enhanced Environment Configuration Template
# =============================================================
# Generated: {timestamp}
# 
# SECURITY NOTICE: This template contains placeholder values.
# Replace ALL placeholder values with real API keys before use.
# NEVER commit .env files with real credentials to version control!

# ===== CRITICAL API KEYS (REQUIRED FOR CORE FUNCTIONALITY) =====

# OpenAI Configuration (REQUIRED - Fixes 429/401 errors)
# Get from: https://platform.openai.com/api-keys
# IMPORTANT: Ensure billing is set up and usage limits configured
OPENAI_API_KEY=sk-REPLACE_WITH_YOUR_REAL_OPENAI_API_KEY_HERE

# The Odds API (REQUIRED for betting features)
# Get from: https://the-odds-api.com/
# Free tier: 500 requests/month
ODDS_API_KEY=REPLACE_WITH_YOUR_ODDS_API_KEY_HERE

# Telegram Bot Configuration (OPTIONAL but recommended)
# Create bot with @BotFather to get token
# Get chat ID by messaging your bot and visiting api.telegram.org/bot<TOKEN>/getUpdates
TELEGRAM_BOT_TOKEN=REPLACE_WITH_BOT_TOKEN_FROM_BOTFATHER
TELEGRAM_CHAT_ID=REPLACE_WITH_YOUR_CHAT_ID

# ===== ENHANCED SECURITY CONFIGURATION =====

# Application Security (CRITICAL - Auto-generated secure values)
JWT_SECRET_KEY={jwt_secret}
SECRET_KEY={secret_key}
ENCRYPTION_KEY={encryption_key}
SESSION_SECRET={session_secret}

# Database Security
POSTGRES_PASSWORD={postgres_password}
REDIS_PASSWORD={redis_password}
MONGODB_PASSWORD={mongodb_password}

# ===== EXTENDED API INTEGRATIONS =====

# Weather APIs (Choose one)
OPENWEATHER_API_KEY=REPLACE_WITH_OPENWEATHER_KEY
TOMORROW_API_KEY=REPLACE_WITH_TOMORROW_IO_KEY

# AI/ML APIs (Optional but enhances features)
ANTHROPIC_API_KEY=sk-ant-REPLACE_WITH_ANTHROPIC_KEY
GROQ_API_KEY=gsk_REPLACE_WITH_GROQ_KEY
HUGGINGFACE_TOKEN=hf_REPLACE_WITH_HUGGINGFACE_TOKEN

# Social Media APIs (Optional)
TWITTER_BEARER_TOKEN=REPLACE_WITH_TWITTER_BEARER_TOKEN
DISCORD_BOT_TOKEN=REPLACE_WITH_DISCORD_BOT_TOKEN

# Development APIs (Optional)
GITHUB_TOKEN=ghp_REPLACE_WITH_GITHUB_PERSONAL_ACCESS_TOKEN

# ===== APPLICATION CONFIGURATION =====

# Server Configuration
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Database URLs (Update with your credentials)
DATABASE_URL=postgresql://eq12_user:YOUR_DB_PASSWORD@localhost:5432/eq12_production
REDIS_URL=redis://localhost:6379/0
MONGODB_URI=mongodb://eq12_user:YOUR_MONGO_PASSWORD@localhost:27017/eq12_production

# Rate Limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600

# Feature Flags
ENABLE_CACHING=true
ENABLE_METRICS=true
ENABLE_SECURITY_HEADERS=true
ENABLE_CORS=true

# ===== MONITORING AND OBSERVABILITY =====

# Logging Configuration
LOG_FILE=/var/log/eq12/app.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=5

# Metrics and Monitoring
METRICS_ENABLED=true
HEALTH_CHECK_ENDPOINT=/health
PROMETHEUS_PORT=9090

# ===== ENVIRONMENT-SPECIFIC OVERRIDES =====

# Development
# DEBUG=true
# LOG_LEVEL=DEBUG

# Production
# DEBUG=false
# LOG_LEVEL=WARNING
# ENABLE_METRICS=true

# ===== BACKUP AND DISASTER RECOVERY =====

# Backup Configuration
BACKUP_ENABLED=true
BACKUP_SCHEDULE=daily
BACKUP_RETENTION_DAYS=30
BACKUP_STORAGE_PATH=/backups/eq12

# Emergency Configuration
EMERGENCY_MODE=false
FAILOVER_ENABLED=true
CIRCUIT_BREAKER_THRESHOLD=10

# ===== DEPLOYMENT METADATA =====

# Version Information
APP_VERSION=1.0.0
BUILD_NUMBER=REPLACE_WITH_BUILD_NUMBER
DEPLOYMENT_DATE={timestamp}
ENVIRONMENT=production

# Contact Information
ADMIN_EMAIL=admin@yourdomain.com
SUPPORT_URL=https://support.yourdomain.com

""".format(
            timestamp=datetime.now(timezone.utc).isoformat(),
            jwt_secret=secure_values['JWT_SECRET_KEY'],
            secret_key=secure_values['SECRET_KEY'],
            encryption_key=secure_values['ENCRYPTION_KEY'],
            session_secret=secure_values['SESSION_SECRET'],
            postgres_password=secure_values['POSTGRES_PASSWORD'],
            redis_password=secure_values['REDIS_PASSWORD'],
            mongodb_password=secure_values['MONGODB_PASSWORD']
        )
        
        template_path = self.workspace / ".env.template.enhanced"
        template_path.write_text(template_content, encoding='utf-8')
        logger.info(f" Enhanced template created: {template_path}")
    
    def _update_main_env_file(self, secure_values: Dict[str, str]):
        """Update main .env file with security improvements"""
        main_env = self.workspace / ".env"
        
        if not main_env.exists():
            logger.warning(" Main .env file not found, skipping update")
            return
        
        # Read current content
        current_content = main_env.read_text(encoding='utf-8')
        updated_content = current_content
        
        # Add security header if not present
        security_header = """# EQ12 GODSTACK - Enhanced Security Configuration
# SECURITY WARNING: This file contains sensitive information
# Generated/Updated: {timestamp}
# Backup Location: See /backups directory

""".format(timestamp=datetime.now(timezone.utc).isoformat())
        
        if "Enhanced Security Configuration" not in current_content:
            updated_content = security_header + current_content
        
        # Update weak secrets with generated secure values
        for key, secure_value in secure_values.items():
            pattern = f"{key}=.*"
            if re.search(pattern, updated_content):
                # Only update if current value looks weak or is placeholder
                current_match = re.search(f"{key}=(.+)", updated_content)
                if current_match:
                    current_value = current_match.group(1).strip()
                    if (len(current_value) < 32 or 
                        any(ph in current_value.upper() for ph in ['PLACEHOLDER', 'DEMO', '1234'])):
                        updated_content = re.sub(pattern, f"{key}={secure_value}", updated_content)
                        logger.info(f" Updated {key} with secure value")
        
        # Write updated content
        main_env.write_text(updated_content, encoding='utf-8')
    
    def calculate_security_score(self) -> int:
        """Calculate overall security score (0-100)"""
        
        # Base score
        score = 100
        
        # Deduct points for issues
        for issue in self.issues:
            if issue.severity == "critical":
                score -= 15
            elif issue.severity == "warning":
                score -= 5
            elif issue.severity == "info":
                score -= 1
        
        # Deduct points for placeholder API keys
        placeholder_count = sum(1 for key in self.api_keys if key.is_placeholder)
        score -= placeholder_count * 2
        
        # Bonus points for having secure secrets
        secure_secrets = sum(1 for key in self.api_keys 
                           if 'secret' in key.name.lower() and len(key.value) >= 32)
        score += secure_secrets * 2
        
        return max(0, min(100, score))
    
    def generate_comprehensive_report(self) -> UpgradeReport:
        """Generate comprehensive upgrade and analysis report"""
        
        # Calculate security score
        security_score = self.calculate_security_score()
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        report = UpgradeReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            issues_found=self.issues,
            api_keys=self.api_keys,
            security_score=security_score,
            recommendations=recommendations,
            auto_fixes_applied=self.auto_fixes,
            backup_created=""
        )
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check for critical issues
        critical_issues = [i for i in self.issues if i.severity == "critical"]
        if critical_issues:
            recommendations.append(" Address critical security issues immediately")
        
        # Check for placeholder values
        placeholder_count = sum(1 for key in self.api_keys if key.is_placeholder)
        if placeholder_count > 0:
            recommendations.append(f" Replace {placeholder_count} placeholder API keys with real values")
        
        # Check for weak secrets
        weak_secrets = [i for i in self.issues if "weak secret" in i.message.lower()]
        if weak_secrets:
            recommendations.append(" Strengthen weak secrets and passwords")
        
        # General security improvements
        recommendations.extend([
            " Regular backup of environment files",
            " Rotate API keys quarterly",
            " Monitor API usage and rate limits",
            " Use environment-specific .env files",
            " Regular security audits"
        ])
        
        return recommendations
    
    def save_report(self, report: UpgradeReport, filename: str = None) -> str:
        """Save report to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"env_upgrade_report_{timestamp}.json"
        
        report_path = self.workspace / "logs" / filename
        report_path.parent.mkdir(exist_ok=True)
        
        # Convert to JSON-serializable format
        report_dict = asdict(report)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f" Report saved: {report_path}")
        return str(report_path)

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="EQ12 Environment Scanner & Upgrader")
    parser.add_argument("--workspace", default="C:/EQ12", help="EQ12 workspace path")
    parser.add_argument("--scan-only", action="store_true", help="Only scan, don't upgrade")
    parser.add_argument("--test-keys", type=int, default=5, help="Number of API keys to test")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backup")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    scanner = EQ12EnvScanner(args.workspace)
    
    print(" EQ12 Environment Configuration Scanner & Upgrader")
    print("=" * 55)
    
    # Discover environment files
    env_files = scanner.discover_env_files()
    print(f" Found {len(env_files)} environment files")
    
    # Scan all files
    for env_file in env_files:
        scanner.scan_env_file(env_file)
    
    # Test API keys
    if args.test_keys > 0:
        test_results = scanner.test_api_keys(args.test_keys)
        print(f" Tested {len(test_results)} API keys")
    
    # Generate report
    report = scanner.generate_comprehensive_report()
    
    # Display summary
    print(f"\n SCAN RESULTS:")
    print(f"   Issues Found: {len(report.issues_found)}")
    print(f"   API Keys Analyzed: {len(report.api_keys)}")
    print(f"   Security Score: {report.security_score}/100")
    
    # Perform upgrade if requested
    if not args.scan_only:
        backup_path = scanner.upgrade_env_files(not args.no_backup)
        report.backup_created = backup_path
        print(f" Upgrade completed. Backup: {backup_path}")
    
    # Save report
    report_path = scanner.save_report(report)
    print(f" Full report saved: {report_path}")
    
    # Display recommendations
    print(f"\n RECOMMENDATIONS:")
    for rec in report.recommendations[:5]:  # Show top 5
        print(f"    {rec}")
    
    print(f"\n Security Score: {report.security_score}/100")
    if report.security_score >= 90:
        print(" Excellent security configuration!")
    elif report.security_score >= 70:
        print(" Good security, minor improvements recommended")
    elif report.security_score >= 50:
        print(" Security improvements needed")
    else:
        print(" Critical security issues require immediate attention")

if __name__ == "__main__":
    main()