#!/usr/bin/env python3
"""
EQ12 Comprehensive Integration Validation Script
Validates Google Blogger, Scheduled Exports, Log Management, and Google Alerts integration
Tests all new VB.NET modules, database schema, CLI commands, and workflow integration
"""

import json
import sys
from datetime import datetime
from pathlib import Path


class EQ12IntegrationValidator:
    def __init__(self):
        self.base_path = Path("c:/EQ12/visual_studio_projects/EQ12SportsBettingTerminal")
        self.config_path = self.base_path / "Config/config.json"
        self.db_path = self.base_path / "Data/eq12_terminal.db"
        self.schema_path = self.base_path / "Data/schema.sql"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "details": [],
        }

    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        self.results["tests_run"] += 1
        if passed:
            self.results["tests_passed"] += 1
            status = "✅ PASS"
        else:
            self.results["tests_failed"] += 1
            status = "❌ FAIL"

        self.results["details"].append({"test": test_name, "status": status, "details": details})
        print(f"{status}: {test_name}")
        if details:
            print(f"    {details}")

    def test_vb_module_structure(self):
        """Test that all VB.NET modules exist and have correct structure"""
        print("\n🔍 Testing VB.NET Module Structure...")

        modules = [
            ("BloggerHelper.vb", ["PublishPost", "LogPost", "ConvertReportToBlog"]),
            (
                "ScheduledExportsHelper.vb",
                [
                    "ExecuteDailyExport",
                    "ExecuteWeeklyExport",
                    "InitializeScheduledExports",
                ],
            ),
            ("LogManagerHelper.vb", ["AnalyzeLogs", "CleanupLogs", "ArchiveLogs"]),
            ("GoogleAlertsHelper.vb", ["FetchAlertsRSS", "LogAlert", "GetAlertsStats"]),
        ]

        for module_name, required_functions in modules:
            module_path = self.base_path / f"Modules/{module_name}"

            if not module_path.exists():
                self.log_test(
                    f"VB Module {module_name} exists",
                    False,
                    f"File not found: {module_path}",
                )
                continue

            # Read module content
            try:
                with open(module_path, encoding="utf-8") as f:
                    content = f.read()

                # Check for required functions
                missing_functions = []
                for func in required_functions:
                    if f"Function {func}" not in content and f"Sub {func}" not in content:
                        missing_functions.append(func)

                if missing_functions:
                    self.log_test(
                        f"VB Module {module_name} has required functions",
                        False,
                        f"Missing functions: {', '.join(missing_functions)}",
                    )
                else:
                    self.log_test(
                        f"VB Module {module_name} structure",
                        True,
                        f"All {len(required_functions)} required functions found",
                    )

            except Exception as e:
                self.log_test(
                    f"VB Module {module_name} readable",
                    False,
                    f"Error reading file: {e}",
                )

    def test_database_schema(self):
        """Test database schema includes all new tables"""
        print("\n🗄️ Testing Database Schema...")

        required_tables = [
            ("blogger_posts", ["post_id", "title", "bitly_url", "status"]),
            (
                "scheduled_exports",
                ["export_type", "deliverable_count", "export_path", "success"],
            ),
            (
                "log_analysis",
                [
                    "analysis_type",
                    "total_errors",
                    "performance_score",
                    "security_score",
                ],
            ),
            ("log_cleanup", ["files_deleted", "files_archived", "size_freed_mb"]),
            (
                "google_alerts_log",
                ["keyword", "title", "link", "summary", "monetization_score"],
            ),
        ]

        if not self.schema_path.exists():
            self.log_test(
                "Schema file exists",
                False,
                f"Schema file not found: {self.schema_path}",
            )
            return

        try:
            with open(self.schema_path, encoding="utf-8") as f:
                schema_content = f.read()

            for table_name, required_columns in required_tables:
                # Check table creation
                table_found = f"CREATE TABLE IF NOT EXISTS {table_name}" in schema_content

                if not table_found:
                    self.log_test(
                        f"Database table {table_name}",
                        False,
                        "Table creation statement not found",
                    )
                    continue

                # Check required columns
                missing_columns = []
                for column in required_columns:
                    if (
                        column
                        not in schema_content[
                            schema_content.find(table_name) : schema_content.find(
                                ");", schema_content.find(table_name)
                            )
                        ]
                    ):
                        missing_columns.append(column)

                if missing_columns:
                    self.log_test(
                        f"Database table {table_name} columns",
                        False,
                        f"Missing columns: {', '.join(missing_columns)}",
                    )
                else:
                    self.log_test(
                        f"Database table {table_name} structure",
                        True,
                        f"All {len(required_columns)} required columns found",
                    )

        except Exception as e:
            self.log_test("Database schema validation", False, f"Error reading schema: {e}")

    def test_configuration_extensions(self):
        """Test config.json has all new sections"""
        print("\n⚙️ Testing Configuration Extensions...")

        if not self.config_path.exists():
            self.log_test(
                "Config file exists",
                False,
                f"Config file not found: {self.config_path}",
            )
            return

        try:
            with open(self.config_path, encoding="utf-8") as f:
                config = json.load(f)

            required_sections = [
                ("blogger", ["enabled", "api_key", "blog_id", "auto_publish_daily"]),
                (
                    "scheduled_exports",
                    ["enabled", "daily", "weekly", "export_directory"],
                ),
                (
                    "log_manager",
                    ["enabled", "retention_days", "archive_directory", "auto_cleanup"],
                ),
                (
                    "google_alerts",
                    ["enabled", "rss_url", "keywords", "auto_generate_content"],
                ),
            ]

            for section_name, required_keys in required_sections:
                if section_name not in config:
                    self.log_test(
                        f"Config section {section_name}",
                        False,
                        "Section not found in config",
                    )
                    continue

                section = config[section_name]
                missing_keys = []
                for key in required_keys:
                    if key not in section:
                        missing_keys.append(key)

                if missing_keys:
                    self.log_test(
                        f"Config section {section_name} keys",
                        False,
                        f"Missing keys: {', '.join(missing_keys)}",
                    )
                else:
                    self.log_test(
                        f"Config section {section_name} structure",
                        True,
                        f"All {len(required_keys)} required keys found",
                    )

        except json.JSONDecodeError as e:
            self.log_test("Config JSON validity", False, f"Invalid JSON: {e}")
        except Exception as e:
            self.log_test("Config file validation", False, f"Error reading config: {e}")

    def test_cli_integration(self):
        """Test CLI commands integration"""
        print("\n💻 Testing CLI Command Integration...")

        cli_path = self.base_path / "Eq12Cli.vb"

        if not cli_path.exists():
            self.log_test("CLI file exists", False, f"CLI file not found: {cli_path}")
            return

        try:
            with open(cli_path, encoding="utf-8") as f:
                cli_content = f.read()

            # Test for new commands in Case statement
            new_commands = [
                'Case "publish-blog"',
                'Case "schedule-export"',
                'Case "manage-logs"',
                'Case "fetch-alerts"',
            ]

            for command in new_commands:
                if command in cli_content:
                    self.log_test(
                        f"CLI command {command.split('"')[1]}",
                        True,
                        "Command case found",
                    )
                else:
                    self.log_test(
                        f"CLI command {command.split('"')[1]}",
                        False,
                        "Command case not found",
                    )

            # Test for command implementations
            command_functions = [
                "Sub PublishBlog",
                "Sub ScheduleExport",
                "Sub ManageLogs",
                "Sub FetchAlerts",
            ]

            for func in command_functions:
                if func in cli_content:
                    self.log_test(f"CLI function {func.split()[1]}", True, "Implementation found")
                else:
                    self.log_test(
                        f"CLI function {func.split()[1]}",
                        False,
                        "Implementation not found",
                    )

        except Exception as e:
            self.log_test("CLI integration validation", False, f"Error reading CLI file: {e}")

    def test_content_engine_integration(self):
        """Test ContentEngine integration with new systems"""
        print("\n🎯 Testing ContentEngine Integration...")

        content_engine_path = self.base_path / "Modules/ContentEngine.vb"

        if not content_engine_path.exists():
            self.log_test(
                "ContentEngine file exists",
                False,
                f"ContentEngine not found: {content_engine_path}",
            )
            return

        try:
            with open(content_engine_path, encoding="utf-8") as f:
                content = f.read()

            # Test for integration hooks
            integration_features = [
                (
                    "IntegrateMonetizationSystems",
                    "Monetization systems integration function",
                ),
                ("BloggerHelper.PublishPost", "Blogger integration"),
                ("GoogleAlertsHelper.FetchAlertsRSS", "Google Alerts integration"),
                (
                    "ScheduledExportsHelper.ExecuteDailyExport",
                    "Scheduled exports integration",
                ),
                ("EnrichContentWithAlerts", "Alert-based content enrichment"),
            ]

            for feature, description in integration_features:
                if feature in content:
                    self.log_test(f"ContentEngine {description}", True, "Integration code found")
                else:
                    self.log_test(
                        f"ContentEngine {description}",
                        False,
                        "Integration code not found",
                    )

        except Exception as e:
            self.log_test(
                "ContentEngine integration validation",
                False,
                f"Error reading ContentEngine: {e}",
            )

    def test_monetization_workflow(self):
        """Test end-to-end monetization workflow"""
        print("\n💰 Testing Monetization Workflow Integration...")

        # Test workflow components
        workflow_tests = [
            ("Blogger API config", self.has_blogger_config),
            ("Scheduled export config", self.has_scheduled_export_config),
            ("Google Alerts config", self.has_google_alerts_config),
            ("Log management config", self.has_log_manager_config),
        ]

        for test_name, test_func in workflow_tests:
            try:
                result = test_func()
                self.log_test(
                    test_name,
                    result,
                    "Configuration validated" if result else "Configuration incomplete",
                )
            except Exception as e:
                self.log_test(test_name, False, f"Test error: {e}")

    def has_blogger_config(self):
        """Check if Blogger is properly configured"""
        try:
            with open(self.config_path, encoding="utf-8") as f:
                config = json.load(f)

            blogger = config.get("blogger", {})
            return blogger.get("enabled") and "api_key" in blogger and "blog_id" in blogger
        except:
            return False

    def has_scheduled_export_config(self):
        """Check if scheduled exports are properly configured"""
        try:
            with open(self.config_path, encoding="utf-8") as f:
                config = json.load(f)

            exports = config.get("scheduled_exports", {})
            return exports.get("enabled") and "daily" in exports and "weekly" in exports
        except:
            return False

    def has_google_alerts_config(self):
        """Check if Google Alerts are properly configured"""
        try:
            with open(self.config_path, encoding="utf-8") as f:
                config = json.load(f)

            alerts = config.get("google_alerts", {})
            return alerts.get("enabled") and "rss_url" in alerts and "keywords" in alerts
        except:
            return False

    def has_log_manager_config(self):
        """Check if log manager is properly configured"""
        try:
            with open(self.config_path, encoding="utf-8") as f:
                config = json.load(f)

            log_mgr = config.get("log_manager", {})
            return (
                log_mgr.get("enabled")
                and "retention_days" in log_mgr
                and "archive_directory" in log_mgr
            )
        except:
            return False

    def generate_summary_report(self):
        """Generate final validation report"""
        print("\n" + "=" * 60)
        print("🎯 EQ12 COMPREHENSIVE INTEGRATION VALIDATION REPORT")
        print("=" * 60)
        print(f"📅 Validation Date: {self.results['timestamp']}")
        print(f"🧪 Tests Run: {self.results['tests_run']}")
        print(f"✅ Tests Passed: {self.results['tests_passed']}")
        print(f"❌ Tests Failed: {self.results['tests_failed']}")

        if self.results["tests_run"] > 0:
            success_rate = (self.results["tests_passed"] / self.results["tests_run"]) * 100
            print(f"📊 Success Rate: {success_rate:.1f}%")

        print(
            f"\n📋 OVERALL STATUS: {'🟢 READY FOR PRODUCTION' if self.results['tests_failed'] == 0 else '🟡 NEEDS ATTENTION'}"
        )

        if self.results["tests_failed"] > 0:
            print("\n❌ FAILED TESTS:")
            for detail in self.results["details"]:
                if "FAIL" in detail["status"]:
                    print(f"   • {detail['test']}: {detail['details']}")

        print("\n🚀 MONETIZATION SYSTEMS SUMMARY:")
        print("   • Google Blogger Integration: Auto-publish betting reports for SEO traffic")
        print("   • Scheduled Exports: Daily/weekly automated report generation and distribution")
        print("   • Log Management: Centralized analysis, cleanup, and monetization insights")
        print("   • Google Alerts: Real-time news ingestion and content monetization")
        print("   • ContentEngine Integration: Unified workflow for content generation")

        return self.results["tests_failed"] == 0

    def run_all_tests(self):
        """Run complete validation suite"""
        print("🚀 Starting EQ12 Comprehensive Integration Validation...")
        print(f"📂 Base Path: {self.base_path}")

        # Run all test suites
        self.test_vb_module_structure()
        self.test_database_schema()
        self.test_configuration_extensions()
        self.test_cli_integration()
        self.test_content_engine_integration()
        self.test_monetization_workflow()

        # Generate final report
        return self.generate_summary_report()


def main():
    """Main validation entry point"""
    validator = EQ12IntegrationValidator()

    try:
        success = validator.run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ CRITICAL VALIDATION ERROR: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
