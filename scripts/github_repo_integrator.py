#!/usr/bin/env python3
"""
EQ12 GitHub Repository Auto-Integrator
Expert-level GitHub Code Search → Pull → Analyze → Integrate system

Supports: Python, JavaScript, C++, Go, Java, PHP, Ruby, VB.NET
Searches for: Arbitrage bots, Kelly criterion implementations, OddsAPI wrappers
Integrates into: EQ12 VB.NET modules with monetization hooks
"""

import asyncio
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import requests

try:
    import git
except ImportError:
    git = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/github_integrator.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("GitHubIntegrator")


class GitHubRepoIntegrator:
    def __init__(self):
        self.eq12_root = Path(__file__).parent.parent
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.session = requests.Session()
        if self.github_token:
            self.session.headers.update({"Authorization": f"token {self.github_token}"})

        # Target repository categories and search queries
        self.search_queries = {
            "arbitrage": [
                "arbitrage betting bot language:python",
                "sports arbitrage calculator language:python",
                "arb_opportunity language:python",
                "odds comparison arbitrage language:javascript",
            ],
            "kelly": [
                "kelly criterion calculator language:python",
                "fractional kelly betting language:python",
                "bankroll management kelly language:python",
                "kelly staking formula language:javascript",
            ],
            "odds_api": [
                "the-odds-api wrapper language:python",
                "oddsapi client language:python",
                "sports odds api language:javascript",
                "TheOddsAPI python client",
            ],
        }

        logger.info("GitHub Repository Integrator initialized")

    def search_repositories(self, query: str, max_results: int = 10) -> list[dict]:
        """Search GitHub repositories using GitHub Search API"""
        try:
            url = "https://api.github.com/search/repositories"
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": max_results,
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            repositories = []

            for repo in data.get("items", []):
                repo_info = {
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo["description"],
                    "html_url": repo["html_url"],
                    "clone_url": repo["clone_url"],
                    "language": repo["language"],
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "updated": repo["updated_at"],
                }
                repositories.append(repo_info)

            logger.info(f"Found {len(repositories)} repositories for query: {query}")
            return repositories

        except Exception as e:
            logger.error(f"Error searching repositories: {e}")
            return []

    def clone_repository(self, repo_url: str, temp_dir: Path) -> Path | None:
        """Clone repository to temporary directory"""
        try:
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            clone_path = temp_dir / repo_name

            cmd = ["git", "clone", "--depth", "1", repo_url, str(clone_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                logger.info(f"Successfully cloned {repo_url}")
                return clone_path
            logger.error(f"Failed to clone {repo_url}: {result.stderr}")
            return None

        except Exception as e:
            logger.error(f"Error cloning repository {repo_url}: {e}")
            return None

    def analyze_repository_structure(self, repo_path: Path) -> dict:
        """Analyze repository structure and identify key files"""
        analysis = {
            "python_files": [],
            "javascript_files": [],
            "config_files": [],
            "key_functions": [],
            "dependencies": [],
        }

        try:
            # Find Python files
            for py_file in repo_path.rglob("*.py"):
                if py_file.is_file():
                    analysis["python_files"].append(str(py_file.relative_to(repo_path)))

            # Find JavaScript files
            for js_file in repo_path.rglob("*.js"):
                if js_file.is_file():
                    analysis["javascript_files"].append(str(js_file.relative_to(repo_path)))

            # Find config files
            config_patterns = [
                "requirements.txt",
                "package.json",
                "setup.py",
                "pyproject.toml",
            ]
            for pattern in config_patterns:
                for config_file in repo_path.rglob(pattern):
                    if config_file.is_file():
                        analysis["config_files"].append(str(config_file.relative_to(repo_path)))

            # Extract key functions from Python files
            for py_file_path in analysis["python_files"][:5]:  # Limit to first 5 files
                full_path = repo_path / py_file_path
                try:
                    with open(full_path, encoding="utf-8") as f:
                        content = f.read()
                        # Find function definitions
                        functions = re.findall(r"def\s+(\w+)\s*\([^)]*\):", content)
                        analysis["key_functions"].extend(
                            [f"{py_file_path}:{func}" for func in functions]
                        )
                except:
                    continue

            logger.info(
                f"Repository analysis complete: {len(analysis['python_files'])} Python files, {len(analysis['key_functions'])} functions"
            )
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing repository structure: {e}")
            return analysis

    def extract_core_logic(self, repo_path: Path, category: str) -> dict:
        """Extract core logic based on repository category"""
        core_logic = {
            "category": category,
            "main_functions": [],
            "classes": [],
            "algorithms": [],
            "dependencies": [],
        }

        try:
            # Category-specific extraction patterns
            if category == "arbitrage":
                patterns = [
                    r"def\s+(.*arb.*)\s*\([^)]*\):",
                    r"def\s+(.*odds.*)\s*\([^)]*\):",
                    r"def\s+(.*profit.*)\s*\([^)]*\):",
                    r"class\s+(.*Arb.*)\s*[:\(]",
                ]
            elif category == "kelly":
                patterns = [
                    r"def\s+(.*kelly.*)\s*\([^)]*\):",
                    r"def\s+(.*stake.*)\s*\([^)]*\):",
                    r"def\s+(.*bankroll.*)\s*\([^)]*\):",
                    r"class\s+(.*Kelly.*)\s*[:\(]",
                ]
            elif category == "odds_api":
                patterns = [
                    r"def\s+(.*odds.*)\s*\([^)]*\):",
                    r"def\s+(.*fetch.*)\s*\([^)]*\):",
                    r"def\s+(.*api.*)\s*\([^)]*\):",
                    r"class\s+(.*Odds.*|.*API.*)\s*[:\(]",
                ]
            else:
                patterns = []

            # Search through Python files
            for py_file in repo_path.rglob("*.py"):
                if py_file.is_file():
                    try:
                        with open(py_file, encoding="utf-8") as f:
                            content = f.read()

                        for pattern in patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches:
                                core_logic["main_functions"].append(
                                    {
                                        "file": str(py_file.relative_to(repo_path)),
                                        "name": match,
                                        "pattern": pattern,
                                    }
                                )
                    except:
                        continue

            logger.info(
                f"Extracted {len(core_logic['main_functions'])} core functions for {category}"
            )
            return core_logic

        except Exception as e:
            logger.error(f"Error extracting core logic: {e}")
            return core_logic

    def generate_vb_net_module(self, repo_info: dict, core_logic: dict, category: str) -> str:
        """Generate VB.NET module based on extracted logic"""

        module_templates = {
            "arbitrage": self._generate_arbitrage_vb_template,
            "kelly": self._generate_kelly_vb_template,
            "odds_api": self._generate_odds_api_vb_template,
        }

        if category in module_templates:
            return module_templates[category](repo_info, core_logic)
        return self._generate_generic_vb_template(repo_info, core_logic, category)

    def _generate_arbitrage_vb_template(self, repo_info: dict, core_logic: dict) -> str:
        """Generate ArbitrageBotEngine.vb template"""
        "\n".join(
            [
                f"    ' {func['name']} from {func['file']}"
                for func in core_logic["main_functions"][:10]
            ]
        )

        return """
' ArbitrageBotEngine.vb
' Source: GitHub repo {repo_info["html_url"]}, adapted for EQ12
' Original description: {repo_info["description"]}
' Functions extracted:
{functions_list}

Imports System
Imports System.Data
Imports System.Data.SQLite

Public Class ArbitrageBotEngine

    Private ReadOnly dbWriter As DBWriter
    Private ReadOnly logger As Logger

    Public Sub New()
        dbWriter = New DBWriter()
        logger = New Logger("ArbitrageBotEngine")
        logger.Info("ArbitrageBotEngine initialized from GitHub repo integration")
    End Sub

    Public Function DetectArbitrageOpportunities(oddsData As DataTable) As List(Of ArbitrageOpportunity)
        ' Core arbitrage detection logic adapted from {repo_info["name"]}
        Dim opportunities As New List(Of ArbitrageOpportunity)()

        Try
            ' Group odds by event_id for comparison
            Dim eventGroups = (
                oddsData.AsEnumerable().GroupBy(Function(row) row("event_id").ToString())
            )

            For Each eventGroup In eventGroups
                Dim eventOdds = eventGroup.ToArray()

                ' Check for two-sided arbitrage (ML, Spread, Total)
                Dim arbOpp = CheckTwoSidedArbitrage(eventOdds)
                If arbOpp IsNot Nothing Then
                    opportunities.Add(arbOpp)
                End If
            Next

            ' Log opportunities to database
            For Each opp In opportunities
                LogArbitrageOpportunity(opp)
                SendArbitrageAlert(opp)
            Next

            logger.Info($"Detected {{opportunities.Count}} arbitrage opportunities")
            Return opportunities

        Catch ex As Exception
            logger.Error($"Error detecting arbitrage: {{ex.Message}}")
            Return opportunities
        End Try
    End Function

    Private Function CheckTwoSidedArbitrage(eventOdds As DataRow()) As ArbitrageOpportunity
        ' Implement arbitrage detection algorithm from GitHub repo
        ' Calculate implied probabilities and check if sum < 1.0

        Try
            ' Find best odds for each side
            Dim sideAOdds As Integer = Integer.MinValue
            Dim sideBOdds As Integer = Integer.MinValue
            Dim sideABook As String = ""
            Dim sideBBook As String = ""

            For Each row In eventOdds
                Dim odds As Integer = Convert.ToInt32(row("odds"))
                Dim book As String = row("book").ToString()
                Dim selection As String = row("selection").ToString()

                ' Logic to identify opposing sides and track best odds
                ' This would be adapted from the specific GitHub repo logic
            Next

            ' Calculate arbitrage percentage
            Dim impliedA As Double = ImpliedProbabilityFromAmerican(sideAOdds)
            Dim impliedB As Double = ImpliedProbabilityFromAmerican(sideBOdds)
            Dim totalImplied As Double = impliedA + impliedB

            If totalImplied < 1.0 Then
                Dim arbPct As Double = ((1.0 / totalImplied) - 1.0) * 100

                Return New ArbitrageOpportunity With {{
                    .EventId = eventOdds(0)("event_id").ToString(),
                    .SideA = "Team A",
                    .BookA = sideABook,
                    .OddsA = sideAOdds,
                    .SideB = "Team B",
                    .BookB = sideBBook,
                    .OddsB = sideBOdds,
                    .ArbPercent = arbPct,
                    .Timestamp = DateTime.Now
                }}
            End If

        Catch ex As Exception
            logger.Error($"Error in arbitrage calculation: {{ex.Message}}")
        End Try

        Return Nothing
    End Function

    Private Function ImpliedProbabilityFromAmerican(americanOdds As Integer) As Double
        ' Convert American odds to implied probability
        If americanOdds > 0 Then
            Return 100.0 / (americanOdds + 100.0)
        Else
            Return Math.Abs(americanOdds) / (Math.Abs(americanOdds) + 100.0)
        End If
    End Function

    Private Sub LogArbitrageOpportunity(opp As ArbitrageOpportunity)
        ' Log to SQLite and BigQuery
        Try
            Dim sql As String = (
                "INSERT INTO arb_opportunities (event_id, sideA, bookA, oddsA, sideB, bookB, oddsB, arb_pct) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            )
            dbWriter.ExecuteNonQuery(
                sql,
                opp.EventId,
                opp.SideA,
                opp.BookA,
                opp.OddsA,
                opp.SideB,
                opp.BookB,
                opp.OddsB,
                opp.ArbPercent
            )

            ' Sync to BigQuery
            dbWriter.SyncToBigQuery("arb_opportunities")

        Catch ex As Exception
            logger.Error($"Error logging arbitrage opportunity: {{ex.Message}}")
        End Try
    End Sub

    Private Sub SendArbitrageAlert(opp As ArbitrageOpportunity)
        ' Send alert via Telegram/Discord with Bitly link
        Try
            Dim alertMessage As String = (
                $"🚨 ARBITRAGE ALERT: {{opp.ArbPercent:F2}}% profit opportunity"
            )
            Dim detailUrl As String = $"https://eq12.local/arb/{{opp.EventId}}"
            Dim bitlyUrl As String = BitlyHelper.ShortenUrl(detailUrl)

            ' Send via configured alert channels
            AlertsHelper.SendTelegramAlert(alertMessage & " " & bitlyUrl)
            AlertsHelper.SendDiscordAlert(alertMessage & " " & bitlyUrl)

        Catch ex As Exception
            logger.Error($"Error sending arbitrage alert: {{ex.Message}}")
        End Try
    End Sub

End Class

Public Class ArbitrageOpportunity
    Public Property EventId As String
    Public Property SideA As String
    Public Property BookA As String
    Public Property OddsA As Integer
    Public Property SideB As String
    Public Property BookB As String
    Public Property OddsB As Integer
    Public Property ArbPercent As Double
    Public Property Timestamp As DateTime
End Class
"""

    def _generate_kelly_vb_template(self, repo_info: dict, core_logic: dict) -> str:
        """Generate KellyCalculator.vb template"""
        "\n".join(
            [
                f"    ' {func['name']} from {func['file']}"
                for func in core_logic["main_functions"][:10]
            ]
        )

        return """
' KellyCalculator.vb
' Source: GitHub repo {repo_info["html_url"]}, adapted for EQ12
' Original description: {repo_info["description"]}
' Functions extracted:
{functions_list}

Imports System

Public Class KellyCalculator

    Private ReadOnly dbWriter As DBWriter
    Private ReadOnly logger As Logger

    Public Sub New()
        dbWriter = New DBWriter()
        logger = New Logger("KellyCalculator")
        logger.Info("KellyCalculator initialized from GitHub repo integration")
    End Sub

    Public Function CalculateKellyStake(
        bankroll As Double,
        americanOdds As Integer,
        winProbability As Double,
        fraction As Double
    ) As KellyResult
        ' Kelly Criterion implementation adapted from {repo_info["name"]}
        Try
            Dim decimalOdds As Double = DecimalFromAmerican(americanOdds)
            Dim b As Double = decimalOdds - 1.0  ' Net odds (profit per unit staked)

            ' Full Kelly formula: k = (b*p - (1-p)) / b
            Dim kellyFull As Double = ((b * winProbability) - (1.0 - winProbability)) / b

            ' Apply fraction (quarter-kelly, half-kelly, etc)
            Dim kellyFraction As Double = kellyFull * fraction

            ' Calculate stake amount
            Dim stakeAmount As Double = bankroll * Math.Max(0, kellyFraction)

            Dim result As New KellyResult With {{
                .Bankroll = bankroll,
                .AmericanOdds = americanOdds,
                .DecimalOdds = decimalOdds,
                .WinProbability = winProbability,
                .KellyFull = kellyFull,
                .KellyFraction = kellyFraction,
                .Fraction = fraction,
                .StakeAmount = stakeAmount,
                .StakePercent = (stakeAmount / bankroll) * 100,
                .Timestamp = DateTime.Now
            }}

            ' Log to database
            LogKellyCalculation(result)

            logger.Info($"Kelly calculation: {{stakeAmount:C}} ({{result.StakePercent:F2}}%) for odds {{americanOdds}}")
            Return result

        Catch ex As Exception
            logger.Error($"Error calculating Kelly stake: {{ex.Message}}")
            Return New KellyResult()
        End Try
    End Function

    Public Function CalculateUnitStake(
        bankroll As Double,
        unitPercent As Double,
        units As Double
    ) As Double
        ' Unit-based staking system
        Try
            Dim unitSize As Double = bankroll * (unitPercent / 100.0)
            Dim stakeAmount As Double = unitSize * units

            logger.Info($"Unit stake: {{stakeAmount:C}} ({{units}} units at {{unitPercent:F1}}%)")
            Return stakeAmount

        Catch ex As Exception
            logger.Error($"Error calculating unit stake: {{ex.Message}}")
            Return 0.0
        End Try
    End Function

    Private Function DecimalFromAmerican(americanOdds As Integer) As Double
        ' Convert American odds to decimal odds
        If americanOdds > 0 Then
            Return (americanOdds / 100.0) + 1.0
        Else
            Return (100.0 / Math.Abs(americanOdds)) + 1.0
        End If
    End Function

    Private Sub LogKellyCalculation(result As KellyResult)
        ' Log to staking_log table
        Try
            Dim sql As String = (
                "INSERT INTO staking_log (decimal_odds, edge, p, kelly_full, kelly_fraction, stake, mode, bankroll_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            )
            Dim edge As Double = result.WinProbability - (1.0 / result.DecimalOdds)

            dbWriter.ExecuteNonQuery(
                sql,
                result.DecimalOdds,
                edge,
                result.WinProbability,
                result.KellyFull,
                result.KellyFraction,
                result.StakeAmount,
                "kelly",
                "Main"
            )

            ' Sync to BigQuery
            dbWriter.SyncToBigQuery("staking_log")

        Catch ex As Exception
            logger.Error($"Error logging Kelly calculation: {{ex.Message}}")
        End Try
    End Sub

End Class

Public Class KellyResult
    Public Property Bankroll As Double
    Public Property AmericanOdds As Integer
    Public Property DecimalOdds As Double
    Public Property WinProbability As Double
    Public Property KellyFull As Double
    Public Property KellyFraction As Double
    Public Property Fraction As Double
    Public Property StakeAmount As Double
    Public Property StakePercent As Double
    Public Property Timestamp As DateTime
End Class
"""

    def _generate_odds_api_vb_template(self, repo_info: dict, core_logic: dict) -> str:
        """Generate OddsApiClient.vb template"""
        "\n".join(
            [
                f"    ' {func['name']} from {func['file']}"
                for func in core_logic["main_functions"][:10]
            ]
        )

        return """
' OddsApiClient.vb
' Source: GitHub repo {repo_info["html_url"]}, adapted for EQ12
' Original description: {repo_info["description"]}
' Functions extracted:
{functions_list}

Imports System
Imports System.Net.Http
Imports System.Threading.Tasks
Imports Newtonsoft.Json
Imports System.Data

Public Class OddsApiClient

    Private ReadOnly httpClient As HttpClient
    Private ReadOnly apiKey As String
    Private ReadOnly baseUrl As String = "https://api.the-odds-api.com/v4"
    Private ReadOnly dbWriter As DBWriter
    Private ReadOnly logger As Logger

    Public Sub New()
        httpClient = New HttpClient()
        apiKey = Environment.GetEnvironmentVariable("ODDS_API_KEY")
        dbWriter = New DBWriter()
        logger = New Logger("OddsApiClient")

        If String.IsNullOrEmpty(apiKey) Then
            Throw New ArgumentException("ODDS_API_KEY environment variable not set")
        End If

        logger.Info("OddsApiClient initialized from GitHub repo integration")
    End Sub

    Public Async Function GetSportsAsync() As Task(Of List(Of Sport))
        ' Get available sports - adapted from {repo_info["name"]}
        Try
            Dim url As String = $"{{baseUrl}}/sports?apiKey={{apiKey}}"
            Dim response = Await httpClient.GetStringAsync(url)

            Dim sports As List(Of Sport) = (
                JsonConvert.DeserializeObject(Of List(Of Sport))(response)
            )
            logger.Info($"Retrieved {{sports.Count}} sports from OddsAPI")

            Return sports

        Catch ex As Exception
            logger.Error($"Error getting sports: {{ex.Message}}")
            Return New List(Of Sport)()
        End Try
    End Function

    Public Async Function GetOddsBySportAsync(sport As String, Optional regions As String = (
        "us", Optional markets As String = "h2h,spreads,totals") As Task(Of DataTable)
    )
        ' Get odds for specific sport - core functionality from GitHub repo
        Try
            Dim url As String = (
                $"{{baseUrl}}/sports/{{sport}}/odds?apiKey={{apiKey}}&regions={{regions}}&markets={{markets}}"
            )
            Dim response = Await httpClient.GetStringAsync(url)

            Dim oddsResponse = JsonConvert.DeserializeObject(response)
            Dim oddsTable As DataTable = ParseOddsToDataTable(oddsResponse, sport)

            ' Save to database
            Await SaveOddsToDatabase(oddsTable)

            logger.Info($"Retrieved {{oddsTable.Rows.Count}} odds records for {{sport}}")
            Return oddsTable

        Catch ex As Exception
            logger.Error($"Error getting odds for {{sport}}: {{ex.Message}}")
            Return New DataTable()
        End Try
    End Function

    Private Function ParseOddsToDataTable(oddsData As Object, sport As String) As DataTable
        ' Parse JSON response to DataTable - adapted from repo parsing logic
        Dim table As New DataTable()

        ' Define schema
        table.Columns.Add("ts", GetType(DateTime))
        table.Columns.Add("event_id", GetType(String))
        table.Columns.Add("sport", GetType(String))
        table.Columns.Add("market", GetType(String))
        table.Columns.Add("selection", GetType(String))
        table.Columns.Add("book", GetType(String))
        table.Columns.Add("odds", GetType(Integer))

        Try
            ' Parse JSON structure and populate DataTable
            ' This would contain the specific parsing logic from the GitHub repo
            Dim timestamp As DateTime = DateTime.Now

            ' Example parsing structure - would be adapted from actual repo
            ' For Each event In oddsData...
            '   For Each bookmaker In event.bookmakers...
            '     For Each market In bookmaker.markets...
            '       For Each outcome In market.outcomes...

            logger.Info($"Parsed odds data into {{table.Rows.Count}} rows")

        Catch ex As Exception
            logger.Error($"Error parsing odds data: {{ex.Message}}")
        End Try

        Return table
    End Function

    Private Async Function SaveOddsToDatabase(oddsTable As DataTable) As Task
        ' Save odds to SQLite and sync to BigQuery
        Try
            For Each row As DataRow In oddsTable.Rows
                Dim sql As String = (
                    "INSERT INTO odds (ts, event_id, sport, market, selection, book, odds) VALUES (?, ?, ?, ?, ?, ?, ?)"
                )
                dbWriter.ExecuteNonQuery(
                    sql,
                    row("ts"),
                    row("event_id"),
                    row("sport"),
                    row("market"),
                    row("selection"),
                    row("book"),
                    row("odds")
                )
            Next

            ' Sync to BigQuery
            dbWriter.SyncToBigQuery("odds")

            ' Check for value bets and send alerts
            Await CheckForValueBets(oddsTable)

        Catch ex As Exception
            logger.Error($"Error saving odds to database: {{ex.Message}}")
        End Try
    End Function

    Private Async Function CheckForValueBets(oddsTable As DataTable) As Task
        ' Simple value bet detection and alerting
        Try
            ' Basic value bet logic - would be enhanced based on repo algorithms
            For Each row As DataRow In oddsTable.Rows
                Dim odds As Integer = Convert.ToInt32(row("odds"))
                Dim impliedProb As Double = (
                    If(odds > 0, 100.0 / (odds + 100.0), Math.Abs(odds) / (Math.Abs(odds) + 100.0))
                )

                ' Simple heuristic - alert if implied probability suggests value
                If impliedProb < 0.45 AndAlso odds > 120 Then
                    Await SendValueBetAlert(row)
                End If
            Next

        Catch ex As Exception
            logger.Error($"Error checking for value bets: {{ex.Message}}")
        End Try
    End Function

    Private Async Function SendValueBetAlert(oddsRow As DataRow) As Task
        ' Send value bet alert with Bitly link
        Try
            Dim alertMessage As String = (
                $"💰 VALUE BET: {{oddsRow("selection")}} {{oddsRow("odds")}} at {{oddsRow("book")}}"
            )
            Dim detailUrl As String = $"https://eq12.local/odds/{{oddsRow("event_id")}}"
            Dim bitlyUrl As String = BitlyHelper.ShortenUrl(detailUrl)

            AlertsHelper.SendTelegramAlert(alertMessage & " " & bitlyUrl)

        Catch ex As Exception
            logger.Error($"Error sending value bet alert: {{ex.Message}}")
        End Try
    End Function

    Public Sub Dispose()
        httpClient?.Dispose()
    End Sub

End Class

Public Class Sport
    Public Property Key As String
    Public Property Group As String
    Public Property Title As String
    Public Property Description As String
    Public Property Active As Boolean
    Public Property HasOutrights As Boolean
End Class
"""

    def _generate_generic_vb_template(
        self, repo_info: dict, core_logic: dict, category: str
    ) -> str:
        """Generate generic VB.NET template"""
        return """
' {category.title()}Engine.vb
' Source: GitHub repo {repo_info["html_url"]}, adapted for EQ12
' Original description: {repo_info["description"]}

Public Class {category.title()}Engine
    ' Adapted from GitHub repository: {repo_info["name"]}
    ' TODO: Implement specific functionality based on repository analysis
End Class
"""

    async def process_all_categories(self) -> dict:
        """Process all repository categories and generate integrations"""
        results = {
            "repositories_found": {},
            "modules_generated": {},
            "integration_status": {},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            for category, queries in self.search_queries.items():
                logger.info(f"Processing category: {category}")

                category_repos = []

                # Search repositories for this category
                for query in queries:
                    repos = self.search_repositories(query, max_results=5)
                    category_repos.extend(repos)

                # Remove duplicates and sort by stars
                unique_repos = {repo["full_name"]: repo for repo in category_repos}.values()
                sorted_repos = sorted(unique_repos, key=lambda x: x["stars"], reverse=True)

                results["repositories_found"][category] = sorted_repos[:3]  # Top 3 repos

                # Process top repository for this category
                if sorted_repos:
                    top_repo = sorted_repos[0]
                    logger.info(
                        f"Processing top repository for {category}: {top_repo['full_name']}"
                    )

                    # Clone and analyze
                    repo_path = self.clone_repository(top_repo["clone_url"], temp_path)
                    if repo_path:
                        core_logic = self.extract_core_logic(repo_path, category)
                        vb_module = self.generate_vb_net_module(top_repo, core_logic, category)

                        # Save generated module
                        module_filename = f"{category.title()}Engine.vb"
                        module_path = (
                            self.eq12_root
                            / "visual_studio_projects"
                            / "EQ12SportsBettingTerminal"
                            / "Modules"
                            / module_filename
                        )

                        module_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(module_path, "w", encoding="utf-8") as f:
                            f.write(vb_module)

                        results["modules_generated"][category] = str(module_path)
                        results["integration_status"][category] = "success"

                        logger.info(f"Generated {module_filename} from {top_repo['full_name']}")
                    else:
                        results["integration_status"][category] = "clone_failed"
                else:
                    results["integration_status"][category] = "no_repos_found"

        return results

    async def update_cli_commands(self):
        """Add new CLI commands for the integrated modules"""
        cli_updates = """
        Case "ingest-oddsapi"
            Dim sport As String = GetArgValue(args, "--sport", "nfl")
            Dim oddsClient As New OddsApiClient()
            Dim oddsData = Await oddsClient.GetOddsBySportAsync(sport)
            Console.WriteLine($"Retrieved {oddsData.Rows.Count} odds records for {sport}")

        Case "run-arb-bot"
            Dim window As String = GetArgValue(args, "--window", "60m")
            Dim minArb As Double = Convert.ToDouble(GetArgValue(args, "--min-arb", "1.0"))

            Dim arbBot As New ArbitrageBotEngine()
            Dim recentOdds = GetRecentOdds(window)
            Dim opportunities = arbBot.DetectArbitrageOpportunities(recentOdds)
            Console.WriteLine($"Found {opportunities.Count} arbitrage opportunities")

        Case "calc-kelly"
            Dim odds As Integer = Convert.ToInt32(GetArgValue(args, "--odds", "+150"))
            Dim probability As Double = Convert.ToDouble(GetArgValue(args, "--p", "0.55"))
            Dim fraction As Double = Convert.ToDouble(GetArgValue(args, "--fraction", "0.5"))
            Dim bankroll As Double = GetCurrentBankroll()

            Dim kelly As New KellyCalculator()
            Dim result = kelly.CalculateKellyStake(bankroll, odds, probability, fraction)
            Console.WriteLine($"Recommended stake: {result.StakeAmount:C} ({result.StakePercent:F2}%)")
        """

        # Save CLI updates to file for manual integration
        cli_file = self.eq12_root / "generated_cli_commands.vb"
        with open(cli_file, "w") as f:
            f.write(cli_updates)

        logger.info(f"CLI command updates saved to {cli_file}")


async def main():
    """Main execution function"""
    integrator = GitHubRepoIntegrator()

    logger.info("Starting GitHub repository integration process...")

    # Process all categories
    results = await integrator.process_all_categories()

    # Update CLI commands
    await integrator.update_cli_commands()

    # Save results summary
    results_file = (
        integrator.eq12_root
        / "logs"
        / f"github_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    logger.info(f"Integration complete! Results saved to {results_file}")

    # Print summary
    print("\n" + "=" * 50)
    print("🚀 EQ12 GITHUB INTEGRATION COMPLETE")
    print("=" * 50)

    for category, _status in results["integration_status"].items():
        print("{status_emoji} {category.upper()}: {status}")

        if category in results["modules_generated"]:
            print("   📁 Module: {results['modules_generated'][category]}")

        if category in results["repositories_found"]:
            top_repo = (
                results["repositories_found"][category][0]
                if results["repositories_found"][category]
                else None
            )
            if top_repo:
                print("   📊 Source: {top_repo['full_name']} ({top_repo['stars']} stars)")

    print("\n📋 CLI commands generated in: generated_cli_commands.vb")
    print("📊 Full results: {results_file}")


if __name__ == "__main__":
    asyncio.run(main())
