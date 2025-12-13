# eq12_testing_cicd_innovation.py
"""
EQ12 Testing & CI/CD Pipeline Innovation
Jest/Pytest integration, contract testing, JSON schema validation, automated API testing
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
import yaml
from jsonschema import ValidationError, validate

from eq12_helpers import setup_utf8_logging

setup_utf8_logging()


@dataclass
class TestSuite:
    """Test suite configuration"""

    name: str
    type: str  # pytest, jest, pester, api, contract
    test_files: list[Path]
    config_file: Path | None = None
    requirements: list[str] = field(default_factory=list)
    environment: dict[str, str] = field(default_factory=dict)
    timeout: int = 300  # 5 minutes default


@dataclass
class TestResult:
    """Test execution result"""

    suite_name: str
    success: bool
    tests_run: int
    tests_passed: int
    tests_failed: int
    duration_seconds: float
    coverage_percentage: float | None = None
    output: str = ""
    errors: list[str] = field(default_factory=list)


@dataclass
class APIContract:
    """API contract definition"""

    endpoint: str
    method: str
    request_schema: dict[str, Any]
    response_schema: dict[str, Any]
    status_codes: list[int]
    headers: dict[str, str] = field(default_factory=dict)


class TestEnvironmentManager:
    """Manage test environments and dependencies"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.venv_path = project_root / "test_env"
        self.node_modules_path = project_root / "node_modules"

    async def setup_python_test_environment(self) -> bool:
        """Setup Python testing environment with pytest"""

        try:
            # Create virtual environment if it doesn't exist
            if not self.venv_path.exists():
                result = await asyncio.create_subprocess_exec(
                    "python",
                    "-m",
                    "venv",
                    str(self.venv_path),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await result.communicate()

                if result.returncode != 0:
                    return False

            # Get pip path
            pip_path = self.venv_path / "Scripts" / "pip.exe"
            if not pip_path.exists():
                pip_path = self.venv_path / "bin" / "pip"

            # Install testing dependencies
            test_packages = [
                "pytest>=7.0.0",
                "pytest-asyncio>=0.21.0",
                "pytest-cov>=4.0.0",
                "pytest-html>=3.1.0",
                "pytest-json-report>=1.5.0",
                "coverage>=7.0.0",
                "requests>=2.28.0",
                "jsonschema>=4.0.0",
                "pydantic>=2.0.0",
            ]

            for package in test_packages:
                result = await asyncio.create_subprocess_exec(
                    str(pip_path),
                    "install",
                    package,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await result.communicate()

            return True

        except Exception as e:
            logging.error(f"Failed to setup Python test environment: {e}")
            return False

    async def setup_nodejs_test_environment(self) -> bool:
        """Setup Node.js testing environment with Jest"""

        try:
            # Check if package.json exists
            package_json_path = self.project_root / "package.json"

            if not package_json_path.exists():
                # Create basic package.json
                package_config = {
                    "name": "eq12-testing",
                    "version": "1.0.0",
                    "description": "EQ12 Testing Suite",
                    "scripts": {
                        "test": "jest",
                        "test:watch": "jest --watch",
                        "test:coverage": "jest --coverage",
                        "test:ci": "jest --ci --coverage --reporters=default --reporters=jest-junit",
                    },
                    "devDependencies": {
                        "jest": "^29.0.0",
                        "@jest/globals": "^29.0.0",
                        "jest-junit": "^16.0.0",
                        "supertest": "^6.3.0",
                        "@types/jest": "^29.0.0",
                        "@types/supertest": "^2.0.12",
                    },
                }

                package_json_path.write_text(json.dumps(package_config, indent=2), encoding="utf-8")

            # Install dependencies
            result = await asyncio.create_subprocess_exec(
                "npm",
                "install",
                cwd=str(self.project_root),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            _stdout, _stderr = await result.communicate()
            return result.returncode == 0

        except Exception as e:
            logging.error(f"Failed to setup Node.js test environment: {e}")
            return False

    def create_jest_config(self) -> Path:
        """Create Jest configuration"""

        jest_config = {
            "testEnvironment": "node",
            "collectCoverage": True,
            "coverageDirectory": "coverage",
            "coverageReporters": ["text", "lcov", "html"],
            "testMatch": ["**/tests/**/*.test.js", "**/tests/**/*.spec.js"],
            "testTimeout": 30000,
            "setupFilesAfterEnv": ["<rootDir>/tests/setup.js"],
            "collectCoverageFrom": [
                "src/**/*.js",
                "!src/**/*.test.js",
                "!**/node_modules/**",
            ],
        }

        config_path = self.project_root / "jest.config.json"
        config_path.write_text(json.dumps(jest_config, indent=2), encoding="utf-8")

        return config_path

    def create_pytest_config(self) -> Path:
        """Create pytest configuration"""

        pytest_config = {
            "pytest": {
                "testpaths": ["tests"],
                "python_files": ["test_*.py", "*_test.py"],
                "python_classes": ["Test*"],
                "python_functions": ["test_*"],
                "addopts": [
                    "--strict-markers",
                    "--strict-config",
                    "--cov=eq12",
                    "--cov-report=term-missing",
                    "--cov-report=html:htmlcov",
                    "--cov-report=xml",
                    "--html=reports/pytest_report.html",
                    "--self-contained-html",
                ],
                "markers": [
                    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
                    "integration: marks tests as integration tests",
                    "unit: marks tests as unit tests",
                    "api: marks tests as API tests",
                    "contract: marks tests as contract tests",
                ],
            }
        }

        config_path = self.project_root / "pytest.ini"

        # Convert to INI format
        ini_content = "[tool:pytest]\n"
        for key, value in pytest_config["pytest"].items():
            if isinstance(value, list):
                if key == "addopts":
                    ini_content += f"{key} = {' '.join(value)}\n"
                else:
                    ini_content += f"{key} = {' '.join(value)}\n"
            else:
                ini_content += f"{key} = {value}\n"

        config_path.write_text(ini_content, encoding="utf-8")
        return config_path


class TestRunner:
    """Advanced test execution and reporting"""

    def __init__(self, env_manager: TestEnvironmentManager):
        self.env_manager = env_manager
        self.test_results: list[TestResult] = []

    async def run_pytest_suite(self, suite: TestSuite) -> TestResult:
        """Run pytest test suite"""

        start_time = datetime.now()

        # Prepare pytest command
        python_path = self.env_manager.venv_path / "Scripts" / "python.exe"
        if not python_path.exists():
            python_path = self.env_manager.venv_path / "bin" / "python"

        pytest_args = [
            str(python_path),
            "-m",
            "pytest",
            "--json-report",
            f"--json-report-file={self.env_manager.project_root}/reports/{suite.name}_report.json",
            "--tb=short",
            "-v",
        ]

        # Add test files
        for test_file in suite.test_files:
            if test_file.exists():
                pytest_args.append(str(test_file))

        try:
            # Set environment variables
            env = os.environ.copy()
            env.update(suite.environment)

            # Run pytest
            process = await asyncio.create_subprocess_exec(
                *pytest_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=str(self.env_manager.project_root),
            )

            stdout, _stderr = await asyncio.wait_for(process.communicate(), timeout=suite.timeout)

            duration = (datetime.now() - start_time).total_seconds()

            # Parse results from JSON report
            report_path = self.env_manager.project_root / "reports" / f"{suite.name}_report.json"

            tests_run = 0
            tests_passed = 0
            tests_failed = 0

            if report_path.exists():
                try:
                    report_data = json.loads(report_path.read_text())
                    summary = report_data.get("summary", {})
                    tests_run = summary.get("total", 0)
                    tests_passed = summary.get("passed", 0)
                    tests_failed = summary.get("failed", 0)
                except:
                    pass

            return TestResult(
                suite_name=suite.name,
                success=process.returncode == 0,
                tests_run=tests_run,
                tests_passed=tests_passed,
                tests_failed=tests_failed,
                duration_seconds=duration,
                output=stdout.decode("utf-8", errors="ignore"),
            )

        except TimeoutError:
            return TestResult(
                suite_name=suite.name,
                success=False,
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                duration_seconds=suite.timeout,
                errors=["Test execution timed out"],
            )
        except Exception as e:
            return TestResult(
                suite_name=suite.name,
                success=False,
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                duration_seconds=0,
                errors=[str(e)],
            )

    async def run_jest_suite(self, suite: TestSuite) -> TestResult:
        """Run Jest test suite"""

        start_time = datetime.now()

        jest_args = [
            "npm",
            "test",
            "--",
            "--ci",
            "--coverage",
            "--reporters=default",
            "--reporters=jest-junit",
            "--outputFile=reports/jest-results.xml",
        ]

        try:
            # Set environment variables
            env = os.environ.copy()
            env.update(suite.environment)
            env["CI"] = "true"

            process = await asyncio.create_subprocess_exec(
                *jest_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=str(self.env_manager.project_root),
            )

            stdout, _stderr = await asyncio.wait_for(process.communicate(), timeout=suite.timeout)

            duration = (datetime.now() - start_time).total_seconds()

            # Parse Jest output for test counts
            output = stdout.decode("utf-8", errors="ignore")

            tests_run = 0
            tests_passed = 0
            tests_failed = 0

            # Simple parsing of Jest output
            if "Tests:" in output:
                lines = output.split("\n")
                for line in lines:
                    if "Tests:" in line:
                        # Extract numbers from Jest summary
                        import re

                        numbers = re.findall(r"\d+", line)
                        if len(numbers) >= 2:
                            tests_failed = int(numbers[0]) if "failed" in line else 0
                            tests_passed = int(numbers[1]) if "passed" in line else int(numbers[0])
                            tests_run = tests_passed + tests_failed

            return TestResult(
                suite_name=suite.name,
                success=process.returncode == 0,
                tests_run=tests_run,
                tests_passed=tests_passed,
                tests_failed=tests_failed,
                duration_seconds=duration,
                output=output,
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return TestResult(
                suite_name=suite.name,
                success=False,
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                duration_seconds=duration,
                errors=[str(e)],
            )


class ContractTester:
    """API contract testing system"""

    def __init__(self):
        self.contracts: list[APIContract] = []

    def add_contract(self, contract: APIContract):
        """Add API contract for testing"""
        self.contracts.append(contract)

    async def validate_contracts(self, base_url: str) -> list[dict[str, Any]]:
        """Validate all API contracts"""

        results = []

        for contract in self.contracts:
            result = await self._validate_single_contract(base_url, contract)
            results.append(result)

        return results

    async def _validate_single_contract(
        self, base_url: str, contract: APIContract
    ) -> dict[str, Any]:
        """Validate a single API contract"""

        url = f"{base_url.rstrip('/')}/{contract.endpoint.lstrip('/')}"

        try:
            # Prepare request
            headers = {"Content-Type": "application/json"}
            headers.update(contract.headers)

            # Make request based on method
            if contract.method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif contract.method.upper() == "POST":
                # Use sample data from request schema
                sample_data = self._generate_sample_from_schema(contract.request_schema)
                response = requests.post(url, json=sample_data, headers=headers, timeout=30)
            else:
                return {
                    "contract": contract.endpoint,
                    "success": False,
                    "error": f"Unsupported method: {contract.method}",
                }

            # Validate status code
            if response.status_code not in contract.status_codes:
                return {
                    "contract": contract.endpoint,
                    "success": False,
                    "error": f"Unexpected status code: {response.status_code}",
                }

            # Validate response schema
            try:
                response_json = response.json()
                validate(instance=response_json, schema=contract.response_schema)

                return {
                    "contract": contract.endpoint,
                    "success": True,
                    "status_code": response.status_code,
                    "response_valid": True,
                }

            except ValidationError as e:
                return {
                    "contract": contract.endpoint,
                    "success": False,
                    "error": f"Response schema validation failed: {e.message}",
                }

        except Exception as e:
            return {"contract": contract.endpoint, "success": False, "error": str(e)}

    def _generate_sample_from_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Generate sample data from JSON schema"""

        sample = {}

        properties = schema.get("properties", {})

        for field, field_schema in properties.items():
            field_type = field_schema.get("type", "string")

            if field_type == "string":
                sample[field] = "test_value"
            elif field_type == "integer":
                sample[field] = 123
            elif field_type == "number":
                sample[field] = 123.45
            elif field_type == "boolean":
                sample[field] = True
            elif field_type == "array":
                sample[field] = []
            elif field_type == "object":
                sample[field] = {}

        return sample


class CICDPipelineManager:
    """CI/CD pipeline configuration and management"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.github_workflows_dir = project_root / ".github" / "workflows"

    def create_github_actions_workflow(self) -> Path:
        """Create comprehensive GitHub Actions workflow"""

        workflow = {
            "name": "EQ12 CI/CD Pipeline",
            "on": {
                "push": {"branches": ["main", "develop"]},
                "pull_request": {"branches": ["main"]},
            },
            "jobs": {
                "test-python": {
                    "runs-on": "ubuntu-latest",
                    "strategy": {"matrix": {"python-version": ["3.9", "3.10", "3.11", "3.12"]}},
                    "steps": [
                        {"uses": "actions/checkout@v4"},
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {"python-version": "${{ matrix.python-version }}"},
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt pytest pytest-cov",
                        },
                        {
                            "name": "Run tests",
                            "run": "pytest --cov=eq12 --cov-report=xml",
                        },
                        {
                            "name": "Upload coverage",
                            "uses": "codecov/codecov-action@v3",
                        },
                    ],
                },
                "test-nodejs": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v4"},
                        {
                            "name": "Setup Node.js",
                            "uses": "actions/setup-node@v3",
                            "with": {"node-version": "18"},
                        },
                        {"name": "Install dependencies", "run": "npm ci"},
                        {"name": "Run tests", "run": "npm test -- --coverage"},
                    ],
                },
                "contract-testing": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v4"},
                        {
                            "name": "Run contract tests",
                            "run": "python -m eq12_testing_cicd_innovation --contract-tests",
                        },
                    ],
                },
            },
        }

        # Ensure directory exists
        self.github_workflows_dir.mkdir(parents=True, exist_ok=True)

        workflow_path = self.github_workflows_dir / "ci.yml"
        workflow_path.write_text(yaml.dump(workflow, default_flow_style=False), encoding="utf-8")

        return workflow_path


async def main():
    """Demonstrate testing and CI/CD innovation"""

    setup_utf8_logging()
    logging.info("🧪 Starting Testing & CI/CD Innovation System")

    project_root = Path("C:/EQ12")

    # Initialize environment manager
    env_manager = TestEnvironmentManager(project_root)

    # Setup test environments
    print("🔧 Setting up test environments...")

    await env_manager.setup_python_test_environment()
    print("  Python/Pytest: {'✅' if python_setup else '❌'}")

    await env_manager.setup_nodejs_test_environment()
    print("  Node.js/Jest: {'✅' if nodejs_setup else '❌'}")

    # Create configuration files
    env_manager.create_pytest_config()
    env_manager.create_jest_config()

    print("✅ Configuration files created:")
    print("  - {pytest_config}")
    print("  - {jest_config}")

    # Initialize test runner
    TestRunner(env_manager)

    # Setup contract testing
    contract_tester = ContractTester()

    # Add sample contracts
    sample_contract = APIContract(
        endpoint="/api/health",
        method="GET",
        request_schema={},
        response_schema={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "timestamp": {"type": "string"},
            },
            "required": ["status"],
        },
        status_codes=[200],
    )

    contract_tester.add_contract(sample_contract)
    print(f"📋 Contract testing configured with {len(contract_tester.contracts)} contracts")

    # Setup CI/CD pipeline
    pipeline_manager = CICDPipelineManager(project_root)
    pipeline_manager.create_github_actions_workflow()
    print("🚀 CI/CD workflow created: {workflow_path}")

    print("\n🎉 Testing & CI/CD Innovation System Ready!")


if __name__ == "__main__":
    asyncio.run(main())
