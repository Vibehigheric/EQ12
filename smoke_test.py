#!/usr/bin/env python3
"""
EQ12 Smoke Test Suite - GitHub Pro Optimized
Validates core betting automation functionality for CI/CD pipeline
Designed to run in GitHub Actions, Codespaces, and local environments
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path


# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m' 
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_colored(message: str, color: str = Colors.WHITE) -> None:
    """Print colored message to terminal"""
    print(f"{color}{message}{Colors.RESET}")

def print_header(title: str) -> None:
    """Print formatted section header"""
    print_colored(f"\n{'='*60}", Colors.CYAN)
    print_colored(f"🧪 {title}", Colors.BOLD + Colors.CYAN)
    print_colored(f"{'='*60}", Colors.CYAN)

def check_environment() -> bool:
    """Verify EQ12 directory structure and environment setup"""
    print_header("ENVIRONMENT VALIDATION")
    
    required_dirs = [
        "scripts", "tests", "logs", "data", ".github", ".vscode"
    ]
    
    optional_dirs = [
        "dashboard", "configs", ".devcontainer"
    ]
    
    all_good = True
    
    # Check required directories
    print_colored("📁 Checking required directories:", Colors.YELLOW)
    for dir_name in required_dirs:
        path = Path(dir_name)
        if path.exists():
            print_colored(f"  ✅ {dir_name}/", Colors.GREEN)
        else:
            print_colored(f"  ❌ {dir_name}/ (REQUIRED)", Colors.RED)
            all_good = False
    
    # Check optional directories
    print_colored("\n📁 Checking optional directories:", Colors.YELLOW)
    for dir_name in optional_dirs:
        path = Path(dir_name)
        if path.exists():
            print_colored(f"  ✅ {dir_name}/", Colors.GREEN)
        else:
            print_colored(f"  ⚪ {dir_name}/ (optional)", Colors.YELLOW)
    
    # Check environment variables
    print_colored("\n🔑 Checking environment configuration:", Colors.YELLOW)
    env_vars = {
        "EQ12_ENVIRONMENT": os.getenv("EQ12_ENVIRONMENT", "unknown"),
        "PYTHON_VERSION": f"{sys.version_info.major}.{sys.version_info.minor}",
        "CODESPACES": "Yes" if os.getenv("CODESPACES") else "No",
        "GITHUB_ACTIONS": "Yes" if os.getenv("GITHUB_ACTIONS") else "No"
    }
    
    for var, value in env_vars.items():
        print_colored(f"  ℹ️  {var}: {value}", Colors.BLUE)
    
    return all_good

def check_dependencies() -> bool:
    """Verify core Python dependencies are installed"""
    print_header("DEPENDENCY VALIDATION")
    
    required_packages = [
        ("requests", "HTTP client for API calls"),
        ("pandas", "Data manipulation and analysis"),
        ("numpy", "Numerical computing"),
        ("aiohttp", "Async HTTP client"),
    ]
    
    optional_packages = [
        ("fastapi", "API framework"),
        ("jupyter", "Interactive notebooks"),
        ("black", "Code formatter"),
        ("ruff", "Fast Python linter"),
        ("pytest", "Testing framework")
    ]
    
    all_good = True
    
    # Check required packages
    print_colored("📦 Checking required packages:", Colors.YELLOW)
    for package, description in required_packages:
        try:
            __import__(package)
            print_colored(f"  ✅ {package:<12} - {description}", Colors.GREEN)
        except ImportError:
            print_colored(f"  ❌ {package:<12} - {description} (REQUIRED)", Colors.RED)
            all_good = False
    
    # Check optional packages
    print_colored("\n📦 Checking optional packages:", Colors.YELLOW)
    for package, description in optional_packages:
        try:
            __import__(package)
            print_colored(f"  ✅ {package:<12} - {description}", Colors.GREEN)
        except ImportError:
            print_colored(f"  ⚪ {package:<12} - {description} (optional)", Colors.YELLOW)
    
    return all_good

async def test_api_connectivity() -> bool:
    """Test basic API connectivity and HTTP client setup"""
    print_header("API CONNECTIVITY TEST")
    
    try:
        import aiohttp
        print_colored("📡 Testing HTTP client functionality:", Colors.YELLOW)
        
        # Test basic HTTP connectivity
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("https://httpbin.org/get", timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print_colored("  ✅ HTTP GET request successful", Colors.GREEN)
                        print_colored(f"  ℹ️  Response from: {data.get('origin', 'unknown')}", Colors.BLUE)
                    else:
                        print_colored(f"  ❌ HTTP request failed: {resp.status}", Colors.RED)
                        return False
            except TimeoutError:
                print_colored("  ❌ HTTP request timeout", Colors.RED)
                return False
            except Exception as e:
                print_colored(f"  ❌ HTTP client error: {e}", Colors.RED)
                return False
        
        # Test API key format validation (without actual API calls)
        print_colored("\n🔑 Testing API key format validation:", Colors.YELLOW)
        api_keys = {
            "THE_ODDS_API_KEY": os.getenv("THE_ODDS_API_KEY"),
            "CFBD_API_KEY": os.getenv("CFBD_API_KEY"),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
        }
        
        for key_name, key_value in api_keys.items():
            if key_value and key_value != f"your_{key_name.lower()}_here":
                print_colored(f"  ✅ {key_name} configured", Colors.GREEN)
            else:
                print_colored(f"  ⚪ {key_name} not configured (expected in CI/production)", Colors.YELLOW)
        
        return True
        
    except ImportError:
        print_colored("❌ aiohttp not available - cannot test API connectivity", Colors.RED)
        return False

def test_file_operations() -> bool:
    """Test file I/O operations for logs and data"""
    print_header("FILE OPERATIONS TEST")
    
    print_colored("📝 Testing file operations:", Colors.YELLOW)
    
    try:
        # Test log directory creation and writing
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        test_log_file = log_dir / "smoke_test.log"
        test_data = {
            "timestamp": time.time(),
            "test": "smoke_test",
            "environment": os.getenv("EQ12_ENVIRONMENT", "unknown"),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        }
        
        # Write JSON log
        with open(test_log_file, "w") as f:
            json.dump(test_data, f, indent=2)
        
        print_colored("  ✅ Log file creation successful", Colors.GREEN)
        
        # Read and validate
        with open(test_log_file) as f:
            loaded_data = json.load(f)
        
        if loaded_data["test"] == "smoke_test":
            print_colored("  ✅ Log file read/write validation successful", Colors.GREEN)
        else:
            print_colored("  ❌ Log file validation failed", Colors.RED)
            return False
        
        # Test data directory
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        print_colored("  ✅ Data directory access successful", Colors.GREEN)
        
        # Cleanup test file
        test_log_file.unlink(missing_ok=True)
        print_colored("  ✅ File cleanup successful", Colors.GREEN)
        
        return True
        
    except Exception as e:
        print_colored(f"  ❌ File operations error: {e}", Colors.RED)
        return False

def test_betting_logic_imports() -> bool:
    """Test that core EQ12 betting modules can be imported"""
    print_header("BETTING LOGIC VALIDATION")
    
    print_colored("🎯 Testing EQ12 module imports:", Colors.YELLOW)
    
    # Common EQ12 scripts that should be importable
    eq12_modules = [
        "scripts.eq12_main",
        "scripts.aligned_model", 
        "scripts.eq12_sports_parlay_analyzer"
    ]
    
    importable_count = 0
    
    for module_name in eq12_modules:
        try:
            # Add scripts directory to path if not already there
            scripts_path = Path("scripts").resolve()
            if str(scripts_path) not in sys.path:
                sys.path.insert(0, str(scripts_path))
            
            # Try importing the module
            module_parts = module_name.split(".")
            if len(module_parts) > 1:
                # Try importing just the script name
                script_name = module_parts[-1]
                __import__(script_name)
                print_colored(f"  ✅ {script_name}", Colors.GREEN)
                importable_count += 1
            else:
                __import__(module_name)
                print_colored(f"  ✅ {module_name}", Colors.GREEN)
                importable_count += 1
                
        except ImportError as e:
            print_colored(f"  ⚪ {module_name.split('.')[-1]} - {str(e)[:50]}...", Colors.YELLOW)
        except Exception as e:
            print_colored(f"  ❌ {module_name.split('.')[-1]} - {str(e)[:50]}...", Colors.RED)
    
    # Consider it successful if at least some modules import
    success_rate = importable_count / len(eq12_modules)
    print_colored(f"\n📊 Module import success rate: {importable_count}/{len(eq12_modules)} ({success_rate:.1%})", Colors.BLUE)
    
    return success_rate > 0.3  # At least 30% of modules should import

def run_performance_check() -> bool:
    """Run basic performance validation"""
    print_header("PERFORMANCE VALIDATION")
    
    print_colored("⚡ Running performance checks:", Colors.YELLOW)
    
    try:
        import sys
        import time

        # Python startup time check
        start_time = time.time()
        import numpy as np
        import pandas as pd
        end_time = time.time()
        
        import_time = end_time - start_time
        print_colored(f"  📊 Pandas/NumPy import time: {import_time:.2f}s", Colors.BLUE)
        
        if import_time > 5.0:
            print_colored("  ⚠️  Import time is slow (>5s) - consider optimizing", Colors.YELLOW)
        else:
            print_colored("  ✅ Import time acceptable", Colors.GREEN)
        
        # Memory usage check
        import os

        import psutil
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        print_colored(f"  🧠 Memory usage: {memory_mb:.1f} MB", Colors.BLUE)
        
        if memory_mb > 500:
            print_colored("  ⚠️  High memory usage (>500MB) - monitor in production", Colors.YELLOW)
        else:
            print_colored("  ✅ Memory usage acceptable", Colors.GREEN)
        
        return True
        
    except ImportError:
        print_colored("  ⚪ psutil not available - skipping memory check", Colors.YELLOW)
        return True
    except Exception as e:
        print_colored(f"  ❌ Performance check error: {e}", Colors.RED)
        return False

async def main() -> int:
    """Run all smoke tests and return exit code"""
    print_colored(f"{Colors.BOLD}🚀 EQ12 SMOKE TEST SUITE - GITHUB PRO OPTIMIZED{Colors.RESET}", Colors.CYAN)
    print_colored(f"Environment: {os.getenv('EQ12_ENVIRONMENT', 'unknown')}", Colors.BLUE)
    print_colored(f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", Colors.BLUE)
    print_colored(f"Platform: {sys.platform}", Colors.BLUE)
    
    # Define all tests
    tests = [
        ("Environment Setup", check_environment),
        ("Dependencies", check_dependencies),
        ("API Connectivity", test_api_connectivity),
        ("File Operations", test_file_operations),
        ("Betting Logic", test_betting_logic_imports),
        ("Performance", run_performance_check)
    ]
    
    results = []
    start_time = time.time()
    
    # Run each test
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
            
            status_color = Colors.GREEN if result else Colors.RED
            status_text = "✅ PASS" if result else "❌ FAIL"
            print_colored(f"\n{status_text}: {test_name}", status_color)
            
        except Exception as e:
            print_colored(f"\n❌ ERROR in {test_name}: {e}", Colors.RED)
            results.append((test_name, False))
    
    # Final summary
    total_time = time.time() - start_time
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print_header("SMOKE TEST SUMMARY")
    
    for test_name, result in results:
        status_icon = "✅" if result else "❌"
        color = Colors.GREEN if result else Colors.RED
        print_colored(f"  {status_icon} {test_name}", color)
    
    print_colored(f"\n📊 Results: {passed}/{total} tests passed", Colors.BLUE)
    print_colored(f"⏱️  Total time: {total_time:.2f}s", Colors.BLUE)
    
    if passed == total:
        print_colored("\n🎉 ALL TESTS PASSED! EQ12 stack is ready for betting automation! 🎯", Colors.GREEN + Colors.BOLD)
        return 0
    elif passed >= total * 0.7:  # 70% pass rate
        print_colored(f"\n⚠️  PARTIAL SUCCESS: {passed}/{total} tests passed (70%+ threshold met)", Colors.YELLOW + Colors.BOLD)
        print_colored("🔧 Some optional features may not be available", Colors.YELLOW)
        return 0
    else:
        print_colored(f"\n❌ TESTS FAILED: Only {passed}/{total} tests passed", Colors.RED + Colors.BOLD)
        print_colored("🚨 EQ12 stack needs attention before production use", Colors.RED)
        return 1

if __name__ == "__main__":
    # Handle async main properly
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_colored("\n🛑 Tests interrupted by user", Colors.YELLOW)
        sys.exit(130)
    except Exception as e:
        print_colored(f"\n💥 Unexpected error: {e}", Colors.RED)
        sys.exit(1)