#!/usr/bin/env python3
"""
 EQ12 BETTING SUITE - Complete Autonomous Betting Stack Executor


Master orchestrator that runs the complete EQ12 betting pipeline:
run-odds  social_intelligence  ai_predictions  run-parlay  revenue_update

Generates nightly dashboard, Telegram summaries, and profit reports.

Author: EQ12 Quantum Development Team
Version: 2.0.0 - Godlike Edition  
Date: November 7, 2025
"""

import os
import sys
import subprocess
import time
import logging
import json
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Add EQ12 modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class EQ12BettingSuite:
    def __init__(self, workspace_path="C:/EQ12"):
        self.workspace = workspace_path
        self.log_path = f"{workspace_path}/logs/eq12_betting_suite_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            handlers=[
                logging.FileHandler(self.log_path, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Define execution modules
        self.modules = {
            'odds_engine': f"{workspace_path}/scripts/eq12_run_odds.py",
            'social_intelligence': f"{workspace_path}/eq12_social_master_integrator.py",
            'parlay_engine': f"{workspace_path}/scripts/eq12_run_parlay.py",
            'revenue_updater': f"{workspace_path}/scripts/eq12_revenue_updater.py",
            'dashboard_generator': f"{workspace_path}/scripts/eq12_dashboard_generator.py"
        }
        
        self.execution_stats = {
            'start_time': None,
            'end_time': None,
            'modules_executed': 0,
            'modules_failed': 0,
            'total_runtime': 0,
            'errors': []
        }
        
    def execute_module(self, module_name: str, module_path: str, args: list = None) -> bool:
        """Execute a single module with error handling"""
        self.logger.info(f" Executing {module_name}...")
        
        try:
            if not os.path.exists(module_path):
                self.logger.warning(f" Module not found: {module_path}")
                return False
                
            # Prepare command
            cmd = ["python", module_path]
            if args:
                cmd.extend(args)
                
            # Execute module
            start_time = time.time()
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=self.workspace,
                timeout=300  # 5 minute timeout per module
            )
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                self.logger.info(f" {module_name} completed successfully ({execution_time:.1f}s)")
                return True
            else:
                self.logger.error(f" {module_name} failed: {result.stderr}")
                self.execution_stats['errors'].append({
                    'module': module_name,
                    'error': result.stderr,
                    'stdout': result.stdout
                })
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f" {module_name} timed out (5 minutes)")
            return False
        except Exception as e:
            self.logger.error(f" {module_name} exception: {e}")
            self.execution_stats['errors'].append({
                'module': module_name,
                'error': str(e)
            })
            return False
            
    def run_full_pipeline(self):
        """Execute complete betting pipeline"""
        self.logger.info(" Starting EQ12 Complete Betting Suite...")
        self.execution_stats['start_time'] = datetime.now()
        
        # Phase 1: Data Collection
        self.logger.info(" PHASE 1: Data Collection & Market Intelligence")
        
        success = self.execute_module(
            'odds_engine', 
            self.modules['odds_engine'],
            ['--mode', 'single', '--verbose']
        )
        if success:
            self.execution_stats['modules_executed'] += 1
        else:
            self.execution_stats['modules_failed'] += 1
            
        # Phase 2: Social Intelligence (if available)
        self.logger.info(" PHASE 2: Social Intelligence Analysis")
        
        if os.path.exists(self.modules['social_intelligence']):
            success = self.execute_module(
                'social_intelligence',
                self.modules['social_intelligence']
            )
            if success:
                self.execution_stats['modules_executed'] += 1
            else:
                self.execution_stats['modules_failed'] += 1
        else:
            self.logger.warning(" Social intelligence module not available")
            
        # Phase 3: Parlay Generation
        self.logger.info(" PHASE 3: AI Parlay Construction")
        
        success = self.execute_module(
            'parlay_engine',
            self.modules['parlay_engine'], 
            ['--legs', '5', '--count', '3', '--verbose']
        )
        if success:
            self.execution_stats['modules_executed'] += 1
        else:
            self.execution_stats['modules_failed'] += 1
            
        # Phase 4: Revenue Optimization
        self.logger.info(" PHASE 4: Revenue Cycle Optimization")
        
        if os.path.exists(self.modules['revenue_updater']):
            success = self.execute_module(
                'revenue_updater',
                self.modules['revenue_updater'],
                ['--verbose']
            )
            if success:
                self.execution_stats['modules_executed'] += 1
            else:
                self.execution_stats['modules_failed'] += 1
        else:
            self.logger.warning(" Revenue updater module not available")
            
        # Phase 5: Dashboard & Reporting
        self.logger.info(" PHASE 5: Dashboard Generation & Reporting")
        
        if os.path.exists(self.modules['dashboard_generator']):
            success = self.execute_module(
                'dashboard_generator',
                self.modules['dashboard_generator'],
                ['--full-strategy', '--verbose']
            )
            if success:
                self.execution_stats['modules_executed'] += 1
            else:
                self.execution_stats['modules_failed'] += 1
        else:
            self.logger.warning(" Dashboard generator module not available")
            
        # Finalize execution
        self.execution_stats['end_time'] = datetime.now()
        self.execution_stats['total_runtime'] = (
            self.execution_stats['end_time'] - self.execution_stats['start_time']
        ).total_seconds()
        
        self.generate_execution_summary()
        
    def run_parallel_pipeline(self):
        """Execute pipeline with parallel processing where possible"""
        self.logger.info(" Starting EQ12 Parallel Betting Suite...")
        self.execution_stats['start_time'] = datetime.now()
        
        # Phase 1: Parallel data collection
        self.logger.info(" PHASE 1: Parallel Data Collection")
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Run odds and social intelligence in parallel
            futures = {}
            
            futures['odds'] = executor.submit(
                self.execute_module,
                'odds_engine',
                self.modules['odds_engine'], 
                ['--mode', 'single', '--verbose']
            )
            
            if os.path.exists(self.modules['social_intelligence']):
                futures['social'] = executor.submit(
                    self.execute_module,
                    'social_intelligence',
                    self.modules['social_intelligence']
                )
                
            # Wait for completion
            for task_name, future in futures.items():
                try:
                    success = future.result(timeout=300)
                    if success:
                        self.execution_stats['modules_executed'] += 1
                    else:
                        self.execution_stats['modules_failed'] += 1
                except Exception as e:
                    self.logger.error(f" Parallel task {task_name} failed: {e}")
                    self.execution_stats['modules_failed'] += 1
                    
        # Phase 2: Sequential processing (depends on data)
        self.logger.info(" PHASE 2: Sequential AI Processing")
        
        # Wait a moment for data to be written
        time.sleep(2)
        
        # Generate parlays
        success = self.execute_module(
            'parlay_engine',
            self.modules['parlay_engine'],
            ['--legs', '7', '--count', '2', '--verbose']
        )
        if success:
            self.execution_stats['modules_executed'] += 1
        else:
            self.execution_stats['modules_failed'] += 1
            
        # Phase 3: Final reporting
        self.logger.info(" PHASE 3: Final Processing & Reports")
        
        # Revenue and dashboard in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {}
            
            if os.path.exists(self.modules['revenue_updater']):
                futures['revenue'] = executor.submit(
                    self.execute_module,
                    'revenue_updater',
                    self.modules['revenue_updater'],
                    ['--verbose']
                )
                
            if os.path.exists(self.modules['dashboard_generator']):
                futures['dashboard'] = executor.submit(
                    self.execute_module,
                    'dashboard_generator', 
                    self.modules['dashboard_generator'],
                    ['--full-strategy', '--verbose']
                )
                
            # Wait for completion
            for task_name, future in futures.items():
                try:
                    success = future.result(timeout=300)
                    if success:
                        self.execution_stats['modules_executed'] += 1
                    else:
                        self.execution_stats['modules_failed'] += 1
                except Exception as e:
                    self.logger.error(f" Final task {task_name} failed: {e}")
                    self.execution_stats['modules_failed'] += 1
                    
        # Finalize
        self.execution_stats['end_time'] = datetime.now()
        self.execution_stats['total_runtime'] = (
            self.execution_stats['end_time'] - self.execution_stats['start_time']
        ).total_seconds()
        
        self.generate_execution_summary()
        
    def generate_execution_summary(self):
        """Generate comprehensive execution summary"""
        success_rate = (
            self.execution_stats['modules_executed'] / 
            (self.execution_stats['modules_executed'] + self.execution_stats['modules_failed']) * 100
            if (self.execution_stats['modules_executed'] + self.execution_stats['modules_failed']) > 0 
            else 0
        )
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "execution_stats": self.execution_stats,
            "success_rate": round(success_rate, 1),
            "runtime_minutes": round(self.execution_stats['total_runtime'] / 60, 2)
        }
        
        # Save summary
        summary_path = f"{self.workspace}/logs/betting_suite_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
            
        # Console output
        print(f"""

 EQ12 BETTING SUITE EXECUTION COMPLETE
{'='*50}
 Total Runtime: {summary['runtime_minutes']:.2f} minutes
 Modules Executed: {self.execution_stats['modules_executed']}
 Modules Failed: {self.execution_stats['modules_failed']}
 Success Rate: {success_rate:.1f}%

 Summary saved: {summary_path}
 Detailed logs: {self.log_path}
""")
        
        if self.execution_stats['errors']:
            print(" ERRORS ENCOUNTERED:")
            for i, error in enumerate(self.execution_stats['errors'], 1):
                print(f"  {i}. {error['module']}: {error['error'][:100]}...")
                
        self.logger.info(f" Betting Suite complete - {success_rate:.1f}% success rate")

def main():
    parser = argparse.ArgumentParser(description='EQ12 Betting Suite - Complete Autonomous Pipeline')
    parser.add_argument('--mode', choices=['sequential', 'parallel'], default='sequential',
                       help='Execution mode: sequential or parallel processing')
    parser.add_argument('--workspace', default='C:/EQ12',
                       help='EQ12 workspace path')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    suite = EQ12BettingSuite(args.workspace)
    
    if args.mode == 'parallel':
        suite.run_parallel_pipeline()
    else:
        suite.run_full_pipeline()

if __name__ == "__main__":
    main()