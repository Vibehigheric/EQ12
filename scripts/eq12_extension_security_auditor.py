#!/usr/bin/env python3
"""
EQ12 Secure Extension Security Auditor
Implements Mozilla Extension Workshop security best practices for cross-browser extensions.

Based on security guidelines from:
- https://extensionworkshop.com/documentation/develop/build-a-secure-extension/
- https://extensionworkshop.com/documentation/develop/browser-compatibility/

Author: EQ12 AI Agent
"""

import argparse
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ExtensionSecurityAuditor:
    """
    Security auditor implementing Mozilla Extension Workshop best practices:
    - Remote script injection detection
    - Unsafe DOM manipulation checks
    - CSP policy validation
    - Third-party library security analysis
    - XSS vulnerability scanning
    """

    def __init__(self, extension_path: str):
        self.extension_path = Path(extension_path)
        self.security_issues = []
        self.warnings = []
        self.recommendations = []

        # Security patterns to detect
        self.dangerous_patterns = {
            "eval_usage": [
                r"eval\s*\(",
                r"window\.eval\s*\(",
                r"Function\s*\(",
                r'setTimeout\s*\(\s*["\']',
                r'setInterval\s*\(\s*["\']',
            ],
            "remote_script_injection": [
                r'document\.createElement\s*\(\s*["\']script["\']',
                r'script\.src\s*=\s*["\']https?://',
                r"\.innerHTML\s*=.*<script",
                r"\.outerHTML\s*=.*<script",
            ],
            "unsafe_dom_manipulation": [
                r"\.innerHTML\s*\+=",
                r'\.innerHTML\s*=\s*[^"\']*\+',
                r"\.outerHTML\s*\+=",
                r"\.insertAdjacentHTML\s*\(",
                r"document\.write\s*\(",
                r"document\.writeln\s*\(",
            ],
            "xhr_security_issues": [
                r'XMLHttpRequest\s*\(\s*\).*open\s*\(\s*["\']GET["\'].*http://',
                r'fetch\s*\(\s*["\']http://',
                r'\.open\s*\(\s*["\'][^"\']*["\'],\s*["\']http://',
            ],
            "crypto_miners": [
                r"coinhive",
                r"cryptonight",
                r"monero.*mining",
                r"bitcoin.*mining",
                r"webassembly.*mining",
            ],
            "fingerprinting": [
                r"moz-extension://",
                r"chrome-extension://",
                r"navigator\.plugins",
                r"screen\.width.*screen\.height",
                r"canvas\.getContext.*toDataURL",
            ],
        }

        # Approved third-party libraries with known secure versions
        self.approved_libraries = {
            "jquery": {
                "min_version": "3.5.1",
                "security_notes": "Versions < 3.5.1 have XSS vulnerabilities",
            },
            "dompurify": {
                "min_version": "2.0.7",
                "security_notes": "Versions <= 2.0.6 have XSS vulnerabilities",
            },
            "lodash": {
                "min_version": "4.17.21",
                "security_notes": "Older versions have prototype pollution issues",
            },
        }

    def audit_extension(self) -> dict[str, Any]:
        """Run comprehensive security audit"""
        logger.info(f"Starting security audit of {self.extension_path}")

        audit_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "extension_path": str(self.extension_path),
            "security_score": 0,
            "issues": [],
            "warnings": [],
            "recommendations": [],
            "files_analyzed": [],
            "compliance": {
                "mozilla_guidelines": False,
                "csp_compliance": False,
                "third_party_security": False,
                "no_remote_scripts": False,
            },
        }

        # Audit manifest.json
        self.audit_manifest()

        # Audit JavaScript files
        js_files = list(self.extension_path.rglob("*.js"))
        for js_file in js_files:
            self.audit_javascript_file(js_file)
            audit_results["files_analyzed"].append(str(js_file))

        # Audit HTML files
        html_files = list(self.extension_path.rglob("*.html"))
        for html_file in html_files:
            self.audit_html_file(html_file)
            audit_results["files_analyzed"].append(str(html_file))

        # Check for third-party libraries
        self.audit_third_party_libraries()

        # Calculate security score
        audit_results["security_score"] = self.calculate_security_score()
        audit_results["issues"] = self.security_issues
        audit_results["warnings"] = self.warnings
        audit_results["recommendations"] = self.recommendations
        audit_results["compliance"] = self.assess_compliance()

        return audit_results

    def audit_manifest(self):
        """Audit manifest.json for security issues"""
        manifest_path = self.extension_path / "manifest.json"
        if not manifest_path.exists():
            self.security_issues.append(
                {
                    "type": "missing_manifest",
                    "severity": "critical",
                    "message": "manifest.json not found",
                    "file": str(manifest_path),
                }
            )
            return

        try:
            with open(manifest_path, encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception as e:
            self.security_issues.append(
                {
                    "type": "invalid_manifest",
                    "severity": "critical",
                    "message": f"Failed to parse manifest.json: {e}",
                    "file": str(manifest_path),
                }
            )
            return

        # Check CSP
        csp = manifest.get("content_security_policy")
        if csp:
            self.audit_csp_policy(csp, str(manifest_path))
        else:
            self.warnings.append(
                {
                    "type": "missing_csp",
                    "message": "No custom CSP defined, using default",
                    "file": str(manifest_path),
                    "recommendation": "Consider defining a strict CSP for additional security",
                }
            )

        # Check permissions
        permissions = manifest.get("permissions", [])
        self.audit_permissions(permissions, str(manifest_path))

        # Check web accessible resources
        web_resources = manifest.get("web_accessible_resources", [])
        if web_resources:
            self.audit_web_accessible_resources(web_resources, str(manifest_path))

    def audit_csp_policy(self, csp: str, file_path: str):
        """Audit Content Security Policy"""
        # Check for unsafe CSP directives
        unsafe_patterns = [
            r"'unsafe-eval'",
            r"'unsafe-inline'",
            r"data:\s*",
            r"https?://\*",
            r"\*",
        ]

        for pattern in unsafe_patterns:
            if re.search(pattern, csp, re.IGNORECASE):
                self.security_issues.append(
                    {
                        "type": "unsafe_csp",
                        "severity": "high",
                        "message": f"Unsafe CSP directive found: {pattern}",
                        "file": file_path,
                        "line": csp,
                    }
                )

    def audit_permissions(self, permissions: list[str], file_path: str):
        """Audit extension permissions for over-privileging"""
        sensitive_permissions = [
            "tabs",
            "activeTab",
            "webNavigation",
            "webRequest",
            "webRequestBlocking",
            "debugger",
            "desktopCapture",
            "nativeMessaging",
        ]

        for permission in permissions:
            if permission in sensitive_permissions:
                self.warnings.append(
                    {
                        "type": "sensitive_permission",
                        "message": f"Sensitive permission requested: {permission}",
                        "file": file_path,
                        "recommendation": f"Ensure {permission} permission is necessary for core functionality",
                    })

    def audit_web_accessible_resources(self, resources: list[str], file_path: str):
        """Check web accessible resources for security issues"""
        for resource in resources:
            if "*" in resource or resource.endswith("/"):
                self.warnings.append(
                    {
                        "type": "overly_broad_web_resources",
                        "message": f"Overly broad web accessible resource: {resource}",
                        "file": file_path,
                        "recommendation": "Be specific about which files are web accessible",
                    })

    def audit_javascript_file(self, js_file: Path):
        """Audit JavaScript file for security vulnerabilities"""
        try:
            with open(js_file, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self.warnings.append(
                {
                    "type": "file_read_error",
                    "message": f"Could not read {js_file}: {e}",
                    "file": str(js_file),
                }
            )
            return

        # Check for dangerous patterns
        for category, patterns in self.dangerous_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1

                    severity = (
                        "critical"
                        if category in ["eval_usage", "remote_script_injection"]
                        else "high"
                    )

                    self.security_issues.append(
                        {
                            "type": category,
                            "severity": severity,
                            "message": f"Dangerous pattern detected: {pattern}",
                            "file": str(js_file),
                            "line": line_num,
                            "code_snippet": match.group(0),
                        }
                    )

        # Check for Google Analytics best practices
        if "google-analytics.com" in content or "gtag(" in content:
            if "XMLHttpRequest" not in content and "fetch(" not in content:
                self.warnings.append(
                    {
                        "type": "analytics_implementation",
                        "message": "Google Analytics script injection detected",
                        "file": str(js_file),
                        "recommendation": "Use XHR/fetch for Google Analytics instead of script injection",
                    })

    def audit_html_file(self, html_file: Path):
        """Audit HTML file for security issues"""
        try:
            with open(html_file, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self.warnings.append(
                {
                    "type": "file_read_error",
                    "message": f"Could not read {html_file}: {e}",
                    "file": str(html_file),
                }
            )
            return

        # Check for inline scripts
        inline_script_pattern = r"<script[^>]*>(?!</script>)"
        matches = re.finditer(inline_script_pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            line_num = content[: match.start()].count("\n") + 1
            self.warnings.append(
                {
                    "type": "inline_script",
                    "message": "Inline script detected",
                    "file": str(html_file),
                    "line": line_num,
                    "recommendation": "Move JavaScript to external files for better CSP compliance",
                })

        # Check for remote script sources
        remote_script_pattern = r'<script[^>]*src\s*=\s*["\']https?://[^"\']+["\'][^>]*>'
        matches = re.finditer(remote_script_pattern, content, re.IGNORECASE)
        for match in matches:
            line_num = content[: match.start()].count("\n") + 1
            self.security_issues.append(
                {
                    "type": "remote_script_source",
                    "severity": "critical",
                    "message": "Remote script source detected",
                    "file": str(html_file),
                    "line": line_num,
                    "code_snippet": match.group(0),
                }
            )

    def audit_third_party_libraries(self):
        """Audit third-party libraries for known vulnerabilities"""
        # Common locations for third-party libraries
        lib_patterns = [
            "*/lib/**/*.js",
            "*/libs/**/*.js",
            "*/vendor/**/*.js",
            "*/node_modules/**/*.js",
            "**/jquery*.js",
            "**/dompurify*.js",
            "**/lodash*.js",
        ]

        found_libraries = set()

        for pattern in lib_patterns:
            for lib_file in self.extension_path.glob(pattern):
                # Extract library name and version from filename
                filename = lib_file.name
                lib_info = self.identify_library(filename)

                if lib_info:
                    found_libraries.add(
                        (lib_info["name"], lib_info.get(
                            "version", "unknown")))

                    # Check if library is approved and version is secure
                    if lib_info["name"] in self.approved_libraries:
                        approved = self.approved_libraries[lib_info["name"]]
                        if (lib_info.get("version") and self.version_compare(
                                lib_info["version"], approved["min_version"]) < 0):
                            self.security_issues.append(
                                {
                                    "type": "outdated_library",
                                    "severity": "high",
                                    "message": f'Outdated {
                                        lib_info["name"]} version {
                                        lib_info["version"]}',
                                    "file": str(lib_file),
                                    "recommendation": f'Update to version {
                                        approved["min_version"]} or higher',
                                })

        # Log found libraries
        for name, version in found_libraries:
            logger.info(f"Found third-party library: {name} v{version}")

    def identify_library(self, filename: str) -> dict[str, str]:
        """Identify library name and version from filename"""
        patterns = [
            r"jquery[.-](\d+\.\d+\.\d+)",
            r"dompurify[.-](\d+\.\d+\.\d+)",
            r"lodash[.-](\d+\.\d+\.\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                lib_name = pattern.split("[")[0]
                version = match.group(1)
                return {"name": lib_name, "version": version}

        return {}

    def version_compare(self, version1: str, version2: str) -> int:
        """Compare two semantic versions. Returns -1 if v1 < v2, 0 if equal, 1 if v1 > v2"""

        def normalize(v):
            return [int(x) for x in v.split(".")]

        v1_parts = normalize(version1)
        v2_parts = normalize(version2)

        # Pad shorter version with zeros
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts.extend([0] * (max_len - len(v1_parts)))
        v2_parts.extend([0] * (max_len - len(v2_parts)))

        for i in range(max_len):
            if v1_parts[i] < v2_parts[i]:
                return -1
            elif v1_parts[i] > v2_parts[i]:
                return 1

        return 0

    def calculate_security_score(self) -> int:
        """Calculate security score (0-100)"""
        score = 100

        # Deduct points for issues
        for issue in self.security_issues:
            if issue["severity"] == "critical":
                score -= 20
            elif issue["severity"] == "high":
                score -= 10
            elif issue["severity"] == "medium":
                score -= 5

        # Deduct points for warnings
        score -= len(self.warnings) * 2

        return max(0, score)

    def assess_compliance(self) -> dict[str, bool]:
        """Assess compliance with Mozilla guidelines"""
        compliance = {
            "mozilla_guidelines": True,
            "csp_compliance": True,
            "third_party_security": True,
            "no_remote_scripts": True,
        }

        # Check for critical security issues
        for issue in self.security_issues:
            if issue["type"] in ["remote_script_injection", "remote_script_source"]:
                compliance["no_remote_scripts"] = False
            if issue["type"] in ["unsafe_csp"]:
                compliance["csp_compliance"] = False
            if issue["type"] in ["outdated_library"]:
                compliance["third_party_security"] = False

        # Overall compliance
        compliance["mozilla_guidelines"] = all(compliance.values())

        return compliance

    def generate_security_recommendations(self) -> list[str]:
        """Generate actionable security recommendations"""
        recommendations = [
            "✅ Use safe DOM manipulation methods: createElement(), setAttribute(), textContent",
            "✅ Sanitize HTML content with DOMPurify before insertion",
            "✅ Use XHR/fetch for Google Analytics instead of script injection",
            "✅ Implement strict Content Security Policy",
            "✅ Keep third-party libraries up to date",
            "✅ Avoid eval(), innerHTML, and other unsafe JavaScript patterns",
            "✅ Use extension UI components instead of injecting into web pages",
            "✅ Validate and sanitize all user inputs",
            "✅ Use HTTPS for all remote requests",
            "✅ Implement proper error handling to prevent information leakage",
        ]

        return recommendations


def main():
    parser = argparse.ArgumentParser(description="EQ12 Extension Security Auditor")
    parser.add_argument(
        "--extension-path",
        "-e",
        required=True,
        help="Path to extension directory")
    parser.add_argument("--output", "-o", help="Output file for audit report (JSON)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run security audit
    auditor = ExtensionSecurityAuditor(args.extension_path)
    results = auditor.audit_extension()

    # Add recommendations
    results["security_recommendations"] = auditor.generate_security_recommendations()

    # Output results
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Audit report saved to {args.output}")
    else:
        print(json.dumps(results, indent=2))

    # Print summary
    score = results["security_score"]
    print("\n🔒 EQ12 Extension Security Audit Summary")
    print(f"Security Score: {score}/100")
    print(f"Issues Found: {len(results['issues'])}")
    print(f"Warnings: {len(results['warnings'])}")
    print(
        f"Mozilla Compliance: {
            '✅' if results['compliance']['mozilla_guidelines'] else '❌'}")

    if score < 70:
        print("⚠️  Security score is below recommended threshold (70)")
        print("Review and address security issues before publishing")
    elif score < 85:
        print("🟡 Good security score, but room for improvement")
    else:
        print("🟢 Excellent security score!")


if __name__ == "__main__":
    main()
