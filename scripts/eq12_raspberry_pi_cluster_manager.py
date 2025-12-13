#!/usr/bin/env python3
"""
EQ12 Raspberry Pi 5 + Coral USB Accelerator Cluster Manager
===========================================================

Distributed Edge Computing Architecture:
- Windows PC (Host): EQ12 system coordinator, heavy compute, storage
- Raspberry Pi 5: Edge processing node with Coral TPU acceleration
- Ethernet Network: Low-latency communication between nodes

Key Features:
- Automatic Pi discovery and configuration
- Coral TPU workload distribution
- Real-time task allocation and monitoring
- Failover and load balancing
- Secure communication via SSH tunnels
"""

import argparse
import asyncio
import json
import logging
import os
import socket
import subprocess
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import threading
import queue
import traceback

# Network and SSH libraries
try:
    import paramiko
    import psutil
    import requests
    from paramiko import SSHClient, AutoAddPolicy
    SSH_AVAILABLE = True
except ImportError:
    SSH_AVAILABLE = False
    logging.warning("SSH libraries not available. Install with: pip install paramiko psutil requests")

# Setup logging
log_dir = Path("C:/EQ12/logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"raspberry_pi_cluster_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class RaspberryPiNode:
    """Raspberry Pi cluster node configuration"""
    ip_address: str
    hostname: str
    username: str = "pi"
    password: str = ""
    ssh_key_path: str = ""
    coral_connected: bool = False
    cpu_cores: int = 4
    memory_gb: float = 8.0
    available: bool = True
    current_tasks: List[str] = None
    last_heartbeat: Optional[datetime] = None
    
    def __post_init__(self):
        if self.current_tasks is None:
            self.current_tasks = []

@dataclass
class EdgeTask:
    """Distributed edge computing task"""
    task_id: str
    task_type: str  # 'coral_inference', 'data_processing', 'monitoring'
    payload: Dict[str, Any]
    priority: int = 5  # 1-10, 10 = highest
    requires_coral: bool = False
    estimated_runtime: int = 30  # seconds
    assigned_node: Optional[str] = None
    status: str = "pending"  # pending, assigned, running, completed, failed
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class RaspberryPiClusterManager:
    """Manages distributed EQ12 processing across Raspberry Pi cluster"""
    
    def __init__(self, config_file: str = "C:/EQ12/configs/raspberry_pi_cluster.json"):
        self.config_file = Path(config_file)
        self.nodes: Dict[str, RaspberryPiNode] = {}
        self.task_queue = queue.PriorityQueue()
        self.completed_tasks: Dict[str, EdgeTask] = {}
        self.running = False
        self.worker_threads: List[threading.Thread] = []
        
        # Load configuration
        self.load_configuration()
        
        # Network scanner
        self.network_base = self._detect_network_base()
        
        logger.info(" EQ12 Raspberry Pi Cluster Manager initialized")
        logger.info(f" Network base: {self.network_base}")
        logger.info(f" Configuration file: {self.config_file}")
    
    def _detect_network_base(self) -> str:
        """Detect local network base for Pi discovery"""
        try:
            # Get default gateway and infer network
            result = subprocess.run(['route', 'print'], capture_output=True, text=True, shell=True)
            for line in result.stdout.split('\n'):
                if '0.0.0.0' in line and 'Gateway' not in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        gateway = parts[2]
                        # Extract network base (e.g., 192.168.1.1 -> 192.168.1)
                        return '.'.join(gateway.split('.')[:-1])
        except:
            pass
        
        # Fallback to common networks
        return "192.168.1"
    
    def load_configuration(self):
        """Load cluster configuration from JSON file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                for node_config in config.get('nodes', []):
                    node = RaspberryPiNode(**node_config)
                    self.nodes[node.ip_address] = node
                
                logger.info(f" Loaded {len(self.nodes)} nodes from configuration")
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
        else:
            logger.info("No existing configuration found, will create new one")
    
    def save_configuration(self):
        """Save cluster configuration to JSON file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            config = {
                'nodes': [asdict(node) for node in self.nodes.values()],
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2, default=str)
            
            logger.info(f" Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def discover_raspberry_pis(self) -> List[str]:
        """Scan network for Raspberry Pi devices"""
        logger.info(f" Scanning network {self.network_base}.1-254 for Raspberry Pi devices...")
        
        discovered_ips = []
        threads = []
        results = queue.Queue()
        
        def check_host(ip: str):
            """Check if host is a Raspberry Pi"""
            try:
                # Quick ping test
                result = subprocess.run(['ping', '-n', '1', '-w', '1000', ip], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    # Try SSH connection to check if it's a Pi
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(2)
                        if sock.connect_ex((ip, 22)) == 0:
                            # SSH port is open, likely a Pi
                            results.put(ip)
                        sock.close()
                    except:
                        pass
            except:
                pass
        
        # Scan range of IPs
        for i in range(1, 255):
            ip = f"{self.network_base}.{i}"
            thread = threading.Thread(target=check_host, args=(ip,))
            thread.start()
            threads.append(thread)
            
            # Limit concurrent threads
            if len(threads) >= 50:
                for t in threads:
                    t.join()
                threads = []
        
        # Wait for remaining threads
        for thread in threads:
            thread.join()
        
        # Collect results
        while not results.empty():
            discovered_ips.append(results.get())
        
        logger.info(f" Discovered {len(discovered_ips)} potential Raspberry Pi devices: {discovered_ips}")
        return discovered_ips
    
    def connect_to_pi(self, ip: str, username: str = "pi", password: str = "", ssh_key_path: str = "") -> Optional[paramiko.SSHClient]:
        """Establish SSH connection to Raspberry Pi"""
        if not SSH_AVAILABLE:
            logger.error("SSH libraries not available")
            return None
        
        try:
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            
            if ssh_key_path and os.path.exists(ssh_key_path):
                client.connect(ip, username=username, key_filename=ssh_key_path, timeout=5)
            elif password:
                client.connect(ip, username=username, password=password, timeout=5)
            else:
                logger.warning(f"No authentication method provided for {ip}")
                return None
            
            logger.info(f" SSH connection established to {ip}")
            return client
        except Exception as e:
            logger.error(f"Failed to connect to {ip}: {e}")
            return None
    
    def detect_coral_on_pi(self, ssh_client: paramiko.SSHClient) -> bool:
        """Check if Coral USB accelerator is connected to Pi"""
        try:
            stdin, stdout, stderr = ssh_client.exec_command("lsusb | grep -i coral || lsusb | grep -i google")
            output = stdout.read().decode().strip()
            return bool(output)
        except Exception as e:
            logger.error(f"Failed to detect Coral: {e}")
            return False
    
    def setup_pi_environment(self, ssh_client: paramiko.SSHClient, node: RaspberryPiNode):
        """Setup EQ12 environment on Raspberry Pi"""
        commands = [
            # Update system
            "sudo apt update",
            
            # Install Python and pip
            "sudo apt install -y python3 python3-pip python3-venv",
            
            # Install Coral Edge TPU runtime
            "echo 'deb https://packages.cloud.google.com/apt coral-edgetpu-stable main' | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list",
            "curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -",
            "sudo apt update",
            "sudo apt install -y libedgetpu1-std python3-pycoral",
            
            # Create EQ12 workspace
            "mkdir -p ~/eq12_edge",
            "cd ~/eq12_edge && python3 -m venv venv",
            "cd ~/eq12_edge && source venv/bin/activate && pip install numpy tensorflow-lite pycoral pillow requests",
            
            # Install monitoring tools
            "sudo apt install -y htop iotop",
            
            # Create startup script
            """cat > ~/eq12_edge/startup.py << 'EOF'
#!/usr/bin/env python3
import socket
import json
import time
import subprocess
from datetime import datetime

def register_with_host():
    try:
        # Get system info
        cpu_info = subprocess.run(['nproc'], capture_output=True, text=True).stdout.strip()
        mem_info = subprocess.run(['free', '-m'], capture_output=True, text=True).stdout
        
        # Parse memory
        mem_lines = mem_info.split('\\n')
        mem_total = int(mem_lines[1].split()[1]) / 1024  # GB
        
        # Check Coral
        coral_check = subprocess.run(['lsusb'], capture_output=True, text=True).stdout
        has_coral = 'coral' in coral_check.lower() or 'google' in coral_check.lower()
        
        registration = {
            'hostname': socket.gethostname(),
            'ip_address': socket.gethostbyname(socket.gethostname()),
            'cpu_cores': int(cpu_info),
            'memory_gb': mem_total,
            'coral_connected': has_coral,
            'timestamp': datetime.now().isoformat(),
            'status': 'ready'
        }
        
        print(f"Raspberry Pi registration: {json.dumps(registration, indent=2)}")
        
    except Exception as e:
        print(f"Registration failed: {e}")

if __name__ == "__main__":
    register_with_host()
EOF""",
            
            "chmod +x ~/eq12_edge/startup.py"
        ]
        
        for cmd in commands:
            try:
                logger.info(f"Executing on Pi: {cmd[:50]}...")
                stdin, stdout, stderr = ssh_client.exec_command(cmd, timeout=60)
                
                # Wait for command completion
                exit_status = stdout.channel.recv_exit_status()
                if exit_status != 0:
                    error_output = stderr.read().decode()
                    logger.warning(f"Command failed (exit {exit_status}): {error_output}")
                else:
                    output = stdout.read().decode()
                    if output.strip():
                        logger.debug(f"Command output: {output[:200]}...")
                        
            except Exception as e:
                logger.error(f"Failed to execute command '{cmd}': {e}")
    
    def add_pi_node(self, ip: str, username: str = "pi", password: str = "", ssh_key_path: str = ""):
        """Add new Raspberry Pi node to cluster"""
        try:
            # Connect to Pi
            ssh_client = self.connect_to_pi(ip, username, password, ssh_key_path)
            if not ssh_client:
                return False
            
            # Get system information
            stdin, stdout, stderr = ssh_client.exec_command("hostname")
            hostname = stdout.read().decode().strip()
            
            stdin, stdout, stderr = ssh_client.exec_command("nproc")
            cpu_cores = int(stdout.read().decode().strip())
            
            stdin, stdout, stderr = ssh_client.exec_command("free -m | grep '^Mem:' | awk '{print $2}'")
            memory_mb = int(stdout.read().decode().strip())
            memory_gb = memory_mb / 1024
            
            # Check for Coral
            coral_connected = self.detect_coral_on_pi(ssh_client)
            
            # Create node
            node = RaspberryPiNode(
                ip_address=ip,
                hostname=hostname,
                username=username,
                password=password,
                ssh_key_path=ssh_key_path,
                coral_connected=coral_connected,
                cpu_cores=cpu_cores,
                memory_gb=memory_gb,
                available=True,
                last_heartbeat=datetime.now()
            )
            
            # Setup environment
            logger.info(f" Setting up EQ12 environment on {hostname} ({ip})")
            self.setup_pi_environment(ssh_client, node)
            
            # Add to cluster
            self.nodes[ip] = node
            self.save_configuration()
            
            ssh_client.close()
            
            logger.info(f" Added Raspberry Pi node: {hostname} ({ip})")
            logger.info(f"   CPU: {cpu_cores} cores, RAM: {memory_gb:.1f}GB, Coral: {coral_connected}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add Pi node {ip}: {e}")
            return False
    
    def submit_edge_task(self, task_type: str, payload: Dict[str, Any], 
                        priority: int = 5, requires_coral: bool = False) -> str:
        """Submit task for distributed processing"""
        task_id = f"task_{int(time.time() * 1000)}"
        
        task = EdgeTask(
            task_id=task_id,
            task_type=task_type,
            payload=payload,
            priority=priority,
            requires_coral=requires_coral,
            created_at=datetime.now()
        )
        
        # Add to priority queue (negative priority for max-heap behavior)
        self.task_queue.put((-priority, time.time(), task))
        
        logger.info(f" Submitted edge task {task_id}: {task_type} (priority: {priority})")
        return task_id
    
    def find_best_node(self, task: EdgeTask) -> Optional[str]:
        """Find best available node for task"""
        available_nodes = [
            (ip, node) for ip, node in self.nodes.items() 
            if node.available and len(node.current_tasks) < node.cpu_cores
        ]
        
        if not available_nodes:
            return None
        
        # Filter by Coral requirement
        if task.requires_coral:
            available_nodes = [(ip, node) for ip, node in available_nodes if node.coral_connected]
            if not available_nodes:
                logger.warning(f"No available nodes with Coral for task {task.task_id}")
                return None
        
        # Sort by current load (fewer active tasks = better)
        available_nodes.sort(key=lambda x: len(x[1].current_tasks))
        
        return available_nodes[0][0]
    
    def execute_task_on_pi(self, task: EdgeTask, node_ip: str) -> bool:
        """Execute task on specific Raspberry Pi node"""
        node = self.nodes[node_ip]
        
        try:
            # Connect to Pi
            ssh_client = self.connect_to_pi(node_ip, node.username, node.password, node.ssh_key_path)
            if not ssh_client:
                return False
            
            # Mark task as running
            task.status = "running"
            task.started_at = datetime.now()
            task.assigned_node = node_ip
            node.current_tasks.append(task.task_id)
            
            logger.info(f" Executing task {task.task_id} on {node.hostname} ({node_ip})")
            
            # Create task script based on type
            if task.task_type == "coral_inference":
                script = self._create_coral_inference_script(task)
            elif task.task_type == "data_processing":
                script = self._create_data_processing_script(task)
            elif task.task_type == "monitoring":
                script = self._create_monitoring_script(task)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")
            
            # Upload and execute script
            script_path = f"/tmp/eq12_task_{task.task_id}.py"
            
            # Write script to Pi
            stdin, stdout, stderr = ssh_client.exec_command(f"cat > {script_path}")
            stdin.write(script)
            stdin.close()
            
            # Execute script
            stdin, stdout, stderr = ssh_client.exec_command(
                f"cd ~/eq12_edge && source venv/bin/activate && python3 {script_path}",
                timeout=300
            )
            
            # Get results
            output = stdout.read().decode()
            error_output = stderr.read().decode()
            exit_status = stdout.channel.recv_exit_status()
            
            if exit_status == 0:
                # Parse result
                try:
                    result = json.loads(output.strip().split('\n')[-1])
                    task.result = result
                    task.status = "completed"
                    task.completed_at = datetime.now()
                    
                    logger.info(f" Task {task.task_id} completed successfully")
                    
                except json.JSONDecodeError:
                    task.result = {"output": output}
                    task.status = "completed"
                    task.completed_at = datetime.now()
            else:
                task.error = error_output
                task.status = "failed"
                task.completed_at = datetime.now()
                
                logger.error(f" Task {task.task_id} failed: {error_output}")
            
            # Cleanup
            ssh_client.exec_command(f"rm -f {script_path}")
            ssh_client.close()
            
            # Update node
            node.current_tasks.remove(task.task_id)
            node.last_heartbeat = datetime.now()
            
            # Store completed task
            self.completed_tasks[task.task_id] = task
            
            return task.status == "completed"
            
        except Exception as e:
            logger.error(f"Failed to execute task {task.task_id} on {node_ip}: {e}")
            
            # Cleanup on error
            if task.task_id in node.current_tasks:
                node.current_tasks.remove(task.task_id)
            
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.now()
            
            return False
    
    def _create_coral_inference_script(self, task: EdgeTask) -> str:
        """Create Python script for Coral TPU inference"""
        return f"""
import json
import numpy as np
from pycoral.utils import edgetpu
from pycoral.utils import dataset
from pycoral.adapters import common
from pycoral.adapters import classify
from PIL import Image
import time

def coral_inference():
    try:
        # Task payload
        payload = {json.dumps(task.payload)}
        
        # Initialize Coral
        interpreter = edgetpu.make_interpreter(payload.get('model_path', '/tmp/model.tflite'))
        interpreter.allocate_tensors()
        
        # Process input data
        if 'image_data' in payload:
            # Image inference
            image = Image.fromarray(np.array(payload['image_data']))
            size = common.input_size(interpreter)
            image = image.convert('RGB').resize(size, Image.ANTIALIAS)
            
            # Run inference
            start_time = time.time()
            common.set_input(interpreter, image)
            interpreter.invoke()
            inference_time = time.time() - start_time
            
            # Get results
            classes = classify.get_classes(interpreter, top_k=5)
            
            result = {{
                'status': 'success',
                'inference_time': inference_time,
                'predictions': [{{
                    'class_id': c.id,
                    'score': float(c.score)
                }} for c in classes],
                'coral_used': True
            }}
        else:
            # Numeric data inference
            input_data = np.array(payload['input_data'], dtype=np.float32)
            
            start_time = time.time()
            common.set_input(interpreter, input_data)
            interpreter.invoke()
            inference_time = time.time() - start_time
            
            output = common.output_tensor(interpreter, 0)
            
            result = {{
                'status': 'success',
                'inference_time': inference_time,
                'output': output.tolist(),
                'coral_used': True
            }}
        
        print(json.dumps(result))
        
    except Exception as e:
        error_result = {{
            'status': 'error',
            'error': str(e),
            'coral_used': False
        }}
        print(json.dumps(error_result))

if __name__ == "__main__":
    coral_inference()
"""
    
    def _create_data_processing_script(self, task: EdgeTask) -> str:
        """Create Python script for data processing tasks"""
        return f"""
import json
import numpy as np
import time
from datetime import datetime

def process_data():
    try:
        # Task payload
        payload = {json.dumps(task.payload)}
        
        start_time = time.time()
        
        # Process based on operation type
        operation = payload.get('operation', 'unknown')
        
        if operation == 'sports_data_analysis':
            # Analyze sports betting data
            odds_data = payload.get('odds_data', [])
            
            # Calculate expected values
            results = []
            for game in odds_data:
                ev = calculate_expected_value(game)
                results.append({{
                    'game_id': game.get('id'),
                    'expected_value': ev,
                    'recommendation': 'bet' if ev > 0.05 else 'pass'
                }})
            
            result = {{
                'status': 'success',
                'operation': operation,
                'processing_time': time.time() - start_time,
                'results': results,
                'processed_count': len(odds_data)
            }}
            
        elif operation == 'parlay_optimization':
            # Optimize parlay combinations
            legs = payload.get('legs', [])
            max_legs = payload.get('max_legs', 5)
            
            optimized_parlays = optimize_parlays(legs, max_legs)
            
            result = {{
                'status': 'success',
                'operation': operation,
                'processing_time': time.time() - start_time,
                'optimized_parlays': optimized_parlays
            }}
            
        else:
            # Generic data processing
            data = payload.get('data', [])
            processed = [x * 2 for x in data] if isinstance(data, list) else data
            
            result = {{
                'status': 'success',
                'operation': operation,
                'processing_time': time.time() - start_time,
                'processed_data': processed
            }}
        
        print(json.dumps(result))
        
    except Exception as e:
        error_result = {{
            'status': 'error',
            'operation': payload.get('operation', 'unknown'),
            'error': str(e)
        }}
        print(json.dumps(error_result))

def calculate_expected_value(game):
    # Simple EV calculation
    odds = game.get('odds', 1.0)
    probability = 1 / odds if odds > 0 else 0.5
    return (probability * odds) - 1

def optimize_parlays(legs, max_legs):
    # Simple parlay optimization
    from itertools import combinations
    
    best_parlays = []
    for r in range(2, min(max_legs + 1, len(legs) + 1)):
        for combo in combinations(legs, r):
            combined_odds = 1
            for leg in combo:
                combined_odds *= leg.get('odds', 1.0)
            
            if combined_odds > 2.0:  # Minimum viable parlay
                best_parlays.append({{
                    'legs': [leg.get('id') for leg in combo],
                    'combined_odds': combined_odds,
                    'leg_count': len(combo)
                }})
    
    # Sort by expected value
    best_parlays.sort(key=lambda x: x['combined_odds'], reverse=True)
    return best_parlays[:10]  # Top 10

if __name__ == "__main__":
    process_data()
"""
    
    def _create_monitoring_script(self, task: EdgeTask) -> str:
        """Create Python script for system monitoring"""
        return f"""
import json
import psutil
import subprocess
import time
from datetime import datetime

def system_monitoring():
    try:
        # Task payload
        payload = {json.dumps(task.payload)}
        
        # Collect system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network stats
        network = psutil.net_io_counters()
        
        # Temperature (Pi-specific)
        try:
            temp_result = subprocess.run(['vcgencmd', 'measure_temp'], 
                                       capture_output=True, text=True)
            temp_str = temp_result.stdout.strip()
            temperature = float(temp_str.split('=')[1].replace("'C", ""))
        except:
            temperature = None
        
        # Check Coral USB
        try:
            usb_result = subprocess.run(['lsusb'], capture_output=True, text=True)
            coral_connected = 'coral' in usb_result.stdout.lower() or 'google' in usb_result.stdout.lower()
        except:
            coral_connected = False
        
        # EQ12 process status
        eq12_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if 'eq12' in proc.info['name'].lower() or 'python' in proc.info['name'].lower():
                    eq12_processes.append(proc.info)
            except:
                pass
        
        result = {{
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'system_metrics': {{
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available': memory.available,
                'disk_percent': (disk.used / disk.total) * 100,
                'disk_free': disk.free,
                'temperature_c': temperature,
                'coral_connected': coral_connected
            }},
            'network_stats': {{
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }},
            'eq12_processes': eq12_processes
        }}
        
        print(json.dumps(result))
        
    except Exception as e:
        error_result = {{
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }}
        print(json.dumps(error_result))

if __name__ == "__main__":
    system_monitoring()
"""
    
    def start_cluster(self):
        """Start cluster task processing"""
        if self.running:
            logger.warning("Cluster is already running")
            return
        
        self.running = True
        logger.info(" Starting EQ12 Raspberry Pi cluster")
        
        # Start worker threads
        for i in range(3):  # 3 worker threads
            worker = threading.Thread(target=self._worker_loop, args=(i,))
            worker.daemon = True
            worker.start()
            self.worker_threads.append(worker)
        
        # Start heartbeat monitor
        heartbeat_thread = threading.Thread(target=self._heartbeat_monitor)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()
        
        logger.info(" Cluster started with 3 workers and heartbeat monitor")
    
    def stop_cluster(self):
        """Stop cluster processing"""
        self.running = False
        logger.info(" Stopping EQ12 Raspberry Pi cluster")
    
    def _worker_loop(self, worker_id: int):
        """Worker thread for processing tasks"""
        logger.info(f" Worker {worker_id} started")
        
        while self.running:
            try:
                # Get task from queue (blocking with timeout)
                try:
                    priority, timestamp, task = self.task_queue.get(timeout=5)
                except queue.Empty:
                    continue
                
                logger.info(f" Worker {worker_id} processing task {task.task_id}")
                
                # Find best node
                node_ip = self.find_best_node(task)
                if not node_ip:
                    logger.warning(f"No available nodes for task {task.task_id}, requeueing")
                    # Requeue with lower priority
                    self.task_queue.put((priority + 1, time.time(), task))
                    time.sleep(2)
                    continue
                
                # Execute task
                success = self.execute_task_on_pi(task, node_ip)
                
                if success:
                    logger.info(f" Worker {worker_id} completed task {task.task_id}")
                else:
                    logger.error(f" Worker {worker_id} failed task {task.task_id}")
                
                self.task_queue.task_done()
                
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                time.sleep(1)
        
        logger.info(f" Worker {worker_id} stopped")
    
    def _heartbeat_monitor(self):
        """Monitor node health via heartbeat"""
        logger.info(" Heartbeat monitor started")
        
        while self.running:
            try:
                for ip, node in self.nodes.items():
                    # Check if node is responsive
                    try:
                        result = subprocess.run(['ping', '-n', '1', '-w', '2000', ip], 
                                              capture_output=True, text=True)
                        if result.returncode == 0:
                            node.available = True
                            node.last_heartbeat = datetime.now()
                        else:
                            node.available = False
                            logger.warning(f" Node {ip} is not responding")
                    except:
                        node.available = False
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Heartbeat monitor error: {e}")
                time.sleep(10)
        
        logger.info(" Heartbeat monitor stopped")
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get comprehensive cluster status"""
        active_tasks = sum(len(node.current_tasks) for node in self.nodes.values())
        available_nodes = sum(1 for node in self.nodes.values() if node.available)
        coral_nodes = sum(1 for node in self.nodes.values() if node.coral_connected and node.available)
        
        return {
            'cluster_running': self.running,
            'total_nodes': len(self.nodes),
            'available_nodes': available_nodes,
            'coral_nodes': coral_nodes,
            'active_tasks': active_tasks,
            'pending_tasks': self.task_queue.qsize(),
            'completed_tasks': len(self.completed_tasks),
            'nodes': {
                ip: {
                    'hostname': node.hostname,
                    'available': node.available,
                    'coral_connected': node.coral_connected,
                    'cpu_cores': node.cpu_cores,
                    'memory_gb': node.memory_gb,
                    'active_tasks': len(node.current_tasks),
                    'last_heartbeat': node.last_heartbeat.isoformat() if node.last_heartbeat else None
                }
                for ip, node in self.nodes.items()
            }
        }
    
    def generate_dashboard_report(self) -> str:
        """Generate HTML dashboard report"""
        status = self.get_cluster_status()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>EQ12 Raspberry Pi Cluster Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }}
        .header {{ background: linear-gradient(45deg, #ff6b6b, #feca57); padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .stat-card {{ background: #2d3436; padding: 15px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 2em; font-weight: bold; color: #00b894; }}
        .nodes-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }}
        .node-card {{ background: #2d3436; padding: 15px; border-radius: 8px; border-left: 4px solid #00b894; }}
        .node-card.offline {{ border-left-color: #e17055; }}
        .coral-indicator {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }}
        .coral-yes {{ background: #00b894; }}
        .coral-no {{ background: #636e72; }}
        .timestamp {{ text-align: center; margin-top: 20px; color: #636e72; }}
    </style>
</head>
<body>
    <div class="header">
        <h1> EQ12 Raspberry Pi Cluster Dashboard</h1>
        <p>Distributed Edge Computing with Coral TPU Acceleration</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{status['total_nodes']}</div>
            <div>Total Nodes</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{status['available_nodes']}</div>
            <div>Online Nodes</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{status['coral_nodes']}</div>
            <div>Coral TPU Nodes</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{status['active_tasks']}</div>
            <div>Active Tasks</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{status['pending_tasks']}</div>
            <div>Pending Tasks</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{status['completed_tasks']}</div>
            <div>Completed Tasks</div>
        </div>
    </div>
    
    <h2> Cluster Nodes</h2>
    <div class="nodes-grid">
"""
        
        for ip, node_info in status['nodes'].items():
            online_class = "" if node_info['available'] else "offline"
            coral_class = "coral-yes" if node_info['coral_connected'] else "coral-no"
            coral_text = "Yes" if node_info['coral_connected'] else "No"
            
            html += f"""
        <div class="node-card {online_class}">
            <h3>{node_info['hostname']} ({ip})</h3>
            <p><strong>Status:</strong> {' Online' if node_info['available'] else ' Offline'}</p>
            <p><strong>Coral TPU:</strong> <span class="coral-indicator {coral_class}"></span>{coral_text}</p>
            <p><strong>CPU Cores:</strong> {node_info['cpu_cores']}</p>
            <p><strong>Memory:</strong> {node_info['memory_gb']:.1f}GB</p>
            <p><strong>Active Tasks:</strong> {node_info['active_tasks']}</p>
            <p><strong>Last Heartbeat:</strong> {node_info['last_heartbeat'] or 'Never'}</p>
        </div>
"""
        
        html += f"""
    </div>
    
    <div class="timestamp">
        Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
"""
        
        return html

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="EQ12 Raspberry Pi Cluster Manager")
    parser.add_argument("--action", choices=['discover', 'add-node', 'start', 'stop', 'status', 'dashboard', 'test-task'], 
                       default='status', help="Action to perform")
    parser.add_argument("--ip", help="IP address for add-node action")
    parser.add_argument("--username", default="pi", help="SSH username")
    parser.add_argument("--password", help="SSH password")
    parser.add_argument("--ssh-key", help="SSH private key file path")
    parser.add_argument("--config", default="C:/EQ12/configs/raspberry_pi_cluster.json", 
                       help="Cluster configuration file")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize cluster manager
    cluster = RaspberryPiClusterManager(args.config)
    
    try:
        if args.action == 'discover':
            logger.info(" Discovering Raspberry Pi devices on network...")
            discovered = cluster.discover_raspberry_pis()
            print(f"Discovered devices: {discovered}")
            
        elif args.action == 'add-node':
            if not args.ip:
                logger.error("IP address required for add-node action")
                return
            
            success = cluster.add_pi_node(args.ip, args.username, args.password, args.ssh_key or "")
            if success:
                print(f" Successfully added node {args.ip}")
            else:
                print(f" Failed to add node {args.ip}")
        
        elif args.action == 'start':
            cluster.start_cluster()
            print(" Cluster started")
            
            # Keep running
            try:
                while True:
                    time.sleep(10)
                    status = cluster.get_cluster_status()
                    print(f" Status: {status['available_nodes']}/{status['total_nodes']} nodes online, "
                          f"{status['active_tasks']} active tasks, {status['pending_tasks']} pending")
            except KeyboardInterrupt:
                cluster.stop_cluster()
                print(" Cluster stopped")
        
        elif args.action == 'stop':
            cluster.stop_cluster()
            print(" Cluster stopped")
        
        elif args.action == 'status':
            status = cluster.get_cluster_status()
            print(json.dumps(status, indent=2, default=str))
        
        elif args.action == 'dashboard':
            html = cluster.generate_dashboard_report()
            dashboard_file = Path("C:/EQ12/dashboard/raspberry_pi_cluster.html")
            dashboard_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(dashboard_file, 'w') as f:
                f.write(html)
            
            print(f" Dashboard saved to {dashboard_file}")
        
        elif args.action == 'test-task':
            if not cluster.nodes:
                logger.error("No nodes configured. Add nodes first.")
                return
            
            # Submit test tasks
            task_id1 = cluster.submit_edge_task(
                "monitoring", 
                {"operation": "system_check"}, 
                priority=8
            )
            
            task_id2 = cluster.submit_edge_task(
                "data_processing", 
                {
                    "operation": "sports_data_analysis",
                    "odds_data": [
                        {"id": "game1", "odds": 2.5},
                        {"id": "game2", "odds": 1.8}
                    ]
                }, 
                priority=7
            )
            
            if any(node.coral_connected for node in cluster.nodes.values()):
                task_id3 = cluster.submit_edge_task(
                    "coral_inference", 
                    {
                        "input_data": [[1.0, 2.0, 3.0, 4.0]]
                    }, 
                    priority=9,
                    requires_coral=True
                )
                print(f" Submitted Coral inference task: {task_id3}")
            
            print(f" Submitted test tasks: {task_id1}, {task_id2}")
            print("Start cluster with --action start to process tasks")
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()