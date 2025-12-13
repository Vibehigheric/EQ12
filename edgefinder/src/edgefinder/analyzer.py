"""
Repository Analysis System
Static analysis and security scanning of downloaded repositories
"""

import ast
import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Any

from .config import Config
from .models import (
    AnalysisResult,
    AnalysisStatus,
    AuditLogEntry,
    Candidate,
    CodeMetrics,
    DependencyInfo,
    SecurityLevel,
    SecurityWarning,
)

logger = logging.getLogger(__name__)


class AnalysisError(Exception):
    """Repository analysis related errors"""

    pass


class SecurityAnalysisError(AnalysisError):
    """Security analysis specific errors"""

    pass


class RepositoryAnalyzer:
    """
    Static analyzer for downloaded repositories

    Performs security scanning, dependency analysis, code quality checks,
    and license validation without executing any downloaded code.
    """

    def __init__(self, config: Config):
        self.config = config
        self.audit_log: list[AuditLogEntry] = []

    def _log_analysis_action(
        self, action: str, candidate_id: str, details: dict[str, Any] | None = None
    ):
        """Log analysis action for audit trail"""
        entry = AuditLogEntry(
            action=f"analysis_{action}", details={"candidate_id": candidate_id, **(details or {})}
        )
        self.audit_log.append(entry)

    def _find_dependency_files(self, repo_path: Path) -> dict[str, list[Path]]:
        """
        Find dependency files in repository

        Args:
            repo_path: Path to repository directory

        Returns:
            Dictionary mapping ecosystem to list of dependency files
        """
        dependency_patterns = {
            "python": ["requirements.txt", "pyproject.toml", "setup.py", "setup.cfg", "Pipfile"],
            "node": ["package.json", "package-lock.json", "yarn.lock"],
            "rust": ["Cargo.toml", "Cargo.lock"],
            "ruby": ["Gemfile", "Gemfile.lock"],
            "php": ["composer.json", "composer.lock"],
            "go": ["go.mod", "go.sum"],
            "java": ["pom.xml", "build.gradle", "gradle.lockfile"],
            "dotnet": ["*.csproj", "packages.config", "project.json"],
        }

        found_files = {}

        for ecosystem, patterns in dependency_patterns.items():
            ecosystem_files = []
            for pattern in patterns:
                # Handle glob patterns
                if "*" in pattern:
                    matches = list(repo_path.rglob(pattern))
                else:
                    matches = list(repo_path.rglob(pattern))
                ecosystem_files.extend(matches)

            if ecosystem_files:
                found_files[ecosystem] = ecosystem_files

        return found_files

    def _analyze_python_dependencies(self, dep_files: list[Path]) -> list[DependencyInfo]:
        """
        Analyze Python dependency files

        Args:
            dep_files: List of Python dependency files

        Returns:
            List of DependencyInfo objects
        """
        dependencies = []

        for file_path in dep_files:
            try:
                if file_path.name == "requirements.txt":
                    dependencies.extend(self._parse_requirements_txt(file_path))
                elif file_path.name == "pyproject.toml":
                    dependencies.extend(self._parse_pyproject_toml(file_path))
                elif file_path.name in ["setup.py", "setup.cfg"]:
                    dependencies.extend(self._parse_setup_files(file_path))
            except Exception as e:
                logger.warning(f"Failed to parse {file_path}: {e}")

        return dependencies

    def _parse_requirements_txt(self, file_path: Path) -> list[DependencyInfo]:
        """Parse requirements.txt file"""
        dependencies = []

        try:
            content = file_path.read_text(encoding="utf-8")
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Parse package name and version
                # Handle various formats: package==1.0, package>=1.0, package~=1.0, etc.
                match = re.match(r"^([a-zA-Z0-9][a-zA-Z0-9\-_.]*[a-zA-Z0-9])[<>=!~]*(.*)$", line)
                if match:
                    name = match.group(1)
                    version = match.group(2).strip() if match.group(2) else None

                    dependencies.append(
                        DependencyInfo(name=name, version=version, ecosystem="pypi")
                    )
        except Exception as e:
            logger.warning(f"Failed to parse requirements.txt {file_path}: {e}")

        return dependencies

    def _parse_pyproject_toml(self, file_path: Path) -> list[DependencyInfo]:
        """Parse pyproject.toml file"""
        dependencies = []

        try:
            import tomllib  # Python 3.11+
        except ImportError:
            try:
                import tomli as tomllib  # Fallback for older Python
            except ImportError:
                logger.warning("TOML parser not available, skipping pyproject.toml analysis")
                return dependencies

        try:
            content = file_path.read_text(encoding="utf-8")
            data = tomllib.loads(content)

            # Check different dependency sections
            dependency_sections = [
                ("project", "dependencies"),
                ("tool.poetry", "dependencies"),
                ("build-system", "requires"),
            ]

            for section_path in dependency_sections:
                current = data
                for key in section_path:
                    current = current.get(key, {})
                    if not current:
                        break

                if isinstance(current, list):
                    # Build system style (list of strings)
                    for dep in current:
                        match = re.match(r"^([a-zA-Z0-9][a-zA-Z0-9\-_.]*[a-zA-Z0-9])", dep)
                        if match:
                            dependencies.append(
                                DependencyInfo(name=match.group(1), ecosystem="pypi")
                            )
                elif isinstance(current, dict):
                    # Poetry/project style (dict)
                    for name, version_spec in current.items():
                        if name != "python":  # Skip python version specifier
                            dependencies.append(
                                DependencyInfo(
                                    name=name,
                                    version=(
                                        str(version_spec)
                                        if not isinstance(version_spec, dict)
                                        else None
                                    ),
                                    ecosystem="pypi",
                                )
                            )

        except Exception as e:
            logger.warning(f"Failed to parse pyproject.toml {file_path}: {e}")

        return dependencies

    def _parse_setup_files(self, file_path: Path) -> list[DependencyInfo]:
        """Parse setup.py or setup.cfg files"""
        dependencies = []

        if file_path.name == "setup.py":
            # Parse setup.py using AST (safer than exec)
            try:
                content = file_path.read_text(encoding="utf-8")
                tree = ast.parse(content)

                # Look for setup() calls and extract install_requires
                for node in ast.walk(tree):
                    if (
                        isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Name)
                        and node.func.id == "setup"
                    ):

                        for keyword in node.keywords:
                            if keyword.arg == "install_requires":
                                if isinstance(keyword.value, ast.List):
                                    for item in keyword.value.elts:
                                        if isinstance(item, ast.Str):
                                            dep_str = item.s
                                        elif isinstance(item, ast.Constant):
                                            dep_str = str(item.value)
                                        else:
                                            continue

                                        match = re.match(
                                            r"^([a-zA-Z0-9][a-zA-Z0-9\-_.]*[a-zA-Z0-9])", dep_str
                                        )
                                        if match:
                                            dependencies.append(
                                                DependencyInfo(
                                                    name=match.group(1), ecosystem="pypi"
                                                )
                                            )
            except Exception as e:
                logger.warning(f"Failed to parse setup.py {file_path}: {e}")

        return dependencies

    def _analyze_node_dependencies(self, dep_files: list[Path]) -> list[DependencyInfo]:
        """Analyze Node.js dependency files"""
        dependencies = []

        for file_path in dep_files:
            if file_path.name == "package.json":
                try:
                    content = json.loads(file_path.read_text(encoding="utf-8"))

                    # Check dependencies and devDependencies
                    for dep_type in ["dependencies", "devDependencies", "peerDependencies"]:
                        deps = content.get(dep_type, {})
                        for name, version in deps.items():
                            dependencies.append(
                                DependencyInfo(name=name, version=version, ecosystem="npm")
                            )

                except Exception as e:
                    logger.warning(f"Failed to parse package.json {file_path}: {e}")

        return dependencies

    def _run_security_scan_bandit(self, repo_path: Path) -> list[SecurityWarning]:
        """
        Run Bandit security scanner on Python code

        Args:
            repo_path: Path to repository

        Returns:
            List of security warnings
        """
        warnings = []

        if not self.config.security.bandit_enabled:
            return warnings

        try:
            # Check if bandit is available
            result = subprocess.run(
                ["bandit", "--version"], capture_output=True, text=True, timeout=30
            )

            if result.returncode != 0:
                logger.warning("Bandit not available, skipping Python security scan")
                return warnings

            # Run bandit scan
            cmd = ["bandit", "-r", str(repo_path), "-f", "json", "-ll"]  # Low confidence level

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300, cwd=repo_path  # 5 minute timeout
            )

            if result.stdout:
                try:
                    bandit_data = json.loads(result.stdout)

                    for issue in bandit_data.get("results", []):
                        # Map bandit severity to our levels
                        severity_map = {
                            "LOW": SecurityLevel.LOW,
                            "MEDIUM": SecurityLevel.MEDIUM,
                            "HIGH": SecurityLevel.HIGH,
                        }

                        level = severity_map.get(
                            issue.get("issue_severity", "LOW"), SecurityLevel.LOW
                        )

                        warnings.append(
                            SecurityWarning(
                                level=level,
                                title=issue.get("test_name", "Security Issue"),
                                description=issue.get("issue_text", ""),
                                file_path=issue.get("filename", ""),
                                line_number=issue.get("line_number"),
                                rule_id=issue.get("test_id", ""),
                                confidence=(
                                    issue.get("issue_confidence", 0.5) / 100.0
                                    if isinstance(issue.get("issue_confidence"), (int, float))
                                    else 0.5
                                ),
                            )
                        )

                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse bandit output: {e}")

        except subprocess.TimeoutExpired:
            logger.warning("Bandit scan timed out")
        except Exception as e:
            logger.warning(f"Bandit scan failed: {e}")

        return warnings

    def _run_custom_security_rules(self, repo_path: Path) -> list[SecurityWarning]:
        """
        Run custom security rules using pattern matching

        Args:
            repo_path: Path to repository

        Returns:
            List of security warnings
        """
        warnings = []

        if not self.config.security.custom_rules_enabled:
            return warnings

        # Define security patterns
        security_patterns = [
            {
                "pattern": r"password\s*=\s*[\"'][^\"']+[\"']",
                "title": "Hardcoded Password",
                "level": SecurityLevel.HIGH,
                "description": "Found potential hardcoded password",
            },
            {
                "pattern": r"api[_-]?key\s*=\s*[\"'][^\"']+[\"']",
                "title": "Hardcoded API Key",
                "level": SecurityLevel.HIGH,
                "description": "Found potential hardcoded API key",
            },
            {
                "pattern": r"secret[_-]?key\s*=\s*[\"'][^\"']+[\"']",
                "title": "Hardcoded Secret",
                "level": SecurityLevel.HIGH,
                "description": "Found potential hardcoded secret",
            },
            {
                "pattern": r"eval\s*\(",
                "title": "Use of eval()",
                "level": SecurityLevel.MEDIUM,
                "description": "Use of eval() can lead to code injection",
            },
            {
                "pattern": r"exec\s*\(",
                "title": "Use of exec()",
                "level": SecurityLevel.MEDIUM,
                "description": "Use of exec() can lead to code injection",
            },
            {
                "pattern": r"shell\s*=\s*True",
                "title": "Shell Injection Risk",
                "level": SecurityLevel.MEDIUM,
                "description": "subprocess with shell=True can lead to injection",
            },
        ]

        # Scan files for patterns
        for file_path in repo_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".py", ".js", ".ts", ".php", ".rb"]:
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")

                    for i, line in enumerate(content.splitlines(), 1):
                        for rule in security_patterns:
                            if re.search(rule["pattern"], line, re.IGNORECASE):
                                warnings.append(
                                    SecurityWarning(
                                        level=rule["level"],
                                        title=rule["title"],
                                        description=rule["description"],
                                        file_path=str(file_path.relative_to(repo_path)),
                                        line_number=i,
                                        rule_id=f"custom_{hash(rule['pattern']) % 10000}",
                                        confidence=0.7,
                                    )
                                )

                except Exception as e:
                    logger.debug(f"Failed to scan {file_path}: {e}")

        return warnings

    def _calculate_code_metrics(self, repo_path: Path) -> CodeMetrics:
        """
        Calculate basic code quality metrics

        Args:
            repo_path: Path to repository

        Returns:
            CodeMetrics object
        """
        total_lines = 0
        code_files = 0

        # Code file extensions to analyze
        code_extensions = {
            ".py",
            ".js",
            ".ts",
            ".java",
            ".cpp",
            ".c",
            ".cs",
            ".php",
            ".rb",
            ".go",
            ".rs",
        }

        for file_path in repo_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in code_extensions:
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    lines = len(content.splitlines())
                    total_lines += lines
                    code_files += 1
                except Exception:
                    continue

        return CodeMetrics(
            lines_of_code=total_lines,
            # Other metrics would require additional analysis tools
            cyclomatic_complexity=None,
            maintainability_index=None,
            test_coverage=None,
            documentation_coverage=None,
            code_duplication=None,
        )

    def _extract_readme_content(self, repo_path: Path) -> str | None:
        """
        Extract README content from repository

        Args:
            repo_path: Path to repository

        Returns:
            README content or None
        """
        readme_patterns = ["README*", "readme*", "Readme*"]

        for pattern in readme_patterns:
            matches = list(repo_path.glob(pattern))
            if matches:
                try:
                    # Take the first match
                    readme_path = matches[0]
                    return readme_path.read_text(encoding="utf-8", errors="ignore")
                except Exception as e:
                    logger.debug(f"Failed to read README {readme_path}: {e}")

        return None

    def _extract_license_content(self, repo_path: Path) -> str | None:
        """
        Extract LICENSE content from repository

        Args:
            repo_path: Path to repository

        Returns:
            LICENSE content or None
        """
        license_patterns = ["LICENSE*", "license*", "License*", "COPYING*", "COPYRIGHT*"]

        for pattern in license_patterns:
            matches = list(repo_path.glob(pattern))
            if matches:
                try:
                    # Take the first match
                    license_path = matches[0]
                    return license_path.read_text(encoding="utf-8", errors="ignore")
                except Exception as e:
                    logger.debug(f"Failed to read LICENSE {license_path}: {e}")

        return None

    def _find_important_files(self, repo_path: Path) -> list[str]:
        """
        Find important files in repository

        Args:
            repo_path: Path to repository

        Returns:
            List of important file paths
        """
        important_patterns = [
            "*.md",
            "*.txt",
            "*.rst",  # Documentation
            "requirements*.txt",
            "pyproject.toml",
            "setup.py",  # Python dependencies
            "package.json",
            "yarn.lock",  # Node.js
            "Cargo.toml",
            "Cargo.lock",  # Rust
            "Gemfile",
            "*.gemspec",  # Ruby
            "composer.json",  # PHP
            "pom.xml",
            "build.gradle",  # Java
            "*.csproj",
            "*.sln",  # .NET
            "Dockerfile",
            "docker-compose.yml",  # Docker
            ".github/workflows/*.yml",
            ".github/workflows/*.yaml",  # GitHub Actions
            "Makefile",
            "CMakeLists.txt",  # Build systems
        ]

        important_files = []

        for pattern in important_patterns:
            matches = list(repo_path.rglob(pattern))
            for match in matches:
                try:
                    relative_path = str(match.relative_to(repo_path))
                    important_files.append(relative_path)
                except ValueError:
                    continue

        # Limit to avoid overwhelming output
        return sorted(set(important_files))[:50]

    async def analyze_candidate(self, candidate: Candidate, repo_path: Path) -> AnalysisResult:
        """
        Perform comprehensive analysis of downloaded repository

        Args:
            candidate: Repository candidate
            repo_path: Path to extracted repository

        Returns:
            AnalysisResult with analysis findings
        """
        from datetime import datetime

        logger.info(f"Analyzing candidate: {candidate.id}")
        self._log_analysis_action("start", candidate.id)

        result = AnalysisResult(
            candidate_id=candidate.id,
            analysis_status=AnalysisStatus.IN_PROGRESS,
            started_at=datetime.utcnow(),
        )

        try:
            # Find dependency files
            dependency_files = self._find_dependency_files(repo_path)
            logger.debug(f"Found dependency files: {list(dependency_files.keys())}")

            # Analyze dependencies
            all_dependencies = []
            for ecosystem, files in dependency_files.items():
                if ecosystem == "python":
                    all_dependencies.extend(self._analyze_python_dependencies(files))
                elif ecosystem == "node":
                    all_dependencies.extend(self._analyze_node_dependencies(files))
                # Add more ecosystems as needed

            result.dependencies = all_dependencies

            # Run security scans
            security_warnings = []

            # Bandit scan for Python
            if "python" in dependency_files:
                security_warnings.extend(self._run_security_scan_bandit(repo_path))

            # Custom security rules
            security_warnings.extend(self._run_custom_security_rules(repo_path))

            # Limit security warnings to prevent overwhelming output
            max_warnings = self.config.security.max_security_warnings
            if len(security_warnings) > max_warnings:
                logger.warning(
                    f"Limiting security warnings to {max_warnings} (found {len(security_warnings)})"
                )
                security_warnings = security_warnings[:max_warnings]

            result.security_warnings = security_warnings

            # Calculate code metrics
            result.code_metrics = self._calculate_code_metrics(repo_path)

            # Extract important content
            result.readme_content = self._extract_readme_content(repo_path)
            result.license_text = self._extract_license_content(repo_path)
            result.important_files = self._find_important_files(repo_path)

            # Generate integration notes
            integration_notes = []

            if result.dependencies:
                integration_notes.append(f"Found {len(result.dependencies)} dependencies")

            if result.security_warnings:
                critical_warnings = [
                    w for w in result.security_warnings if w.level == SecurityLevel.CRITICAL
                ]
                high_warnings = [
                    w for w in result.security_warnings if w.level == SecurityLevel.HIGH
                ]

                if critical_warnings:
                    integration_notes.append(
                        f"⚠️ {len(critical_warnings)} CRITICAL security warnings"
                    )
                if high_warnings:
                    integration_notes.append(f"⚠️ {len(high_warnings)} HIGH security warnings")

            if result.code_metrics and result.code_metrics.lines_of_code:
                integration_notes.append(
                    f"Repository contains {result.code_metrics.lines_of_code} lines of code"
                )

            result.integration_notes = integration_notes

            # Mark as completed
            result.analysis_status = AnalysisStatus.COMPLETED
            result.completed_at = datetime.utcnow()

            self._log_analysis_action(
                "success",
                candidate.id,
                {
                    "dependencies_found": len(result.dependencies),
                    "security_warnings": len(result.security_warnings),
                    "lines_of_code": (
                        result.code_metrics.lines_of_code if result.code_metrics else 0
                    ),
                },
            )

            logger.info(f"Analysis completed for {candidate.id}")

        except Exception as e:
            logger.error(f"Analysis failed for {candidate.id}: {e}")
            result.analysis_status = AnalysisStatus.FAILED
            result.completed_at = datetime.utcnow()
            self._log_analysis_action("error", candidate.id, {"error": str(e)})
            raise AnalysisError(f"Analysis failed for {candidate.id}: {e}") from e

        return result

    def get_audit_log(self) -> list[AuditLogEntry]:
        """Get audit log of all analysis actions"""
        return self.audit_log.copy()
