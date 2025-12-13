#!/usr/bin/env python3
"""
EQ12 NBA Cluster Manager
Orchestrates the complete NBA betting pipeline across EQ12 + Pi5 + Coral TPU cluster.
Coordinates data collection, feature engineering, TPU inference, and prop generation.
"""

import asyncio
import subprocess
import paramiko
import json
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import time
import threading
from dataclasses import dataclass
import psutil
import socket
import warnings
warnings.filterwarnings('ignore')

# EQ12 Cluster Configuration
CLUSTER_CONFIG = {
    "eq12_host": "192.168.100.1",
    "pi_host": "192.168.100.2", 
    "pi_user": "eq12",
    "ssh_key": "C:/Users/admin/.ssh/id_rsa",
    "data_dir": "C:/EQ12/data",
    "logs_dir": "C:/EQ12/logs",
    "scripts_dir": "C:/EQ12/scripts",
    "models_dir": "C:/EQ12/models",
    "cluster_mode": True
}


@dataclass
class ClusterStatus:
    """Cluster node status information"""
    eq12_online: bool
    pi_online: bool
    tpu_detected: bool
    data_synced: bool
    models_loaded: bool
    last_update: datetime


class EQ12_NBA_ClusterManager:
    """NBA Betting Cluster Orchestration Engine"""
    
    def __init__(self, config: Dict = None):
        self.config = config or CLUSTER_CONFIG
        self.setup_logging()
        self.ssh_client = None
        self.cluster_status = ClusterStatus(
            eq12_online=True,
            pi_online=False,
            tpu_detected=False,
            data_synced=False,
            models_loaded=False,
            last_update=datetime.now()
        )
        
    def setup_logging(self):
        """Initialize logging for cluster manager"""
        log_file = f"{self.config['logs_dir']}/nba_cluster_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def check_pi_connectivity(self) -> bool:
        """Check if Pi node is accessible via SSH"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                self.config['pi_host'], 
                username=self.config['pi_user'],
                key_filename=self.config['ssh_key'],
                timeout=10
            )
            
            # Test basic command
            stdin, stdout, stderr = ssh.exec_command("echo 'EQ12_CLUSTER_TEST'")
            result = stdout.read().decode().strip()
            
            ssh.close()
            
            if result == "EQ12_CLUSTER_TEST":
                self.cluster_status.pi_online = True
                return True
                
        except Exception as e:
            self.logger.warning(f" Pi connectivity check failed: {e}")
            
        self.cluster_status.pi_online = False
        return False
    
    def check_tpu_status(self) -> bool:
        """Check Coral TPU status on Pi"""
        
        if not self.cluster_status.pi_online:
            return False
            
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                self.config['pi_host'],
                username=self.config['pi_user'], 
                key_filename=self.config['ssh_key']
            )
            
            # Check for Coral TPU
            stdin, stdout, stderr = ssh.exec_command("lsusb | grep 1a6e:089a")
            tpu_output = stdout.read().decode().strip()
            
            ssh.close()
            
            tpu_detected = "1a6e:089a" in tpu_output
            self.cluster_status.tpu_detected = tpu_detected
            
            return tpu_detected
            
        except Exception as e:
            self.logger.error(f" TPU status check failed: {e}")
            return False
    
    def execute_on_pi(self, command: str, timeout: int = 60) -> Dict[str, any]:
        """Execute command on Pi node via SSH"""
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                self.config['pi_host'],
                username=self.config['pi_user'],
                key_filename=self.config['ssh_key']
            )
            
            stdin, stdout, stderr = ssh.exec_command(command)
            
            # Wait for command completion with timeout
            stdout.channel.settimeout(timeout)
            stderr.channel.settimeout(timeout)
            
            output = stdout.read().decode()
            error = stderr.read().decode()
            exit_code = stdout.channel.recv_exit_status()
            
            ssh.close()
            
            return {
                'success': exit_code == 0,
                'output': output,
                'error': error,
                'exit_code': exit_code
            }
            
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'exit_code': -1
            }
    
    def sync_data_to_pi(self) -> bool:
        """Sync NBA data and models to Pi node"""
        
        self.logger.info(" Syncing data to Pi node...")
        
        # Files to sync
        sync_files = [
            f"{self.config['data_dir']}/nba_cluster.db",
            f"{self.config['models_dir']}/nba_player_model.tflite",
            f"{self.config['models_dir']}/nba_scaler.joblib"
        ]
        
        # Check if files exist
        missing_files = [f for f in sync_files if not Path(f).exists()]
        if missing_files:
            self.logger.warning(f" Missing files: {missing_files}")
        
        try:
            # Create Pi directories
            mkdir_cmd = "mkdir -p /home/eq12/nba_data /home/eq12/nba_models"
            result = self.execute_on_pi(mkdir_cmd)
            
            if not result['success']:
                self.logger.error(f" Failed to create Pi directories: {result['error']}")
                return False
            
            # Use SCP to transfer files
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                self.config['pi_host'],
                username=self.config['pi_user'],
                key_filename=self.config['ssh_key']
            )
            
            scp = ssh.open_sftp()
            
            for local_file in sync_files:
                if Path(local_file).exists():
                    if 'data' in local_file:
                        remote_file = f"/home/eq12/nba_data/{Path(local_file).name}"
                    else:
                        remote_file = f"/home/eq12/nba_models/{Path(local_file).name}"
                    
                    scp.put(local_file, remote_file)
                    self.logger.info(f" Synced: {Path(local_file).name}")
            
            scp.close()
            ssh.close()
            
            self.cluster_status.data_synced = True
            return True
            
        except Exception as e:
            self.logger.error(f" Data sync failed: {e}")
            return False
    
    def run_data_collection(self) -> bool:
        """Execute NBA data collection on EQ12 host"""
        
        self.logger.info(" Starting NBA data collection...")
        
        try:
            # Run odds collector
            cmd = [
                "python", 
                f"{self.config['scripts_dir']}/eq12_nba_odds_collector.py",
                "--mode", "single",
                "--export-tpu"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.logger.info(" Data collection completed")
                return True
            else:
                self.logger.error(f" Data collection failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f" Data collection error: {e}")
            return False
    
    def run_feature_engineering(self, game_date: str = None) -> bool:
        """Execute feature engineering pipeline"""
        
        if game_date is None:
            game_date = datetime.now().strftime('%Y-%m-%d')
            
        self.logger.info(f" Building features for {game_date}...")
        
        try:
            cmd = [
                "python",
                f"{self.config['scripts_dir']}/eq12_nba_feature_builder.py", 
                "--date", game_date,
                "--export-tpu"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                self.logger.info(" Feature engineering completed")
                return True
            else:
                self.logger.error(f" Feature engineering failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f" Feature engineering error: {e}")
            return False
    
    def run_tpu_inference(self, game_date: str = None) -> bool:
        """Execute TPU inference on Pi node"""
        
        if game_date is None:
            game_date = datetime.now().strftime('%Y-%m-%d')
            
        self.logger.info(" Running TPU inference on Pi...")
        
        # Command to run on Pi
        date_str = game_date.replace('-', '')
        cmd = f"""
            cd /home/eq12 && 
            python3 -c "
import numpy as np
import tensorflow as tf
from pathlib import Path
import json
from datetime import datetime

# Load feature data
feature_file = 'nba_data/nba_features_{date_str}.npy'
if Path(feature_file).exists():
    features = np.load(feature_file)
    print(f'Loaded features: {{features.shape}}')
    
    # Load TFLite model
    interpreter = tf.lite.Interpreter(model_path='nba_models/nba_player_model.tflite')
    interpreter.allocate_tensors()
    
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    predictions = []
    for i in range(features.shape[0]):
        interpreter.set_tensor(input_details[0]['index'], features[i:i+1])
        interpreter.invoke()
        pred = interpreter.get_tensor(output_details[0]['index'])[0]
        predictions.append(pred.tolist())
    
    # Save predictions
    results = {{
        'game_date': '{game_date}',
        'predictions': predictions,
        'timestamp': datetime.utcnow().isoformat()
    }}
    
    with open('nba_data/predictions_{date_str}.json', 'w') as f:
        json.dump(results, f)
    
    print(f'Generated {{len(predictions)}} predictions')
else:
    print('No feature file found')
"
        """
        
        result = self.execute_on_pi(cmd, timeout=120)
        
        if result['success']:
            self.logger.info(" TPU inference completed")
            return True
        else:
            self.logger.error(f" TPU inference failed: {result['error']}")
            return False
    
    def sync_predictions_from_pi(self, game_date: str = None) -> bool:
        """Sync prediction results back from Pi to EQ12"""
        
        if game_date is None:
            game_date = datetime.now().strftime('%Y-%m-%d')
            
        date_str = game_date.replace('-', '')
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                self.config['pi_host'],
                username=self.config['pi_user'],
                key_filename=self.config['ssh_key']
            )
            
            scp = ssh.open_sftp()
            
            # Download prediction file
            remote_file = f"/home/eq12/nba_data/predictions_{date_str}.json"
            local_file = f"{self.config['data_dir']}/predictions_{date_str}.json"
            
            scp.get(remote_file, local_file)
            scp.close()
            ssh.close()
            
            self.logger.info(f" Synced predictions from Pi: {Path(local_file).name}")
            return True
            
        except Exception as e:
            self.logger.error(f" Prediction sync failed: {e}")
            return False
    
    def run_prop_analysis(self) -> bool:
        """Execute prop betting analysis"""
        
        self.logger.info(" Running prop betting analysis...")
        
        try:
            cmd = [
                "python",
                f"{self.config['scripts_dir']}/eq12_nba_prop_engine.py",
                "--action", "analyze",
                "--min-ev", "0.05"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.logger.info(" Prop analysis completed")
                return True
            else:
                self.logger.error(f" Prop analysis failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f" Prop analysis error: {e}")
            return False
    
    def run_complete_pipeline(self) -> Dict[str, bool]:
        """Execute the complete NBA betting pipeline"""
        
        self.logger.info(" Starting complete NBA betting pipeline")
        
        pipeline_results = {
            'connectivity_check': False,
            'tpu_check': False,
            'data_collection': False,
            'feature_engineering': False,
            'data_sync': False,
            'tpu_inference': False,
            'prediction_sync': False,
            'prop_analysis': False
        }
        
        try:
            # 1. Check cluster connectivity
            pipeline_results['connectivity_check'] = self.check_pi_connectivity()
            pipeline_results['tpu_check'] = self.check_tpu_status()
            
            if not pipeline_results['connectivity_check']:
                self.logger.error(" Pi connectivity failed - aborting pipeline")
                return pipeline_results
            
            if not pipeline_results['tpu_check']:
                self.logger.warning(" TPU not detected - continuing with CPU inference")
            
            # 2. Data collection on EQ12
            pipeline_results['data_collection'] = self.run_data_collection()
            
            # 3. Feature engineering on EQ12
            pipeline_results['feature_engineering'] = self.run_feature_engineering()
            
            # 4. Sync data to Pi
            pipeline_results['data_sync'] = self.sync_data_to_pi()
            
            # 5. TPU inference on Pi
            if pipeline_results['data_sync']:
                pipeline_results['tpu_inference'] = self.run_tpu_inference()
                
                # 6. Sync predictions back
                if pipeline_results['tpu_inference']:
                    pipeline_results['prediction_sync'] = self.sync_predictions_from_pi()
            
            # 7. Prop analysis on EQ12
            pipeline_results['prop_analysis'] = self.run_prop_analysis()
            
            # Update cluster status
            self.cluster_status.last_update = datetime.now()
            
            # Generate pipeline report
            success_count = sum(pipeline_results.values())
            total_steps = len(pipeline_results)
            
            self.logger.info(f" Pipeline complete: {success_count}/{total_steps} steps successful")
            
            return pipeline_results
            
        except Exception as e:
            self.logger.error(f" Pipeline error: {e}")
            return pipeline_results
    
    def get_cluster_status(self) -> Dict:
        """Get comprehensive cluster status"""
        
        # Update real-time status
        self.check_pi_connectivity()
        self.check_tpu_status()
        
        # EQ12 system stats
        eq12_stats = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('C:').percent
        }
        
        # Pi system stats (if online)
        pi_stats = {}
        if self.cluster_status.pi_online:
            result = self.execute_on_pi("free | grep Mem: && vcgencmd measure_temp")
            if result['success']:
                pi_stats = {'status': 'online', 'output': result['output']}
        
        status_report = {
            'timestamp': datetime.now().isoformat(),
            'cluster_status': {
                'eq12_online': self.cluster_status.eq12_online,
                'pi_online': self.cluster_status.pi_online,
                'tpu_detected': self.cluster_status.tpu_detected,
                'data_synced': self.cluster_status.data_synced,
                'last_update': self.cluster_status.last_update.isoformat()
            },
            'eq12_stats': eq12_stats,
            'pi_stats': pi_stats,
            'network': {
                'eq12_ip': self.config['eq12_host'],
                'pi_ip': self.config['pi_host']
            }
        }
        
        return status_report
    
    def monitor_cluster(self, interval_minutes: int = 15):
        """Continuous cluster monitoring"""
        
        self.logger.info(f" Starting cluster monitoring (every {interval_minutes}m)")
        
        while True:
            try:
                status = self.get_cluster_status()
                
                # Log status
                status_file = f"{self.config['logs_dir']}/cluster_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(status_file, 'w') as f:
                    json.dump(status, f, indent=2)
                
                # Check for issues
                if not status['cluster_status']['pi_online']:
                    self.logger.warning(" Pi node offline")
                
                if not status['cluster_status']['tpu_detected']:
                    self.logger.warning(" TPU not detected")
                
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                self.logger.info(" Monitoring stopped")
                break
            except Exception as e:
                self.logger.error(f" Monitoring error: {e}")
                time.sleep(60)


def main():
    parser = argparse.ArgumentParser(description="EQ12 NBA Cluster Manager")
    parser.add_argument('--action', choices=['status', 'pipeline', 'monitor', 'sync'], 
                       default='status', help='Action to perform')
    parser.add_argument('--game-date', type=str, help='Game date for processing (YYYY-MM-DD)')
    parser.add_argument('--monitor-interval', type=int, default=15,
                       help='Monitoring interval in minutes')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    manager = EQ12_NBA_ClusterManager()
    
    try:
        if args.action == 'status':
            # Get cluster status
            status = manager.get_cluster_status()
            print(" EQ12 NBA Cluster Status:")
            print(f"   EQ12 Host: {' ONLINE' if status['cluster_status']['eq12_online'] else ' OFFLINE'}")
            print(f"   Pi Node: {' ONLINE' if status['cluster_status']['pi_online'] else ' OFFLINE'}")
            print(f"   Coral TPU: {' DETECTED' if status['cluster_status']['tpu_detected'] else ' NOT FOUND'}")
            print(f"   CPU Usage: {status['eq12_stats']['cpu_percent']:.1f}%")
            print(f"   Memory: {status['eq12_stats']['memory_percent']:.1f}%")
        
        elif args.action == 'pipeline':
            # Run complete pipeline
            results = manager.run_complete_pipeline()
            print(" Pipeline Results:")
            for step, success in results.items():
                status = " PASS" if success else " FAIL"
                print(f"   {step:20s}: {status}")
        
        elif args.action == 'monitor':
            # Start monitoring
            manager.monitor_cluster(args.monitor_interval)
        
        elif args.action == 'sync':
            # Sync data only
            success = manager.sync_data_to_pi()
            print(f" Data sync: {' SUCCESS' if success else ' FAILED'}")
        
        else:
            print(" Invalid action")
            return 1
    
    except Exception as e:
        print(f" Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())