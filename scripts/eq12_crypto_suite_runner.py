#!/usr/bin/env python3
"""
 EQ12 COMPREHENSIVE CRYPTO SUITE RUNNER
Master launcher for all cryptocurrency programs in the EQ12 ecosystem
Runs ALL crypto programs: AI, arbitrage bots, data streams, and analysis tools
"""

import os
import sys
import json
import time
import logging
import asyncio
import subprocess
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed


class EQ12CryptoSuiteRunner:
    """
     Master orchestrator for ALL EQ12 cryptocurrency programs
    Launches and manages the complete crypto ecosystem
    """
    
    def __init__(self, verbose: bool = False):
        self.setup_logging(verbose)
        
        # System paths
        self.workspace_path = Path("C:/EQ12")
        self.scripts_path = self.workspace_path / "scripts"
        self.logs_path = self.workspace_path / "logs" / "crypto_suite"
        
        # Create directories
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
        # Program registry
        self.crypto_programs = self._discover_crypto_programs()
        self.running_processes = {}
        self.execution_results = {}
        
        # Performance metrics
        self.start_time = None
        self.total_programs = 0
        self.successful_launches = 0
        
        self.logger.info(" EQ12 Crypto Suite Runner initialized")
        
    def setup_logging(self, verbose: bool = False):
        """Setup comprehensive logging"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"C:/EQ12/logs/crypto_suite_runner_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        
    def _discover_crypto_programs(self) -> Dict[str, Dict[str, Any]]:
        """Discover all cryptocurrency programs in the EQ12 system"""
        
        programs = {}
        
        # Python crypto programs
        python_programs = {
            "coral_crypto_ai": {
                "path": self.scripts_path / "eq12_coral_crypto_ai.py",
                "type": "python",
                "args": ["--start-analysis", "--verbose"],
                "description": "Coral Edge TPU Crypto AI Engine",
                "category": "ai_analysis",
                "priority": 1
            },
            "crypto_stream": {
                "path": self.scripts_path / "eq12_crypto_stream.py", 
                "type": "python",
                "args": ["--start-streaming", "--verbose"],
                "description": "Real-time Crypto Data Stream Collector",
                "category": "data_feed",
                "priority": 2
            },
            "coral_crypto_master": {
                "path": self.scripts_path / "eq12_coral_crypto_master.py",
                "type": "python", 
                "args": ["--action", "start", "--verbose"],
                "description": "Coral Crypto Master Orchestrator",
                "category": "orchestration",
                "priority": 0
            }
        }
        
        # Node.js crypto programs (Solana arbitrage bots)
        nodejs_programs = {
            "solana_jupiter_arb": {
                "path": self.workspace_path / "data/github_repos/ARBProtocol_solana-jupiter-bot",
                "type": "nodejs",
                "command": "node src/index.js",
                "description": "ARBProtocol Solana Jupiter Arbitrage Bot",
                "category": "arbitrage",
                "priority": 3,
                "requires_config": True
            },
            "solana_lane_arb": {
                "path": self.workspace_path / "data/github_repos/LaneOlsons_solana-arbitrage-bot",
                "type": "nodejs", 
                "command": "node src/index.js",
                "description": "LaneOlsons Solana Arbitrage Bot",
                "category": "arbitrage",
                "priority": 4,
                "requires_config": True
            },
            "uniswap_sushi_arb": {
                "path": self.workspace_path / "data/github_repos/6eer_uniswap-sushiswap-arbitrage-bot",
                "type": "nodejs",
                "command": "node src/bot_flashswap.js",
                "description": "Uniswap-Sushiswap Flashswap Arbitrage Bot",
                "category": "arbitrage", 
                "priority": 5,
                "requires_config": True
            }
        }
        
        # PowerShell programs
        powershell_programs = {
            "coral_crypto_wrapper": {
                "path": self.scripts_path / "eq12_coral_crypto_wrapper.ps1",
                "type": "powershell",
                "args": ["-Action", "StartAll", "-Verbose"],
                "description": "Coral Crypto PowerShell Wrapper",
                "category": "wrapper",
                "priority": 6
            }
        }
        
        # Combine all programs
        programs.update(python_programs)
        programs.update(nodejs_programs)
        programs.update(powershell_programs)
        
        # Filter to only existing programs
        existing_programs = {}
        for name, config in programs.items():
            if config["path"].exists():
                existing_programs[name] = config
            else:
                self.logger.warning(f"Program not found: {config['path']}")
                
        self.logger.info(f"Discovered {len(existing_programs)} crypto programs")
        return existing_programs
        
    def run_all_crypto_programs(self) -> Dict[str, Any]:
        """Launch ALL cryptocurrency programs in the EQ12 system"""
        
        self.logger.info(" LAUNCHING ALL EQ12 CRYPTO PROGRAMS!")
        self.logger.info("=" * 60)
        
        self.start_time = time.time()
        self.total_programs = len(self.crypto_programs)
        
        # Sort programs by priority
        sorted_programs = sorted(
            self.crypto_programs.items(),
            key=lambda x: x[1]["priority"]
        )
        
        # Launch programs in parallel with some orchestration
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {}
            
            for name, config in sorted_programs:
                # Submit program for execution
                future = executor.submit(self._launch_program, name, config)
                futures[future] = name
                
                # Small delay between launches for stability
                time.sleep(2)
            
            # Collect results
            for future in as_completed(futures):
                program_name = futures[future]
                try:
                    result = future.result()
                    self.execution_results[program_name] = result
                    
                    if result["success"]:
                        self.successful_launches += 1
                        self.logger.info(f" {program_name}: {result['message']}")
                    else:
                        self.logger.error(f" {program_name}: {result['message']}")
                        
                except Exception as e:
                    self.logger.error(f" {program_name} failed with exception: {e}")
                    self.execution_results[program_name] = {
                        "success": False,
                        "message": f"Exception: {e}",
                        "process_id": None
                    }
        
        # Generate comprehensive report
        return self._generate_execution_report()
        
    def _launch_program(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Launch a single crypto program"""
        
        try:
            self.logger.info(f" Launching {config['description']}...")
            
            if config["type"] == "python":
                return self._launch_python_program(name, config)
            elif config["type"] == "nodejs":
                return self._launch_nodejs_program(name, config)
            elif config["type"] == "powershell":
                return self._launch_powershell_program(name, config)
            else:
                return {
                    "success": False,
                    "message": f"Unknown program type: {config['type']}",
                    "process_id": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Launch failed: {e}",
                "process_id": None
            }
            
    def _launch_python_program(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Launch Python crypto program"""
        
        try:
            cmd = ["python", str(config["path"])] + config.get("args", [])
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.scripts_path)
            )
            
            # Store process reference
            self.running_processes[name] = process
            
            # Give it a moment to start
            time.sleep(3)
            
            # Check if still running
            if process.poll() is None:
                return {
                    "success": True,
                    "message": f"Started successfully (PID: {process.pid})",
                    "process_id": process.pid
                }
            else:
                stdout, stderr = process.communicate()
                return {
                    "success": False,
                    "message": f"Process exited early. STDERR: {stderr[:200]}",
                    "process_id": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Python launch failed: {e}",
                "process_id": None
            }
            
    def _launch_nodejs_program(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Launch Node.js crypto program"""
        
        try:
            # Change to program directory
            cwd = str(config["path"])
            
            # Check if package.json exists
            package_json = config["path"] / "package.json"
            if not package_json.exists():
                return {
                    "success": False,
                    "message": f"package.json not found in {cwd}",
                    "process_id": None
                }
            
            # Ensure dependencies are installed
            self.logger.info(f"Ensuring npm dependencies for {name}...")
            npm_cmd = r"C:\Program Files\nodejs\npm.cmd"
            npm_install = subprocess.run(
                [npm_cmd, "install", "--silent"],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Enhanced execution strategies based on bot type and available scripts
            cmd = self._determine_best_command(config, cwd)
            
            self.logger.info(f"Launching {name} with command: {' '.join(cmd)} in {cwd}")
            
            # Launch with proper environment
            env = os.environ.copy()
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd,
                env=env
            )
            
            self.running_processes[name] = process
            
            # Give it time to start and check for immediate failures
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                return {
                    "success": True,
                    "message": f"Node.js program started successfully (PID: {process.pid})",
                    "process_id": process.pid
                }
            else:
                # Process exited, get error details
                try:
                    stdout, stderr = process.communicate(timeout=5)
                    error_msg = stderr[:500] if stderr else stdout[:500]
                    return {
                        "success": False,
                        "message": f"Process exited immediately. Error: {error_msg}",
                        "process_id": None
                    }
                except subprocess.TimeoutExpired:
                    return {
                        "success": False,
                        "message": "Process communication timeout",
                        "process_id": None
                    }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "npm install timeout (300s)",
                "process_id": None
            }
        except FileNotFoundError as e:
            return {
                "success": False,
                "message": f"File not found: {e}. Check Node.js installation.",
                "process_id": None
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Launch failed: {str(e)}",
                "process_id": None
            }
    
    def _determine_best_command(self, config: Dict[str, Any], cwd: str) -> List[str]:
        """Determine the best command to run a Node.js bot."""
        import json
        
        # Try to read package.json for scripts
        package_json_path = Path(cwd) / "package.json"
        scripts = {}
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                scripts = package_data.get('scripts', {})
            except:
                pass
        
        # Strategy 1: Use npm scripts if available (with full path)
        npm_cmd = r"C:\Program Files\nodejs\npm.cmd"
        if 'wizard' in scripts:
            return [npm_cmd, "run", "wizard"]
        elif 'start' in scripts:
            return [npm_cmd, "run", "start"]
        elif 'trade' in scripts:
            return [npm_cmd, "run", "trade"]
        
        # Strategy 2: Direct node execution with full path
        node_cmd = r"C:\Program Files\nodejs\node.exe"
        npx_cmd = r"C:\Program Files\nodejs\npx.cmd"
        path_str = str(config["path"])
        
        if "solana-jupiter-bot" in path_str:
            return [node_cmd, "--no-deprecation", "src/index.js"]
        elif "solana-arbitrage-bot" in path_str:
            return [node_cmd, "--no-deprecation", "src/index.js"]
        elif "uniswap-sushiswap" in path_str:
            # Check for available entry points
            src_dir = Path(cwd) / "src"
            if (src_dir / "bot_flashswap.js").exists():
                return [node_cmd, "src/bot_flashswap.js"]
            elif (src_dir / "index.js").exists():
                return [node_cmd, "src/index.js"]
            else:
                # Use truffle for Ethereum-based bots as fallback
                return [npx_cmd, "truffle", "console", "--network", "mainnet"]
        
        # Strategy 3: Default fallback
        return [node_cmd, "src/index.js"]
            
    def _launch_powershell_program(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Launch PowerShell crypto program"""
        
        try:
            cmd = [
                "powershell",
                "-ExecutionPolicy", "Bypass",
                "-File", str(config["path"])
            ] + config.get("args", [])
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.scripts_path)
            )
            
            self.running_processes[name] = process
            
            # PowerShell programs might exit quickly
            time.sleep(2)
            
            return {
                "success": True,
                "message": f"PowerShell program executed (PID: {process.pid})",
                "process_id": process.pid
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"PowerShell launch failed: {e}",
                "process_id": None
            }
            
    def _generate_execution_report(self) -> Dict[str, Any]:
        """Generate comprehensive execution report"""
        
        execution_time = time.time() - self.start_time
        
        # Categorize results
        successful = [name for name, result in self.execution_results.items() if result["success"]]
        failed = [name for name, result in self.execution_results.items() if not result["success"]]
        
        # Create detailed report
        report = {
            "execution_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_programs": self.total_programs,
                "successful_launches": len(successful),
                "failed_launches": len(failed),
                "execution_time_seconds": execution_time,
                "success_rate": (len(successful) / self.total_programs) * 100 if self.total_programs > 0 else 0
            },
            "successful_programs": successful,
            "failed_programs": failed,
            "detailed_results": self.execution_results,
            "running_processes": {
                name: proc.pid for name, proc in self.running_processes.items() 
                if proc.poll() is None
            }
        }
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.logs_path / f"crypto_suite_execution_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.logger.info(f" Execution report saved: {report_file}")
        return report
        
    def get_running_status(self) -> Dict[str, Any]:
        """Get current status of all running crypto programs"""
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "running_programs": {},
            "total_running": 0
        }
        
        for name, process in self.running_processes.items():
            if process.poll() is None:
                status["running_programs"][name] = {
                    "pid": process.pid,
                    "status": "running",
                    "description": self.crypto_programs[name]["description"]
                }
                status["total_running"] += 1
            else:
                status["running_programs"][name] = {
                    "pid": process.pid,
                    "status": "stopped",
                    "exit_code": process.returncode
                }
                
        return status
        
    def stop_all_programs(self):
        """Stop all running crypto programs"""
        
        self.logger.info(" Stopping all crypto programs...")
        
        for name, process in self.running_processes.items():
            try:
                if process.poll() is None:
                    self.logger.info(f"Terminating {name} (PID: {process.pid})")
                    process.terminate()
                    
                    # Give it 5 seconds to terminate gracefully
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.logger.warning(f"Force killing {name}")
                        process.kill()
                        
            except Exception as e:
                self.logger.error(f"Error stopping {name}: {e}")
                
        self.logger.info(" All crypto programs stopped")


def main():
    """Main crypto suite runner"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Comprehensive Crypto Suite Runner")
    parser.add_argument("--action", choices=["run-all", "status", "stop-all"], 
                       default="run-all", help="Action to perform")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Create runner
    runner = EQ12CryptoSuiteRunner(verbose=args.verbose)
    
    print(" EQ12 COMPREHENSIVE CRYPTO SUITE RUNNER")
    print("=" * 50)
    print(f"Action: {args.action}")
    print(f"Discovered Programs: {len(runner.crypto_programs)}")
    print("=" * 50)
    
    if args.action == "run-all":
        print(" LAUNCHING ALL CRYPTOCURRENCY PROGRAMS!")
        print("This will start:")
        for name, config in runner.crypto_programs.items():
            print(f"   {config['description']} ({config['category']})")
        print()
        
        # Launch everything
        report = runner.run_all_crypto_programs()
        
        print("\n EXECUTION SUMMARY:")
        print(f"Total Programs: {report['execution_summary']['total_programs']}")
        print(f"Successful Launches: {report['execution_summary']['successful_launches']}")
        print(f"Failed Launches: {report['execution_summary']['failed_launches']}")
        print(f"Success Rate: {report['execution_summary']['success_rate']:.1f}%")
        print(f"Execution Time: {report['execution_summary']['execution_time_seconds']:.2f}s")
        
        print("\n SUCCESSFUL PROGRAMS:")
        for program in report['successful_programs']:
            print(f"   {program}")
            
        if report['failed_programs']:
            print("\n FAILED PROGRAMS:")
            for program in report['failed_programs']:
                print(f"   {program}")
                
        print(f"\n Full report saved to logs directory")
        
    elif args.action == "status":
        status = runner.get_running_status()
        
        print(f" CRYPTO PROGRAMS STATUS ({status['timestamp']})")
        print(f"Total Running: {status['total_running']}")
        print()
        
        for name, info in status['running_programs'].items():
            status_emoji = "" if info['status'] == 'running' else ""
            print(f"{status_emoji} {name}: {info['status']} (PID: {info['pid']})")
            
    elif args.action == "stop-all":
        runner.stop_all_programs()
        print(" All crypto programs stopped")


if __name__ == "__main__":
    main()