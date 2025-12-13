#!/usr/bin/env python3
"""
Google Integration Validation Script
Tests the EQ12 Google Drive + DocHub and Google Sheets + AppSheet integration
"""

import json
import os
import sys


def check_file_exists(file_path, description):
    """Check if a required file exists"""
    if os.path.exists(file_path):
        print("✅ {description}: {file_path}")
        return True
    print("❌ Missing {description}: {file_path}")
    return False


def validate_config_structure(config_path):
    """Validate config.json has required Google integration settings"""
    try:
        with open(config_path) as f:
            config = json.load(f)

        required_sections = ["google_drive", "google_sheets", "dochub", "appsheet"]

        missing_sections = []
        for section in required_sections:
            if section not in config:
                missing_sections.append(section)
            else:
                print("✅ Config section: {section}")

        if missing_sections:
            print("❌ Missing config sections: {', '.join(missing_sections)}")
            return False

        # Check Google Drive config
        drive_config = config.get("google_drive", {})
        drive_required = ["client_id", "client_secret", "redirect_uri", "token_path"]
        for field in drive_required:
            if field not in drive_config:
                print("❌ Missing google_drive.{field}")
                return False

        # Check Google Sheets config
        sheets_config = config.get("google_sheets", {})
        if "sheet_id" not in sheets_config:
            print("❌ Missing google_sheets.sheet_id")
            return False

        print("✅ Configuration structure validation passed")
        return True

    except json.JSONDecodeError:
        print("❌ Invalid JSON in config file: {e}")
        return False
    except Exception:
        print("❌ Error validating config: {e}")
        return False


def validate_vb_modules():
    """Check VB.NET module files for basic structure"""
    base_path = "c:/EQ12/visual_studio_projects/EQ12SportsBettingTerminal/Modules"

    modules = [
        (
            "GoogleAuthHelper.vb",
            [
                "Public Shared Function GenerateAuthUrl",
                "Public Shared Function ExchangeCodeForTokens",
                "Public Shared Function GetAccessToken",
                "Public Shared Function StartAuthFlow",
                "Public Shared Function TestConnection",
            ],
        ),
        (
            "DriveHelper.vb",
            [
                "Public Shared Function UploadReport",
                "Public Shared Function GetDocHubUrl",
                "Public Shared Function GetShareableLink",
                "Public Shared Function UploadReportWithWorkflow",
                "Public Shared Function ListFiles",
            ],
        ),
        (
            "SheetsHelper.vb",
            [
                "Public Shared Function SyncTable",
                "Public Shared Function SyncMultipleTables",
                "Public Shared Function TestSheetsConnection",
                "Private Shared Function CheckSheetExists",
                "Private Shared Function CreateSheet",
            ],
        ),
    ]

    all_valid = True

    for module_name, required_functions in modules:
        module_path = os.path.join(base_path, module_name)

        if not check_file_exists(module_path, f"VB.NET Module {module_name}"):
            all_valid = False
            continue

        try:
            with open(module_path, encoding="utf-8") as f:
                content = f.read()

            missing_functions = []
            for func in required_functions:
                if func not in content:
                    missing_functions.append(func.split(" ")[-1])  # Get function name only

            if missing_functions:
                print(f"❌ {module_name} missing functions: {', '.join(missing_functions)}")
                all_valid = False
            else:
                print("✅ {module_name} structure validation passed")

        except Exception:
            print("❌ Error reading {module_name}: {e}")
            all_valid = False

    return all_valid


def validate_cli_integration():
    """Check CLI integration for Google commands"""
    cli_path = "c:/EQ12/visual_studio_projects/EQ12SportsBettingTerminal/Eq12Cli.vb"

    if not check_file_exists(cli_path, "CLI Module"):
        return False

    try:
        with open(cli_path, encoding="utf-8") as f:
            content = f.read()

        required_commands = [
            'Case "test-google-drive"',
            'Case "test-google-sheets"',
            'Case "upload-report"',
            'Case "sync-sheets"',
            "Private Sub TestGoogleDrive",
            "Private Sub TestGoogleSheets",
            "Private Sub UploadReport",
            "Private Sub SyncSheets",
        ]

        missing_commands = []
        for cmd in required_commands:
            if cmd not in content:
                missing_commands.append(cmd)

        if missing_commands:
            print("❌ CLI missing commands: {', '.join(missing_commands)}")
            return False
        print("✅ CLI integration validation passed")
        return True

    except Exception:
        print("❌ Error reading CLI file: {e}")
        return False


def validate_database_schema():
    """Check database schema for Google integration tables"""
    schema_path = "c:/EQ12/visual_studio_projects/EQ12SportsBettingTerminal/Data/schema.sql"

    if not check_file_exists(schema_path, "Database Schema"):
        return False

    try:
        with open(schema_path) as f:
            content = f.read()

        required_tables = [
            "CREATE TABLE IF NOT EXISTS drive_uploads",
            "CREATE TABLE IF NOT EXISTS sheet_syncs",
        ]

        missing_tables = []
        for table in required_tables:
            if table not in content:
                missing_tables.append(table.split()[-1])  # Get table name

        if missing_tables:
            print("❌ Database missing tables: {', '.join(missing_tables)}")
            return False
        print("✅ Database schema validation passed")
        return True

    except Exception:
        print("❌ Error reading schema file: {e}")
        return False


def main():
    """Run complete Google integration validation"""
    print("🚀 EQ12 Google Integration Validation")
    print("=" * 50)
    print()

    # Configuration validation
    print("📋 Validating Configuration...")
    config_path = "c:/EQ12/visual_studio_projects/EQ12SportsBettingTerminal/Config/config.json"
    config_valid = validate_config_structure(config_path)
    print()

    # VB.NET modules validation
    print("🔧 Validating VB.NET Modules...")
    modules_valid = validate_vb_modules()
    print()

    # CLI integration validation
    print("⚡ Validating CLI Integration...")
    cli_valid = validate_cli_integration()
    print()

    # Database schema validation
    print("🗄️ Validating Database Schema...")
    db_valid = validate_database_schema()
    print()

    # Summary
    print("📊 VALIDATION SUMMARY")
    print("=" * 30)

    results = [
        ("Configuration Structure", config_valid),
        ("VB.NET Module Structure", modules_valid),
        ("CLI Integration", cli_valid),
        ("Database Schema", db_valid),
    ]

    passed = sum(1 for _, valid in results if valid)
    total = len(results)

    for _name, _valid in results:
        print("  {status} {name}")

    print()
    print("Overall: {passed}/{total} validations passed")

    if passed == total:
        print("🎉 Google integration validation completed successfully!")
        print()
        print("Next Steps:")
        print("1. Set up OAuth2 credentials in Google Cloud Console")
        print("2. Configure client_id and client_secret in config.json")
        print("3. Create target Google Drive folder and Sheets spreadsheet")
        print("4. Test authentication flow: test-google-drive command")
        print("5. Test file upload: upload-report --file=sample.pdf")
        print("6. Test sheets sync: sync-sheets --table=events")
        return True
    print("❌ Validation failed - please fix issues above")
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
