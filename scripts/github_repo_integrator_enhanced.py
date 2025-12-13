#!/usr/bin/env python3
"""
EQ12 GitHub Repository Auto-Integrator - ENHANCED MULTI-LANGUAGE VERSION
Expert-level GitHub Code Search → Pull → Analyze → Integrate system

Supports: Python, JavaScript, C++, Go, Java, PHP, Ruby, VB.NET
Searches for: Arbitrage bots, Kelly criterion implementations, OddsAPI wrappers
Integrates into: EQ12 VB.NET modules with monetization hooks
"""

import argparse
import logging
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:\\\\EQ12\\logs\\github_integrator_enhanced.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class EnhancedGitHubIntegrator:
    """
    Advanced GitHub repository integration system for EQ12

    Features:
    - Multi-language code analysis (Python, JS, C++, Go, Java, PHP, Ruby)
    - Smart repository ranking and selection
    - Automated VB.NET module generation
    - Kelly Criterion and Arbitrage bot integration
    - OddsAPI wrapper conversion
    - Monetization hook injection
    """

    def __init__(self, github_token: str | None = None):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.session = requests.Session()
        self.base_url = "https://api.github.com"
        self.clone_root = Path("C:\\\\EQ12\\\\data\\github_repos")
        self.clone_root.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self.init_database()

        # Configure requests session
        if self.github_token:
            self.session.headers.update(
                {
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "EQ12-Enhanced-Integrator/2.0",
                }
            )

        # Multi-language search patterns
        self.search_patterns = {
            "arbitrage": [
                '"arbitrage" AND ("betting" OR "sports") language:python',
                '"arbitrage bot" language:javascript',
                '"odds comparison" AND "arbitrage" language:python',
                '"arbitrage detection" language:cpp',
                '"surebet" AND "arbitrage" language:go',
                '"arbitrage calculator" language:java',
                '"sports arbitrage" language:php',
                '"betting arbitrage" language:ruby',
            ],
            "kelly": [
                '"kelly criterion" language:python',
                '"fractional kelly" language:python',
                '"kelly bet sizing" language:javascript',
                '"bankroll management" AND "kelly" language:python',
                '"optimal betting" AND "kelly" language:r',
                '"kelly formula" language:java',
                '"kelly stake" language:cpp',
                '"kelly calculator" language:go',
            ],
            "oddsapi": [
                '"TheOddsAPI" language:python',
                '"odds api" language:javascript',
                '"sportsbook api" language:python',
                '"betting odds api" language:php',
                '"odds data api" language:ruby',
                '"sports betting api" language:go',
                '"odds feed" language:cpp',
                '"live odds" language:java',
            ],
        }

        logger.info("Enhanced GitHub Integrator initialized")

    def init_database(self):
        """Initialize SQLite database for tracking integrations"""
        db_path = "C:\\\\EQ12\\\\data\\github_integration_enhanced.db"
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS searches_enhanced (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT (datetime('now')),
                    query TEXT NOT NULL,
                    category TEXT,
                    language TEXT,
                    result_count INTEGER,
                    status TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS repos_enhanced (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT (datetime('now')),
                    repo_full_name TEXT UNIQUE NOT NULL,
                    clone_path TEXT,
                    primary_language TEXT,
                    all_languages TEXT,
                    stars INTEGER DEFAULT 0,
                    category TEXT,
                    complexity_score INTEGER,
                    monetization_score INTEGER,
                    status TEXT,
                    integration_notes TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS vb_modules_enhanced (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT (datetime('now')),
                    module_name TEXT NOT NULL,
                    source_repo TEXT,
                    source_languages TEXT,
                    integration_type TEXT,
                    file_path TEXT,
                    status TEXT,
                    monetization_features TEXT
                )
            """
            )

            conn.commit()

    def search_repositories(self, category: str = "all", max_results: int = 50) -> list[dict]:
        """
        Enhanced GitHub search with multi-language support
        """
        all_repos = []

        patterns = []
        if category == "all":
            for cat_patterns in self.search_patterns.values():
                patterns.extend(cat_patterns)
        elif category in self.search_patterns:
            patterns = self.search_patterns[category]
        else:
            # Custom category with multi-language support
            languages = ["python", "javascript", "cpp", "go", "java", "php", "ruby"]
            patterns = [f'"{category}" language:{lang}' for lang in languages]

        logger.info(f"Searching with {len(patterns)} patterns for category: {category}")

        for pattern in patterns:
            try:
                repos = self._search_single_pattern(pattern, category)
                if repos:
                    all_repos.extend(repos)
                    logger.info(f"Pattern '{pattern}' found {len(repos)} repositories")
            except Exception as e:
                logger.error(f"Search error for pattern '{pattern}': {e}")

        # Remove duplicates and rank by multiple factors
        unique_repos = {}
        for repo in all_repos:
            repo_key = repo.get("full_name")
            if repo_key and repo_key not in unique_repos:
                unique_repos[repo_key] = repo

        # Enhanced ranking algorithm
        ranked_repos = self._rank_repositories(list(unique_repos.values()))

        return ranked_repos[:max_results]

    def _search_single_pattern(self, query: str, category: str) -> list[dict]:
        """Execute enhanced GitHub search with better error handling"""
        try:
            url = f"{self.base_url}/search/repositories"
            params = {"q": query, "sort": "stars", "order": "desc", "per_page": 20}

            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                repos = data.get("items", [])

                # Log search with language detection
                language = self._extract_language_from_query(query)
                self._log_search(query, category, language, len(repos), "success")

                return repos
            logger.warning(f"Search failed: {query}, Status: {response.status_code}")
            self._log_search(query, category, "unknown", 0, "failed")
            return []

        except Exception as e:
            logger.error(f"Search error for '{query}': {e}")
            self._log_search(query, category, "unknown", 0, "error")
            return []

    def _extract_language_from_query(self, query: str) -> str:
        """Extract programming language from search query"""
        language_map = {
            "python": "python",
            "javascript": "javascript",
            "cpp": "cpp",
            "go": "go",
            "java": "java",
            "php": "php",
            "ruby": "ruby",
        }

        for key, value in language_map.items():
            if f"language:{key}" in query.lower():
                return value
        return "unknown"

    def _rank_repositories(self, repos: list[dict]) -> list[dict]:
        """Enhanced repository ranking algorithm"""

        def calculate_score(repo):
            score = 0

            # Star rating (logarithmic scale)
            stars = repo.get("stargazers_count", 0)
            score += min(50, stars // 10)  # Max 50 points for stars

            # Language bonus
            language = repo.get("language", "").lower()
            if language == "python":
                score += 30
            elif language in ["javascript", "java"]:
                score += 25
            elif language in ["cpp", "go"]:
                score += 20
            elif language in ["php", "ruby"]:
                score += 15

            # Recent activity bonus
            try:
                updated = datetime.fromisoformat(repo.get("updated_at", "").replace("Z", "+00:00"))
                days_old = (datetime.now(UTC) - updated).days
                if days_old < 30:
                    score += 20
                elif days_old < 90:
                    score += 10
            except:
                pass

            # Keyword relevance in name/description
            name_desc = f"{repo.get('name', '')} {repo.get('description', '')}".lower()
            keywords = ["betting", "arbitrage", "kelly", "odds", "sportsbook", "api"]
            for keyword in keywords:
                if keyword in name_desc:
                    score += 5

            return score

        # Sort by calculated score
        return sorted(repos, key=calculate_score, reverse=True)

    def clone_repository(self, repo_url: str, repo_name: str) -> str | None:
        """
        Enhanced repository cloning with fallback methods
        """
        try:
            safe_name = re.sub(r"[^\w\-_]", "_", repo_name)
            clone_path = self.clone_root / safe_name

            # Remove existing if present
            if clone_path.exists():
                shutil.rmtree(clone_path)

            logger.info(f"Cloning {repo_url}")

            # Method 1: Try git command
            result = subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, str(clone_path)],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                self._log_repo(repo_name, str(clone_path), "cloned")
                return str(clone_path)

            # Method 2: Try downloading zip
            logger.info(f"Git clone failed, trying zip download for {repo_name}")
            return self._download_repo_zip(repo_url, clone_path)

        except Exception as e:
            logger.error(f"Clone failed for {repo_url}: {e}")
            self._log_repo(repo_name, "", "clone_failed")
            return None

    def _download_repo_zip(self, repo_url: str, clone_path: Path) -> str | None:
        """Fallback method to download repository as ZIP"""
        try:
            # Convert clone URL to zip download URL
            if repo_url.endswith(".git"):
                repo_url = repo_url[:-4]

            zip_url = f"{repo_url}/archive/main.zip"

            response = self.session.get(zip_url, timeout=300)
            if response.status_code != 200:
                zip_url = f"{repo_url}/archive/master.zip"
                response = self.session.get(zip_url, timeout=300)

            if response.status_code == 200:
                # Save and extract zip
                zip_path = clone_path.with_suffix(".zip")
                with open(zip_path, "wb") as f:
                    f.write(response.content)

                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(clone_path.parent)

                # Find extracted directory
                extracted_dirs = [
                    d
                    for d in clone_path.parent.iterdir()
                    if d.is_dir() and d.name.startswith(clone_path.name)
                ]

                if extracted_dirs:
                    if extracted_dirs[0] != clone_path:
                        extracted_dirs[0].rename(clone_path)

                    os.remove(zip_path)
                    return str(clone_path)

            return None

        except Exception as e:
            logger.error(f"ZIP download failed: {e}")
            return None

    def analyze_repository(self, repo_path: str) -> dict:
        """
        Enhanced multi-language repository analysis
        """
        analysis = {
            "languages": {},
            "files_of_interest": [],
            "integration_type": "unknown",
            "complexity_score": 0,
            "monetization_potential": 0,
            "quality_indicators": {},
            "api_endpoints": [],
            "database_schemas": [],
        }

        try:
            repo_path = Path(repo_path)
            if not repo_path.exists():
                return analysis

            # Enhanced file analysis
            for file_path in repo_path.rglob("*"):
                if (
                    file_path.is_file() and file_path.stat().st_size < 1024 * 1024
                ):  # Skip large files
                    suffix = file_path.suffix.lower()

                    # Count language files with more detail
                    language_map = {
                        ".py": "python",
                        ".js": "javascript",
                        ".ts": "typescript",
                        ".cpp": "cpp",
                        ".cc": "cpp",
                        ".cxx": "cpp",
                        ".go": "go",
                        ".java": "java",
                        ".php": "php",
                        ".rb": "ruby",
                        ".vb": "vbnet",
                        ".cs": "csharp",
                        ".sql": "sql",
                        ".json": "json",
                        ".yaml": "yaml",
                        ".yml": "yaml",
                    }

                    if suffix in language_map:
                        lang = language_map[suffix]
                        analysis["languages"][lang] = analysis["languages"].get(lang, 0) + 1

                    # Look for files of interest
                    filename_lower = file_path.name.lower()
                    content_keywords = [
                        "kelly",
                        "arbitrage",
                        "odds",
                        "betting",
                        "sportsbook",
                        "api",
                    ]

                    if any(keyword in filename_lower for keyword in content_keywords):
                        analysis["files_of_interest"].append(
                            {
                                "path": str(file_path),
                                "type": suffix,
                                "size": file_path.stat().st_size,
                            }
                        )

                    # Look for API endpoints and schemas
                    if suffix in [".py", ".js", ".go", ".java", ".php", ".rb"]:
                        self._analyze_code_content(file_path, analysis)

            # Determine integration type with enhanced logic
            analysis["integration_type"] = self._classify_repo_type_enhanced(analysis)

            # Calculate enhanced scores
            analysis["complexity_score"] = self._calculate_complexity_score(analysis)
            analysis["monetization_potential"] = self._calculate_monetization_score_enhanced(
                analysis
            )
            analysis["quality_indicators"] = self._assess_code_quality(analysis)

            logger.info(
                f"Enhanced analysis: {analysis['integration_type']} type, "
                f"complexity: {analysis['complexity_score']}, "
                f"monetization: {analysis['monetization_potential']}"
            )

        except Exception as e:
            logger.error(f"Enhanced repository analysis failed: {e}")

        return analysis

    def _analyze_code_content(self, file_path: Path, analysis: dict):
        """Analyze code content for API endpoints and schemas"""
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read().lower()

                # Look for API endpoints
                api_patterns = [
                    r'@app\.route\([\'"]([^\'"]+)',  # Flask
                    r'app\.get\([\'"]([^\'"]+)',  # Express.js
                    r'router\.post\([\'"]([^\'"]+)',  # Express.js
                    r'@RequestMapping\([\'"]([^\'"]+)',  # Spring
                ]

                for pattern in api_patterns:
                    matches = re.findall(pattern, content)
                    analysis["api_endpoints"].extend(matches)

                # Look for database schemas
                if "create table" in content or "schema" in content:
                    analysis["database_schemas"].append(str(file_path))

        except Exception as e:
            logger.debug(f"Content analysis failed for {file_path}: {e}")

    def _classify_repo_type_enhanced(self, analysis: dict) -> str:
        """Enhanced repository type classification"""
        # Check files of interest
        file_text = " ".join([f["path"] for f in analysis["files_of_interest"]]).lower()

        # Check API endpoints
        api_text = " ".join(analysis["api_endpoints"]).lower()
        combined_text = f"{file_text} {api_text}"

        # Enhanced classification logic
        if "kelly" in combined_text or "bankroll" in combined_text:
            return "kelly"
        if "arbitrage" in combined_text or "arb" in combined_text or "surebet" in combined_text:
            return "arbitrage"
        if ("odds" in combined_text and "api" in combined_text) or "sportsbook" in combined_text:
            return "oddsapi"
        if "betting" in combined_text or "wager" in combined_text:
            return "general_betting"
        if len(analysis["api_endpoints"]) > 5:
            return "api_framework"
        return "utility"

    def _calculate_complexity_score(self, analysis: dict) -> int:
        """Calculate code complexity score"""
        score = sum(analysis["languages"].values())

        # Bonus for multiple languages
        if len(analysis["languages"]) > 3:
            score += 20

        # Bonus for database schemas
        score += len(analysis["database_schemas"]) * 5

        # Bonus for API endpoints
        score += len(analysis["api_endpoints"]) * 2

        return min(score, 200)  # Cap at 200

    def _calculate_monetization_score_enhanced(self, analysis: dict) -> int:
        """Enhanced monetization potential calculation"""
        score = 0

        # Language bonuses (enhanced)
        lang_scores = {
            "python": 35,
            "javascript": 25,
            "java": 20,
            "cpp": 15,
            "go": 15,
            "php": 10,
            "ruby": 10,
        }

        for lang, _count in analysis["languages"].items():
            if lang in lang_scores:
                score += lang_scores[lang]

        # Integration type bonuses (enhanced)
        type_scores = {
            "kelly": 50,
            "arbitrage": 45,
            "oddsapi": 40,
            "general_betting": 25,
            "api_framework": 20,
            "utility": 10,
        }

        integration_type = analysis["integration_type"]
        if integration_type in type_scores:
            score += type_scores[integration_type]

        # File complexity bonus
        score += min(len(analysis["files_of_interest"]) * 3, 20)

        # API endpoints bonus
        score += min(len(analysis["api_endpoints"]) * 2, 15)

        # Database schema bonus
        score += len(analysis["database_schemas"]) * 5

        return min(score, 100)

    def _assess_code_quality(self, analysis: dict) -> dict:
        """Assess code quality indicators"""
        indicators = {
            "has_tests": False,
            "has_documentation": False,
            "has_ci_cd": False,
            "multiple_languages": len(analysis["languages"]) > 1,
            "has_api": len(analysis["api_endpoints"]) > 0,
            "has_database": len(analysis["database_schemas"]) > 0,
        }

        # Check for common quality patterns
        for file_info in analysis["files_of_interest"]:
            path_lower = file_info["path"].lower()
            if "test" in path_lower or "spec" in path_lower:
                indicators["has_tests"] = True
            if "readme" in path_lower or "doc" in path_lower:
                indicators["has_documentation"] = True
            if ".github" in path_lower or ".gitlab" in path_lower:
                indicators["has_ci_cd"] = True

        return indicators

    def generate_enhanced_vb_module(
        self, repo_path: str, analysis: dict, repo_name: str
    ) -> str | None:
        """
        Generate enhanced VB.NET module with advanced features
        """
        try:
            integration_type = analysis["integration_type"]

            if integration_type == "kelly":
                return self._generate_enhanced_kelly_module(repo_path, analysis, repo_name)
            if integration_type == "arbitrage":
                return self._generate_enhanced_arbitrage_module(repo_path, analysis, repo_name)
            if integration_type == "oddsapi":
                return self._generate_enhanced_oddsapi_module(repo_path, analysis, repo_name)
            return self._generate_enhanced_utility_module(repo_path, analysis, repo_name)

        except Exception as e:
            logger.error(f"Enhanced VB.NET module generation failed: {e}")
            return None

    def _generate_enhanced_kelly_module(
        self, repo_path: str, analysis: dict, repo_name: str
    ) -> str:
        """Generate enhanced Kelly Criterion VB.NET module"""
        languages = ", ".join(analysis["languages"].keys())
        monetization_features = self._get_monetization_features(analysis)

        template = """
' ENHANCED Kelly Criterion Module - Auto-generated from {repo_name}
' Generated by EQ12 Enhanced GitHub Integrator at {datetime.now().isoformat()}
' Source Languages: {languages}
' Complexity Score: {analysis["complexity_score"]}
' Monetization Score: {analysis["monetization_potential"]}

Imports System
Imports System.Data
Imports System.Math
Imports System.Threading.Tasks
Imports Newtonsoft.Json

Public Class SuperKellyCalculator

    ' Multi-algorithm Kelly implementation based on {repo_name}
    Public Shared Function CalculateOptimalStakeAdvanced(
        bankroll As Double,
        odds As Double,
        winProbability As Double,
        Optional fraction As Double = 0.5,
        Optional maxRisk As Double = 0.1,
        Optional algorithm As String = "standard"
    ) As EnhancedKellyResult

        Try
            Dim result As New EnhancedKellyResult With {{
                .Bankroll = bankroll,
                .Odds = odds,
                .WinProbability = winProbability,
                .Fraction = fraction,
                .MaxRisk = maxRisk,
                .Algorithm = algorithm,
                .SourceRepo = "{repo_name}",
                .SourceLanguages = "{languages}",
                .Timestamp = DateTime.UtcNow
            }}

            ' Convert odds format
            Dim decimalOdds As Double = ConvertOddsToDecimal(odds)

            ' Calculate Kelly using specified algorithm
            Select Case algorithm.ToLower()
                Case "standard"
                    result.KellyFraction = CalculateStandardKelly(decimalOdds, winProbability)
                Case "fractional"
                    result.KellyFraction = (
                        CalculateFractionalKelly(decimalOdds, winProbability, fraction)
                    )
                Case "adaptive"
                    result.KellyFraction = (
                        CalculateAdaptiveKelly(decimalOdds, winProbability, bankroll)
                    )
                Case Else
                    result.KellyFraction = CalculateStandardKelly(decimalOdds, winProbability)
            End Select

            ' Apply safety constraints
            result.SafeKelly = Math.Min(result.KellyFraction * fraction, maxRisk)
            result.SafeKelly = Math.Max(0, result.SafeKelly)

            ' Calculate stake amounts
            result.StakeAmount = bankroll * result.SafeKelly
            result.ExpectedValue = CalculateExpectedValue(decimalOdds, winProbability)
            result.ExpectedGrowth = (
                CalculateExpectedGrowth(result.SafeKelly, decimalOdds, winProbability)
            )

            ' Risk metrics
            result.RiskOfRuin = (
                CalculateRiskOfRuin(result.SafeKelly, winProbability, 100) ' 100 bets
            )
            result.VolatilityScore = CalculateVolatility(decimalOdds, winProbability)

            ' Monetization hooks
            If result.ExpectedValue > 0.05 AndAlso result.StakeAmount > 10 Then
                LogHighValueOpportunity(result)
                SendPremiumAlert(result)
            End If

            Return result

        Catch ex As Exception
            Logger.Error($"Advanced Kelly calculation error: {{ex.Message}}")
            Return Nothing
        End Try
    End Function

    Private Shared Function CalculateStandardKelly(decimalOdds As Double, p As Double) As Double
        Dim b As Double = decimalOdds - 1.0
        Dim q As Double = 1.0 - p
        Return ((b * p) - q) / b
    End Function

    Private Shared Function CalculateFractionalKelly(
        decimalOdds As Double,
        p As Double,
        fraction As Double
    ) As Double
        Return CalculateStandardKelly(decimalOdds, p) * fraction
    End Function

    Private Shared Function CalculateAdaptiveKelly(
        decimalOdds As Double,
        p As Double,
        bankroll As Double
    ) As Double
        ' Adaptive Kelly based on bankroll size
        Dim baseKelly As Double = CalculateStandardKelly(decimalOdds, p)
        Dim adaptiveFactor As Double = (
            Math.Min(1.0, 10000.0 / bankroll) ' Reduce for larger bankrolls
        )
        Return baseKelly * adaptiveFactor
    End Function

    Private Shared Function CalculateExpectedValue(decimalOdds As Double, p As Double) As Double
        Return (p * (decimalOdds - 1)) - ((1 - p) * 1)
    End Function

    Private Shared Function CalculateExpectedGrowth(
        kellyFraction As Double,
        decimalOdds As Double,
        p As Double
    ) As Double
        ' Expected logarithmic growth rate
        Return p * Math.Log(1 + kellyFraction * (decimalOdds - 1)) + (1 - p) * Math.Log(1 - kellyFraction)
    End Function

    Private Shared Function CalculateRiskOfRuin(
        kellyFraction As Double,
        p As Double,
        numBets As Integer
    ) As Double
        ' Simplified risk of ruin calculation
        If kellyFraction <= 0 Then Return 0
        Dim drawdownRisk As Double = Math.Pow(1 - kellyFraction, numBets)
        Return Math.Max(0, Math.Min(1, drawdownRisk * (1 - p) / p))
    End Function

    Private Shared Function CalculateVolatility(decimalOdds As Double, p As Double) As Double
        ' Measure bet outcome volatility
        Dim winReturn As Double = decimalOdds - 1
        Dim lossReturn As Double = -1
        Dim expectedReturn As Double = p * winReturn + (1 - p) * lossReturn
        Dim variance As Double = (
            p * Math.Pow(winReturn - expectedReturn, 2) + (1 - p) * Math.Pow(lossReturn - expectedReturn, 2)
        )
        Return Math.Sqrt(variance)
    End Function

    Private Shared Function ConvertOddsToDecimal(odds As Double) As Double
        If odds > 100 Then
            ' American positive
            Return 1 + (odds / 100)
        ElseIf odds < -100 Then
            ' American negative
            Return 1 + (100 / Math.Abs(odds))
        Else
            ' Assume already decimal
            Return odds
        End If
    End Function

    ' ENHANCED MONETIZATION FEATURES
    Private Shared Sub LogHighValueOpportunity(result As EnhancedKellyResult)
        Try
            ' Log to BigQuery for analytics
            Dim logData As Object = New With {{
                .timestamp = result.Timestamp,
                .expected_value = result.ExpectedValue,
                .stake_amount = result.StakeAmount,
                .odds = result.Odds,
                .probability = result.WinProbability,
                .source_repo = result.SourceRepo,
                .source_languages = result.SourceLanguages
            }}

            BigQueryClient.LogKellyOpportunity(JsonConvert.SerializeObject(logData))

        Catch ex As Exception
            Logger.Error($"Kelly monetization logging failed: {{ex.Message}}")
        End Try
    End Sub

    Private Shared Sub SendPremiumAlert(result As EnhancedKellyResult)
        Try
            Dim message As String = $"💎 PREMIUM KELLY ALERT: {{result.ExpectedValue:P2}} edge, " &
                                  $"${{result.StakeAmount:F2}} optimal stake on {{result.Odds}} odds"

            ' Send to multiple channels
            Task.Run(Async Function()
                Await Alerts.SendTelegramAlertAsync(message)
                Await Alerts.SendDiscordAlertAsync(message)

                ' Create monetized tracking link
                Dim bitlyLink As String = Await BitlyHelper.CreateLinkAsync(
                    $"EQ12 Kelly Calculator found {{result.ExpectedValue:P2}} edge! Join premium for instant alerts.",
                    "kelly-premium-alert"
                )

                Logger.Info($"Premium Kelly alert sent with link: {{bitlyLink}}")
            End Function)

        Catch ex As Exception
            Logger.Error($"Premium alert failed: {{ex.Message}}")
        End Try
    End Sub

    ' API endpoint for external integration
    Public Shared Async Function CalculateKellyApiAsync(
        bankroll As Double,
        odds As Double,
        probability As Double,
        Optional fraction As Double = 0.5
    ) As Task(Of String)

        Dim result As EnhancedKellyResult = (
            CalculateOptimalStakeAdvanced(bankroll, odds, probability, fraction)
        )

        If result IsNot Nothing Then
            ' Track API usage for monetization
            ApiUsageTracker.LogKellyApiCall(result.SourceRepo, result.ExpectedValue)
            Return JsonConvert.SerializeObject(result)
        End If

        return '{"error":"Kelly calculation failed"}'
    End Function
End Class

Public Class EnhancedKellyResult
    Public Property Bankroll As Double
    Public Property Odds As Double
    Public Property WinProbability As Double
    Public Property Fraction As Double
    Public Property MaxRisk As Double
    Public Property Algorithm As String
    Public Property KellyFraction As Double
    Public Property SafeKelly As Double
    Public Property StakeAmount As Double
    Public Property ExpectedValue As Double
    Public Property ExpectedGrowth As Double
    Public Property RiskOfRuin As Double
    Public Property VolatilityScore As Double
    Public Property SourceRepo As String
    Public Property SourceLanguages As String
    Public Property Timestamp As DateTime
End Class
"""

        # Save enhanced module
        module_path = "C:\\\\EQ12\\visual_studio_projects\\\\EQ12SportsBettingTerminal\\Modules\\SuperKellyCalculator.vb"
        os.makedirs(os.path.dirname(module_path), exist_ok=True)

        with open(module_path, "w", encoding="utf-8") as f:
            f.write(template)

        self._log_vb_module_enhanced(
            "SuperKellyCalculator",
            repo_name,
            languages,
            "kelly",
            module_path,
            monetization_features,
            "generated",
        )

        logger.info(f"Generated Enhanced Kelly module: {module_path}")
        return module_path

    def _get_monetization_features(self, analysis: dict) -> str:
        """Get monetization features based on analysis"""
        features = []

        if analysis["monetization_potential"] >= 70:
            features.append("premium_alerts")
        if analysis["complexity_score"] >= 50:
            features.append("api_endpoints")
        if len(analysis["api_endpoints"]) > 0:
            features.append("webhook_integration")
        if analysis["integration_type"] in ["kelly", "arbitrage"]:
            features.append("automated_trading")

        return ", ".join(features) if features else "basic"

    def _log_search(self, query: str, category: str, language: str, result_count: int, status: str):
        """Enhanced search logging"""
        db_path = "C:\\\\EQ12\\\\data\\github_integration_enhanced.db"
        try:
            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO searches_enhanced (query, category, language, result_count, status)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (query, category, language, result_count, status),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log search: {e}")

    def _log_repo(self, repo_name: str, clone_path: str, status: str):
        """Enhanced repo logging"""
        db_path = "C:\\\\EQ12\\\\data\\github_integration_enhanced.db"
        try:
            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO repos_enhanced
                    (repo_full_name, clone_path, status)
                    VALUES (?, ?, ?)
                """,
                    (repo_name, clone_path, status),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log repo: {e}")

    def _log_vb_module_enhanced(
        self,
        module_name: str,
        source_repo: str,
        source_languages: str,
        integration_type: str,
        file_path: str,
        monetization_features: str,
        status: str,
    ):
        """Enhanced VB module logging"""
        db_path = "C:\\\\EQ12\\\\data\\github_integration_enhanced.db"
        try:
            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO vb_modules_enhanced
                    (module_name, source_repo, source_languages, integration_type,
                     file_path, monetization_features, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        module_name,
                        source_repo,
                        source_languages,
                        integration_type,
                        file_path,
                        monetization_features,
                        status,
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log VB module: {e}")

    def run_enhanced_integration(self, category: str = "all", max_repos: int = 15) -> dict:
        """
        Run enhanced integration workflow
        """
        logger.info(f"Starting Enhanced GitHub Integration for category: {category}")

        results = {
            "searched_repos": 0,
            "cloned_repos": 0,
            "generated_modules": 0,
            "total_languages": set(),
            "errors": [],
            "modules": [],
            "summary": {},
        }

        try:
            # Enhanced search
            logger.info("Enhanced Step 1: Multi-language GitHub search...")
            repos = self.search_repositories(category, max_repos * 2)  # Search more, filter better
            results["searched_repos"] = len(repos)

            logger.info(f"Found {len(repos)} repositories across multiple languages")

            # Process top repositories with enhanced analysis
            for repo in repos[:max_repos]:
                try:
                    repo_name = repo["full_name"]
                    repo_url = repo["clone_url"]

                    logger.info(f"Enhanced processing: {repo_name}")

                    # Clone with fallback methods
                    clone_path = self.clone_repository(repo_url, repo_name)
                    if not clone_path:
                        results["errors"].append(f"Failed to clone {repo_name}")
                        continue

                    results["cloned_repos"] += 1

                    # Enhanced analysis
                    analysis = self.analyze_repository(clone_path)
                    results["total_languages"].update(analysis["languages"].keys())

                    # Generate enhanced module for high-value repos
                    if analysis["monetization_potential"] >= 40:  # Lower threshold for more modules
                        module_path = self.generate_enhanced_vb_module(
                            clone_path, analysis, repo_name
                        )

                        if module_path:
                            results["generated_modules"] += 1
                            results["modules"].append(
                                {
                                    "repo": repo_name,
                                    "module_path": module_path,
                                    "integration_type": analysis["integration_type"],
                                    "monetization_score": analysis["monetization_potential"],
                                    "complexity_score": analysis["complexity_score"],
                                    "languages": list(analysis["languages"].keys()),
                                    "quality_indicators": analysis["quality_indicators"],
                                }
                            )
                        else:
                            results["errors"].append(
                                f"Failed to generate enhanced module for {repo_name}"
                            )
                    else:
                        logger.info(
                            f"Skipping low-value repository: {repo_name} "
                            f"(monetization score: {analysis['monetization_potential']})"
                        )

                except Exception as e:
                    error_msg = (
                        f"Enhanced processing error for {repo.get('full_name', 'unknown')}: {e}"
                    )
                    results["errors"].append(error_msg)
                    logger.error(error_msg)

            # Generate summary
            results["summary"] = {
                "languages_found": list(results["total_languages"]),
                "success_rate": f"{(results['generated_modules'] / max(results['cloned_repos'], 1)) * 100:.1f}%",
                "avg_complexity": sum([m["complexity_score"] for m in results["modules"]])
                / max(len(results["modules"]), 1),
                "avg_monetization": sum([m["monetization_score"] for m in results["modules"]])
                / max(len(results["modules"]), 1),
            }

            logger.info(
                f"Enhanced Integration Complete: {results['generated_modules']} enhanced modules generated"
            )

        except Exception as e:
            error_msg = f"Enhanced integration workflow error: {e}"
            results["errors"].append(error_msg)
            logger.error(error_msg)

        return results

    # Placeholder methods for modules not implemented in this example
    def _generate_enhanced_arbitrage_module(
        self, repo_path: str, analysis: dict, repo_name: str
    ) -> str:
        """Enhanced arbitrage module - placeholder for brevity"""
        return self._generate_enhanced_kelly_module(repo_path, analysis, repo_name)

    def _generate_enhanced_oddsapi_module(
        self, repo_path: str, analysis: dict, repo_name: str
    ) -> str:
        """Enhanced OddsAPI module - placeholder for brevity"""
        return self._generate_enhanced_kelly_module(repo_path, analysis, repo_name)

    def _generate_enhanced_utility_module(
        self, repo_path: str, analysis: dict, repo_name: str
    ) -> str:
        """Enhanced utility module - placeholder for brevity"""
        return self._generate_enhanced_kelly_module(repo_path, analysis, repo_name)


def main():
    """Enhanced main entry point"""
    parser = argparse.ArgumentParser(description="EQ12 Enhanced GitHub Repository Integrator")
    parser.add_argument(
        "--category",
        default="all",
        choices=["all", "arbitrage", "kelly", "oddsapi"],
        help="Category of repositories to search for",
    )
    parser.add_argument(
        "--max-repos",
        type=int,
        default=15,
        help="Maximum number of repositories to process",
    )
    parser.add_argument("--github-token", help="GitHub API token (or set GITHUB_TOKEN env var)")

    args = parser.parse_args()

    # Initialize enhanced integrator
    integrator = EnhancedGitHubIntegrator(args.github_token)

    # Run enhanced integration
    results = integrator.run_enhanced_integration(args.category, args.max_repos)

    # Enhanced results display
    print("\n" + "=" * 80)
    print("🚀 EQ12 ENHANCED GITHUB INTEGRATION RESULTS 🚀")
    print("=" * 80)
    print(f"📊 Searched repositories: {results['searched_repos']}")
    print(f"📥 Successfully cloned: {results['cloned_repos']}")
    print(f"⚡ Generated VB.NET modules: {results['generated_modules']}")
    print(f"🌐 Languages discovered: {', '.join(results['summary']['languages_found'])}")
    print(f"✅ Success rate: {results['summary']['success_rate']}")
    print(f"🔧 Avg complexity score: {results['summary']['avg_complexity']:.1f}")
    print(f"💰 Avg monetization score: {results['summary']['avg_monetization']:.1f}")

    if results["modules"]:
        print("\n🎯 Generated Enhanced Modules:")
        for module in results["modules"]:
            print(f"  • {module['repo']}")
            print(
                f"    Type: {module['integration_type']} | "
                f"Score: {module['monetization_score']} | "
                f"Languages: {', '.join(module['languages'])}"
            )
            print(f"    Path: {module['module_path']}")
            print()

    if results["errors"]:
        print("❌ Errors encountered:")
        for error in results["errors"][:5]:  # Show first 5 errors
            print(f"  • {error}")
        if len(results["errors"]) > 5:
            print(f"  ... and {len(results['errors']) - 5} more errors")

    print("=" * 80)


if __name__ == "__main__":
    main()
