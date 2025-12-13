#!/usr/bin/env python3
"""
EQ12 JavaScript/Node.js and C# Upgrade Tool
Modernizes JavaScript packages and C# OpenAI integrations
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EQ12JSCSUpgrader:
    """Upgrade JavaScript/Node.js and C# components"""

    def __init__(self):
        self.eq12_root = Path(".")
        self.upgrades = []
        self.errors = []

    def scan_javascript_components(self) -> dict[str, Any]:
        """Scan for JavaScript/Node.js components"""
        print("🔍 Scanning JavaScript/Node.js Components...")

        results = {
            "package_files": [],
            "js_files": [],
            "outdated_dependencies": [],
            "security_vulnerabilities": [],
        }

        # Find package.json files
        package_files = list(self.eq12_root.rglob("package.json"))

        for pkg_file in package_files:
            try:
                with open(pkg_file, encoding="utf-8") as f:
                    pkg_data = json.load(f)

                results["package_files"].append(
                    {
                        "path": str(pkg_file),
                        "name": pkg_data.get("name", "unknown"),
                        "version": pkg_data.get("version", "0.0.0"),
                        "dependencies": pkg_data.get("dependencies", {}),
                        "devDependencies": pkg_data.get("devDependencies", {}),
                    }
                )

                print(f"  ✅ Found package: {pkg_data.get('name')} v{pkg_data.get('version')}")

            except Exception as e:
                self.errors.append(f"Error reading {pkg_file}: {e}")
                print(f"  ❌ Error reading {pkg_file}: {e}")

        # Find JavaScript files
        js_files = list(self.eq12_root.rglob("*.js"))
        js_files.extend(list(self.eq12_root.rglob("*.ts")))

        for js_file in js_files[:10]:  # Limit to prevent overflow
            results["js_files"].append(str(js_file))

        print(f"  📄 Found {len(js_files)} JavaScript/TypeScript files")

        return results

    def upgrade_javascript_dependencies(self) -> list[str]:
        """Upgrade JavaScript dependencies where possible"""
        print("⬆️ Upgrading JavaScript Dependencies...")

        upgrades = []

        # Check the main Firefox extension package.json
        firefox_pkg = Path("eq12-firefox-ext/package.json")
        if firefox_pkg.exists():
            try:
                with open(firefox_pkg, encoding="utf-8") as f:
                    pkg_data = json.load(f)

                # Check webextension-polyfill version
                current_version = pkg_data.get("dependencies", {}).get(
                    "webextension-polyfill", "0.0.0"
                )

                # Modern webextension-polyfill is 0.12.0, let's upgrade to latest
                if current_version.startswith("0.12"):
                    print(f"  ✅ webextension-polyfill is modern: {current_version}")
                else:
                    # Upgrade to latest
                    pkg_data["dependencies"]["webextension-polyfill"] = "^0.12.0"

                    with open(firefox_pkg, "w", encoding="utf-8") as f:
                        json.dump(pkg_data, f, indent=4)

                    upgrades.append(f"Updated webextension-polyfill: {current_version} → ^0.12.0")
                    print(f"  ✅ Updated webextension-polyfill: {current_version} → ^0.12.0")

                # Add modern development tools
                if "devDependencies" not in pkg_data:
                    pkg_data["devDependencies"] = {}

                dev_upgrades = {
                    "eslint": "^8.57.0",
                    "@types/webextension-polyfill": "^0.10.7",
                    "web-ext": "^7.11.0",
                }

                for tool, version in dev_upgrades.items():
                    if tool not in pkg_data["devDependencies"]:
                        pkg_data["devDependencies"][tool] = version
                        upgrades.append(f"Added dev dependency: {tool} {version}")
                        print(f"  ✅ Added dev dependency: {tool} {version}")

                # Add modern scripts
                modern_scripts = {
                    "lint": "eslint src/**/*.js",
                    "build": "npm run build:windows:firefox",
                    "start": "web-ext run --source-dir=dist-firefox",
                    "package": "npm run package:windows",
                }

                for script, command in modern_scripts.items():
                    if script not in pkg_data.get("scripts", {}):
                        if "scripts" not in pkg_data:
                            pkg_data["scripts"] = {}
                        pkg_data["scripts"][script] = command
                        upgrades.append(f"Added npm script: {script}")
                        print(f"  ✅ Added npm script: {script}")

                # Save updated package.json
                with open(firefox_pkg, "w", encoding="utf-8") as f:
                    json.dump(pkg_data, f, indent=4)

            except Exception as e:
                self.errors.append(f"Error upgrading Firefox extension package.json: {e}")
                print(f"  ❌ Error upgrading Firefox extension: {e}")

        return upgrades

    def modernize_javascript_code(self) -> list[str]:
        """Modernize JavaScript code patterns"""
        print("🚀 Modernizing JavaScript Code...")

        modernizations = []

        # Check content.js for modern patterns
        content_js = Path("eq12-firefox-ext/src/content.js")
        if content_js.exists():
            try:
                with open(content_js, encoding="utf-8") as f:
                    content = f.read()

                # Check if using modern async/await
                if "async function" in content and "await fetch" in content:
                    print("  ✅ content.js uses modern async/await")
                else:
                    modernizations.append("content.js could benefit from async/await patterns")
                    print("  ⚠️ content.js could use async/await modernization")

                # Check for modern APIs
                if "browser.runtime" in content or "chrome.runtime" in content:
                    print("  ✅ content.js uses modern WebExtension APIs")
                else:
                    modernizations.append("content.js should use WebExtension APIs")

            except Exception as e:
                self.errors.append(f"Error analyzing content.js: {e}")

        return modernizations

    def scan_csharp_components(self) -> dict[str, Any]:
        """Scan for C# components"""
        print("🔍 Scanning C# Components...")

        results = {
            "csproj_files": [],
            "solution_files": [],
            "cs_files": [],
            "openai_references": [],
        }

        # Find C# project files
        csproj_files = list(self.eq12_root.rglob("*.csproj"))
        sln_files = list(self.eq12_root.rglob("*.sln"))
        cs_files = list(self.eq12_root.rglob("*.cs"))

        for proj_file in csproj_files:
            try:
                with open(proj_file, encoding="utf-8") as f:
                    content = f.read()

                results["csproj_files"].append(
                    {
                        "path": str(proj_file),
                        "has_openai_ref": "openai" in content.lower(),
                        "framework": self._extract_framework(content),
                    }
                )

                print(f"  ✅ Found C# project: {proj_file.name}")

            except Exception as e:
                self.errors.append(f"Error reading {proj_file}: {e}")

        # Check for OpenAI usage in C# files
        for cs_file in cs_files:
            try:
                with open(cs_file, encoding="utf-8") as f:
                    content = f.read()

                if "openai" in content.lower() or "chatgpt" in content.lower():
                    results["openai_references"].append(str(cs_file))
                    print(f"  🤖 Found OpenAI usage: {cs_file.name}")

            except Exception as e:
                self.errors.append(f"Error reading {cs_file}: {e}")

        results["solution_files"] = [str(f) for f in sln_files]
        results["cs_files"] = [str(f) for f in cs_files[:20]]  # Limit output

        print(
            f"  📄 Found {len(cs_files)} C# files, {len(csproj_files)} projects, {len(sln_files)} solutions"
        )

        return results

    def _extract_framework(self, csproj_content: str) -> str:
        """Extract .NET framework version from csproj content"""
        import re

        # Look for TargetFramework or TargetFrameworkVersion
        framework_match = re.search(
            r"<TargetFramework[^>]*>([^<]+)</TargetFramework[^>]*>", csproj_content
        )
        if framework_match:
            return framework_match.group(1)

        version_match = re.search(
            r"<TargetFrameworkVersion[^>]*>([^<]+)</TargetFrameworkVersion[^>]*>",
            csproj_content,
        )
        if version_match:
            return version_match.group(1)

        return "unknown"

    def upgrade_csharp_openai_integration(self) -> list[str]:
        """Upgrade C# OpenAI integration"""
        print("⬆️ Upgrading C# OpenAI Integration...")

        upgrades = []

        # Check the main OpenAI client
        openai_client = Path("EQ12.ChatGPT.InlineRefactor/Services/OpenAiClient.cs")
        if openai_client.exists():
            try:
                with open(openai_client, encoding="utf-8") as f:
                    content = f.read()

                # Check if using old endpoint
                if '"https://api.openai.com/v1/responses"' in content:
                    # This is wrong - should be chat/completions
                    new_content = content.replace(
                        '"https://api.openai.com/v1/responses"',
                        '"https://api.openai.com/v1/chat/completions"',
                    )

                    # Also fix the payload structure
                    old_payload = """var payload = new
            {
                model = model,
                input = BuildPrompt(instruction, selectedCode),
                temperature = 0.2
            };"""

                    new_payload = """var payload = new
            {
                model = model,
                messages = new[]
                {
                    new { role = "user", content = BuildPrompt(instruction, selectedCode) }
                },
                temperature = 0.2,
                max_tokens = 2000
            };"""

                    new_content = new_content.replace(old_payload, new_payload)

                    # Add using statement for modern JSON handling
                    if "using System.Text.Json;" not in new_content:
                        new_content = new_content.replace(
                            "using System.Threading.Tasks;",
                            "using System.Threading.Tasks;\nusing System.Text.Json;",
                        )

                    with open(openai_client, "w", encoding="utf-8") as f:
                        f.write(new_content)

                    upgrades.append("Fixed C# OpenAI endpoint to use chat/completions")
                    upgrades.append("Updated C# OpenAI payload structure for modern API")
                    print("  ✅ Fixed C# OpenAI client to use modern chat/completions API")

                # Check for modern model usage
                if '"gpt-3.5-turbo"' in content or '"text-davinci"' in content:
                    new_content = content.replace('"gpt-3.5-turbo"', '"gpt-4o-mini"')
                    new_content = new_content.replace('"text-davinci-003"', '"gpt-4o-mini"')

                    with open(openai_client, "w", encoding="utf-8") as f:
                        f.write(new_content)

                    upgrades.append("Updated C# OpenAI models to GPT-4o-mini")
                    print("  ✅ Updated C# OpenAI models to GPT-4o-mini")

            except Exception as e:
                self.errors.append(f"Error upgrading C# OpenAI client: {e}")
                print(f"  ❌ Error upgrading C# OpenAI client: {e}")

        return upgrades

    def create_modern_eslint_config(self):
        """Create modern ESLint configuration"""
        print("📝 Creating Modern ESLint Configuration...")

        eslint_config = {
            "env": {"browser": True, "webextensions": True, "es2022": True},
            "extends": ["eslint:recommended"],
            "parserOptions": {"ecmaVersion": 2022, "sourceType": "module"},
            "globals": {"browser": "readonly", "chrome": "readonly"},
            "rules": {
                "no-unused-vars": "warn",
                "no-console": "off",
                "prefer-const": "error",
                "no-var": "error",
            },
        }

        eslint_path = Path("eq12-firefox-ext/.eslintrc.json")
        try:
            with open(eslint_path, "w", encoding="utf-8") as f:
                json.dump(eslint_config, f, indent=2)

            print(f"  ✅ Created modern ESLint config: {eslint_path}")
            return True

        except Exception as e:
            self.errors.append(f"Error creating ESLint config: {e}")
            return False

    def generate_upgrade_report(self) -> dict[str, Any]:
        """Generate comprehensive upgrade report"""
        print("📊 Generating Upgrade Report...")

        # Run all scans and upgrades
        js_scan = self.scan_javascript_components()
        js_upgrades = self.upgrade_javascript_dependencies()
        js_modernizations = self.modernize_javascript_code()

        cs_scan = self.scan_csharp_components()
        cs_upgrades = self.upgrade_csharp_openai_integration()

        eslint_created = self.create_modern_eslint_config()

        report = {
            "timestamp": datetime.now().isoformat(),
            "javascript": {
                "scan_results": js_scan,
                "upgrades": js_upgrades,
                "modernizations": js_modernizations,
                "eslint_config_created": eslint_created,
            },
            "csharp": {"scan_results": cs_scan, "upgrades": cs_upgrades},
            "summary": {
                "total_js_upgrades": len(js_upgrades),
                "total_cs_upgrades": len(cs_upgrades),
                "total_errors": len(self.errors),
                "success": len(self.errors) == 0,
            },
            "errors": self.errors,
        }

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"logs/eq12_js_cs_upgrade_report_{timestamp}.json"

        try:
            os.makedirs("logs", exist_ok=True)
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)

            print(f"📋 Report saved: {report_path}")

        except Exception as e:
            print(f"⚠️ Could not save report: {e}")

        return report


def main():
    """Main upgrade function"""
    print("🚀 EQ12 JAVASCRIPT/NODE.JS & C# UPGRADE TOOL")
    print("=" * 50)

    upgrader = EQ12JSCSUpgrader()
    report = upgrader.generate_upgrade_report()

    print("\n" + "=" * 50)
    print("🎯 UPGRADE SUMMARY")
    print("=" * 50)
    print(f"JavaScript Upgrades: {report['summary']['total_js_upgrades']}")
    print(f"C# Upgrades: {report['summary']['total_cs_upgrades']}")
    print(f"Errors: {report['summary']['total_errors']}")

    if report["summary"]["success"]:
        print("✅ All upgrades completed successfully!")
    else:
        print("⚠️ Some errors occurred during upgrades")

    return report


if __name__ == "__main__":
    main()
