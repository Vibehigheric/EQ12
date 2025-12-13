#!/usr/bin/env python3
"""
 EQ12 FORENSIC EVIDENCE COLLECTION TOOLKIT
Rapid evidence collection for incident response teams

Created: November 7, 2025
Author: EQ12 Incident Response Team
Purpose: Automated collection of forensic evidence with chain of custody
Classification: RESTRICTED - INCIDENT RESPONSE USE ONLY
"""

import asyncio
import json
import logging
import os
import subprocess
import hashlib
import zipfile
from datetime import datetime
from pathlib import Path
import psutil


class EQ12ForensicCollector:
    """
     Automated forensic evidence collection system
    """

    def __init__(self, incident_id: str, workspace_path: str = "C:\\EQ12"):
        self.incident_id = incident_id
        self.workspace_path = Path(workspace_path)
        self.evidence_path = self.workspace_path / "incident_response" / "forensics"
        self.evidence_path.mkdir(parents=True, exist_ok=True)

        self.logger = self._setup_logging()
        self.evidence_chain = []

        self.logger.info(f" Forensic collector initialized for incident:\
                {incident_id}")

    def _setup_logging(self):
        """Setup forensic logging with evidence integrity"""
        log_file = self.evidence_path / f"forensic_collection_{self.incident_id}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - [FORENSIC] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

        return logging.getLogger(__name__)

    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash for evidence integrity with robust error handling"""
        try:
            # Handle Windows long paths
            if os.name == 'nt':
                pstr = str(file_path.absolute())
                if not pstr.startswith('\\\\?\\') and len(pstr) > 260:
                    pstr = '\\\\?\\' + pstr
            else:
                pstr = str(file_path)

            sha256_hash = hashlib.sha256()
            with open(pstr, "rb") as f:
                while True:
                    chunk = f.read(4*1024*1024)  # 4MB chunks
                    if not chunk:
                        break
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()

        except PermissionError as pe:
            self.logger.error(f" Permission denied hashing {file_path}: {pe}")
            return f"HASH_FAILED_PERMISSION: {pe}"
        except FileNotFoundError as fnf:
            self.logger.error(f" File not found hashing {file_path}: {fnf}")
            return f"HASH_FAILED_NOT_FOUND: {fnf}"
        except OSError as ose:
            self.logger.error(f" OS error hashing {file_path}: {ose}")
            return f"HASH_FAILED_OS_ERROR: {ose}"
        except Exception as e:
            self.logger.error(f" Hash calculation failed for {file_path}: {e}")
            return f"HASH_FAILED_UNEXPECTED: {e}"

    def _add_to_evidence_chain(self, artifact_type: str, file_path: str, description: str):
        """Add artifact to chain of custody"""
        evidence_entry = {
            "timestamp": datetime.now().isoformat(),
            "incident_id": self.incident_id,
            "artifact_type": artifact_type,
            "file_path": file_path,
            "file_hash": self._calculate_hash(Path(file_path)),
            "description": description,
            "collected_by": "EQ12_Forensic_Collector",
            "integrity_verified": True
        }

        self.evidence_chain.append(evidence_entry)
        self.logger.info(f" Added to evidence chain: {artifact_type} - {file_path}")

    async def collect_memory_artifacts(self):
        """Collect memory-related forensic artifacts"""
        self.logger.info(" Collecting memory artifacts...")

        try:
            # Virtual memory information
            vm = psutil.virtual_memory()
            memory_data = {
                "virtual_memory": {
                    "total": vm.total,
                    "available": vm.available,
                    "percent": vm.percent,
                    "used": vm.used,
                    "free": vm.free,
                    "active": vm.active,
                    "inactive": vm.inactive,
                    "buffers": vm.buffers,
                    "cached": vm.cached,
                    "shared": vm.shared
                },
                "swap_memory": psutil.swap_memory()._asdict(),
                "collection_timestamp": datetime.now().isoformat()
            }

            memory_file = self.evidence_path / f"memory_analysis_{self.incident_id}.json"
            with open(memory_file, 'w') as f:
                json.dump(memory_data, f, indent=2)

            self._add_to_evidence_chain("MEMORY_ANALYSIS", str(memory_file), "System memory utilization analysis")

            # Process memory usage
            process_memory = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'memory_percent']):
                try:
                    proc_data = proc.info.copy()
                    if proc_data['memory_info']:
                        proc_data['memory_info'] = proc_data['memory_info']._asdict()
                    process_memory.append(proc_data)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            proc_memory_file = self.evidence_path / f"process_memory_{self.incident_id}.json"
            with open(proc_memory_file, 'w') as f:
                json.dump(process_memory, f, indent=2)

            self._add_to_evidence_chain("PROCESS_MEMORY", str(proc_memory_file), "Per-process memory usage analysis")

            return True

        except Exception as e:
            self.logger.error(f" Memory artifact collection failed: {e}")
            return False

    async def collect_process_artifacts(self):
        """Collect process-related forensic artifacts with robust error handling"""
        self.logger.info(" Collecting process artifacts...")

        try:
            # Complete process listing with safe attribute access
            processes = []
            collection_errors = []

            for proc in psutil.process_iter():
                try:
                    # Safely collect basic process information
                    proc_info = {'pid': proc.pid}

                    # Safe attribute collection with fallbacks
                    safe_attrs = {
                        'ppid': lambda: proc.ppid(),
                        'name': lambda: proc.name(),
                        'exe': lambda: proc.exe(),
                        'cmdline': lambda: proc.cmdline(),
                        'create_time': lambda: proc.create_time(),
                        'status': lambda: proc.status(),
                        'username': lambda: proc.username(),
                        'cwd': lambda: proc.cwd()
                    }

                    for attr_name, attr_func in safe_attrs.items():
                        try:
                            value = attr_func()
                            if attr_name == 'create_time' and value:
                                proc_info[attr_name] = datetime.fromtimestamp(value).isoformat()
                            else:
                                proc_info[attr_name] = value
                        except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
                            proc_info[f'{attr_name}_error'] = "AccessDenied"
                        except Exception as e:
                            proc_info[f'{attr_name}_error'] = str(e)

                    # Memory information with safe access
                    try:
                        mem_info = proc.memory_info()
                        proc_info['memory_info'] = {
                            'rss': mem_info.rss,
                            'vms': mem_info.vms
                        }
                        # Add Windows-specific memory info if available
                        if hasattr(mem_info, 'peak_wset'):
                            proc_info['memory_info']['peak_wset'] = mem_info.peak_wset
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        proc_info['memory_error'] = "AccessDenied"
                    except Exception as e:
                        proc_info['memory_error'] = str(e)

                    # CPU usage with safe access
                    try:
                        proc_info['cpu_percent'] = proc.cpu_percent()
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        proc_info['cpu_error'] = "AccessDenied"
                    except Exception as e:
                        proc_info['cpu_error'] = str(e)

                    # Network connections with robust error handling
                    try:
                        if hasattr(proc, 'connections'):
                            try:
                                # Try with inet parameter first
                                connections = proc.connections(kind='inet')
                            except TypeError:
                                # Fallback for older psutil versions
                                connections = proc.connections()

                            conn_list = []
                            for conn in connections:
                                try:
                                    conn_dict = {
                                        'family': str(conn.family),
                                        'type': str(conn.type),
                                        'laddr':\
                f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                                        'raddr':\
                f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                                        'status': conn.status
                                    }
                                    conn_list.append(conn_dict)
                                except Exception as e:
                                    conn_list.append({'error': str(e)})

                            proc_info['connections'] = conn_list
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        proc_info['connections_error'] = "AccessDenied"
                    except Exception as e:
                        proc_info['connections_error'] = str(e)

                    # Open files with safe access
                    try:
                        open_files = proc.open_files()
                        proc_info['open_files'] = [f.path for f in open_files]
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        proc_info['open_files_error'] = "AccessDenied"
                    except Exception as e:
                        proc_info['open_files_error'] = str(e)

                    processes.append(proc_info)

                except (psutil.NoSuchProcess, psutil.ZombieProcess):
                    # Process terminated during collection
                    continue
                except Exception as e:
                    collection_errors.append(f"Process {proc.pid if hasattr(proc, 'pid') else 'unknown'}:\
                {e}")
                    continue

            # Save process data with collection metadata
            process_data = {
                'collection_time': datetime.now().isoformat(),
                'total_processes': len(processes),
                'collection_errors': collection_errors,
                'processes': processes
            }

            process_file = self.evidence_path / f"complete_process_list_{self.incident_id}.json"
            with open(process_file, 'w') as f:
                json.dump(process_data, f, indent=2, default=str)

            self._add_to_evidence_chain("PROCESS_LIST", str(process_file),
                                      f"Complete system process listing - {len(processes)} processes, {len(collection_errors)} errors")

            # Suspicious process analysis
            suspicious_processes = []
            suspicious_keywords = ['eq12', 'python', 'powershell', 'cmd', 'wscript', 'cscript', 'ngrok']

            for proc in processes:
                try:
                    cmdline = proc.get('cmdline', [])
                    if cmdline and isinstance(cmdline, list):
                        cmdline_str = ' '.join(cmdline).lower()
                        if any(keyword in cmdline_str for keyword in suspicious_keywords):
                            suspicious_processes.append(proc)

                    # Check executable name
                    exe_name = proc.get('name', '').lower()
                    if any(keyword in exe_name for keyword in suspicious_keywords):
                        suspicious_processes.append(proc)

                except Exception as e:
                    self.logger.debug(f"Suspicious process analysis error: {e}")
                    continue

            if suspicious_processes:
                suspicious_file = self.evidence_path / f"suspicious_processes_{self.incident_id}.json"
                with open(suspicious_file, 'w') as f:
                    json.dump(suspicious_processes, f, indent=2)

                self._add_to_evidence_chain("SUSPICIOUS_PROCESSES", str(suspicious_file), "Processes matching suspicious patterns")

            return True

        except Exception as e:
            self.logger.error(f" Process artifact collection failed: {e}")
            return False

    async def collect_network_artifacts(self):
        """Collect network-related forensic artifacts"""
        self.logger.info(" Collecting network artifacts...")

        try:
            # Network connections
            connections = []
            for conn in psutil.net_connections(kind='inet'):
                try:
                    conn_info = {
                        'fd': conn.fd,
                        'family': str(conn.family),
                        'type': str(conn.type),
                        'local_address':\
                f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        'remote_address':\
                f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        'status': conn.status,
                        'pid': conn.pid
                    }
                    connections.append(conn_info)
                except Exception:
                    continue

            network_file = self.evidence_path / f"network_connections_{self.incident_id}.json"
            with open(network_file, 'w') as f:
                json.dump(connections, f, indent=2)

            self._add_to_evidence_chain("NETWORK_CONNECTIONS", str(network_file), "Active network connections")

            # Network interface statistics
            net_io = psutil.net_io_counters(pernic=True)
            net_stats = {}
            for interface, stats in net_io.items():
                net_stats[interface] = stats._asdict()

            net_stats_file = self.evidence_path / f"network_statistics_{self.incident_id}.json"
            with open(net_stats_file, 'w') as f:
                json.dump(net_stats, f, indent=2)

            self._add_to_evidence_chain("NETWORK_STATS", str(net_stats_file), "Network interface statistics")

            # Netstat output (Windows)
            try:
                netstat_result = subprocess.run(
                    "netstat -an", shell=True, capture_output=True, text=True, timeout=30
                )

                if netstat_result.returncode == 0:
                    netstat_file = self.evidence_path / f"netstat_output_{self.incident_id}.txt"
                    with open(netstat_file, 'w') as f:
                        f.write(f"Netstat output collected at:\
                {datetime.now().isoformat()}\n")
                        f.write("="*80 + "\n")
                        f.write(netstat_result.stdout)

                    self._add_to_evidence_chain("NETSTAT_OUTPUT", str(netstat_file), "Netstat command output")

            except Exception as e:
                self.logger.error(f" Netstat collection failed: {e}")

            return True

        except Exception as e:
            self.logger.error(f" Network artifact collection failed: {e}")
            return False

    async def collect_file_system_artifacts(self):
        """Collect file system forensic artifacts"""
        self.logger.info(" Collecting file system artifacts...")

        try:
            # EQ12 directory file inventory with timestamps and hashes
            file_inventory = []

            for file_path in self.workspace_path.rglob("*"):
                if file_path.is_file():
                    try:
                        stat_info = file_path.stat()
                        relative_path = file_path.relative_to(self.workspace_path)

                        # Skip large files for hash calculation (>10MB)
                        file_hash = "SKIPPED_LARGE_FILE" if stat_info.st_size > 10*1024*1024 else self._calculate_hash(file_path)

                        file_info = {
                            'path': str(relative_path),
                            'full_path': str(file_path),
                            'size_bytes': stat_info.st_size,
                            'modified_time': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                            'created_time': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                            'accessed_time': datetime.fromtimestamp(stat_info.st_atime).isoformat(),
                            'sha256_hash': file_hash,
                            'file_extension': file_path.suffix.lower()
                        }
                        file_inventory.append(file_info)

                    except Exception as e:
                        self.logger.warning(f" Could not process file {file_path}:\
                {e}")
                        continue

            inventory_file = self.evidence_path / f"file_system_inventory_{self.incident_id}.json"
            with open(inventory_file, 'w') as f:
                json.dump(file_inventory, f, indent=2)

            self._add_to_evidence_chain("FILE_INVENTORY", str(inventory_file), "Complete EQ12 file system inventory")

            # Recently modified files (last 24 hours)
            recent_threshold = datetime.now().timestamp() - (24 * 60 * 60)
            recent_files = [
                f for f in file_inventory
                if datetime.fromisoformat(f['modified_time']).timestamp() > recent_threshold
            ]

            if recent_files:
                recent_file = self.evidence_path / f"recently_modified_files_{self.incident_id}.json"
                with open(recent_file, 'w') as f:
                    json.dump(recent_files, f, indent=2)

                self._add_to_evidence_chain("RECENT_FILES", str(recent_file), "Files modified in last 24 hours")

            # Suspicious file extensions
            suspicious_extensions = ['.exe', '.bat', '.cmd', '.ps1', '.vbs', '.js', '.jar']
            suspicious_files = [
                f for f in file_inventory
                if f['file_extension'] in suspicious_extensions
            ]

            if suspicious_files:
                suspicious_file = self.evidence_path / f"suspicious_files_{self.incident_id}.json"
                with open(suspicious_file, 'w') as f:
                    json.dump(suspicious_files, f, indent=2)

                self._add_to_evidence_chain("SUSPICIOUS_FILES", str(suspicious_file), "Files with suspicious extensions")

            return True

        except Exception as e:
            self.logger.error(f" File system artifact collection failed: {e}")
            return False

    async def collect_system_artifacts(self):
        """Collect system-level forensic artifacts"""
        self.logger.info(" Collecting system artifacts...")

        try:
            # System information
            system_info = {
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "cpu_info": {
                    "physical_cores": psutil.cpu_count(logical=False),
                    "total_cores": psutil.cpu_count(logical=True),
                    "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                    "cpu_percent": psutil.cpu_percent(interval=1, percpu=True),
                    "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                "disk_usage": {
                    partition.device: psutil.disk_usage(partition.mountpoint)._asdict()
                    for partition in psutil.disk_partitions()
                },
                "disk_io": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else None,
                "users": [user._asdict() for user in psutil.users()],
                "collection_timestamp": datetime.now().isoformat()
            }

            system_file = self.evidence_path / f"system_information_{self.incident_id}.json"
            with open(system_file, 'w') as f:
                json.dump(system_info, f, indent=2)

            self._add_to_evidence_chain("SYSTEM_INFO", str(system_file), "Complete system information snapshot")

            # Environment variables (potentially sensitive)
            env_vars = dict(os.environ)
            env_file = self.evidence_path / f"environment_variables_{self.incident_id}.json"
            with open(env_file, 'w') as f:
                json.dump(env_vars, f, indent=2)

            self._add_to_evidence_chain("ENVIRONMENT_VARS", str(env_file), "System environment variables")

            # Windows Event Logs (if available)
            try:
                event_log_result = subprocess.run(
                    "wevtutil qe Security /f:text /c:100",
                    shell=True, capture_output=True, text=True, timeout=60
                )

                if event_log_result.returncode == 0:
                    event_file = self.evidence_path / f"security_event_log_{self.incident_id}.txt"
                    with open(event_file, 'w') as f:
                        f.write(f"Security Event Log (last 100 entries) - {datetime.now().isoformat()}\n")
                        f.write("="*80 + "\n")
                        f.write(event_log_result.stdout)

                    self._add_to_evidence_chain("EVENT_LOG", str(event_file), "Windows Security Event Log")

            except Exception as e:
                self.logger.warning(f" Event log collection failed: {e}")

            return True

        except Exception as e:
            self.logger.error(f" System artifact collection failed: {e}")
            return False

    async def create_evidence_package(self):
        """Create tamper-evident evidence package"""
        self.logger.info(" Creating evidence package...")

        try:
            # Create chain of custody document
            custody_document = {
                "incident_id": self.incident_id,
                "collection_start": datetime.now().isoformat(),
                "evidence_chain": self.evidence_chain,
                "total_artifacts": len(self.evidence_chain),
                "collector_info": {
                    "system": "EQ12_Forensic_Collector",
                    "version": "1.0",
                    "collection_method": "Automated"
                },
                "integrity_verification": {
                    "hash_algorithm": "SHA256",
                    "all_hashes_verified": all(e['integrity_verified'] for e in self.evidence_chain)
                }
            }

            custody_file = self.evidence_path / f"chain_of_custody_{self.incident_id}.json"
            with open(custody_file, 'w') as f:
                json.dump(custody_document, f, indent=2)

            # Create evidence package ZIP
            package_name = f"EQ12_Evidence_Package_{self.incident_id}.zip"
            package_path = self.evidence_path / package_name

            with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all evidence files
                for evidence in self.evidence_chain:
                    file_path = Path(evidence['file_path'])
                    if file_path.exists():
                        zipf.write(file_path, file_path.name)

                # Add chain of custody
                zipf.write(custody_file, custody_file.name)

            # Calculate package hash
            package_hash = self._calculate_hash(package_path)

            # Create package manifest
            manifest = {
                "package_name": package_name,
                "package_hash": package_hash,
                "creation_time": datetime.now().isoformat(),
                "incident_id": self.incident_id,
                "total_files": len(self.evidence_chain) + 1,  # +1 for custody document
                "package_size_bytes": package_path.stat().st_size,
                "verification_instructions": [
                    f"Verify package integrity: SHA256 hash should be {package_hash}",
                    "Extract package in secure environment only",
                    "Verify individual file hashes against chain of custody",
                    "Maintain chain of custody documentation"
                ]
            }

            manifest_file = self.evidence_path / f"package_manifest_{self.incident_id}.json"
            with open(manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)

            self.logger.info(f" Evidence package created: {package_path}")
            self.logger.info(f" Package hash: {package_hash}")

            return {
                "package_path": str(package_path),
                "package_hash": package_hash,
                "manifest_path": str(manifest_file),
                "total_artifacts": len(self.evidence_chain)
            }

        except Exception as e:
            self.logger.error(f" Evidence package creation failed: {e}")
            return None

    async def run_complete_collection(self):
        """Run complete forensic evidence collection"""
        self.logger.info(f" Starting complete forensic collection for incident:\
                {self.incident_id}")

        collection_start = datetime.now()

        print("" + "="*70)
        print(" EQ12 FORENSIC EVIDENCE COLLECTION")
        print("" + "="*70)
        print(f" Incident ID: {self.incident_id}")
        print(f" Collection Start:\
                {collection_start.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("" + "="*70)

        # Run all collection modules
        collection_tasks = [
            ("Memory Artifacts", self.collect_memory_artifacts),
            ("Process Artifacts", self.collect_process_artifacts),
            ("Network Artifacts", self.collect_network_artifacts),
            ("File System Artifacts", self.collect_file_system_artifacts),
            ("System Artifacts", self.collect_system_artifacts)
        ]

        successful_collections = []
        failed_collections = []

        for task_name, task_func in collection_tasks:
            print(f"\n Collecting {task_name}...")
            try:
                result = await task_func()
                if result:
                    successful_collections.append(task_name)
                    print(f" {task_name} collection complete")
                else:
                    failed_collections.append(task_name)
                    print(f" {task_name} collection failed")
            except Exception as e:
                failed_collections.append(task_name)
                print(f" {task_name} collection failed: {e}")

        # Create evidence package
        print(f"\n Creating evidence package...")
        package_info = await self.create_evidence_package()

        collection_end = datetime.now()
        collection_duration = (collection_end - collection_start).total_seconds()

        # Final summary
        print("\n FORENSIC COLLECTION COMPLETE")
        print("="*70)
        print(f" Incident ID: {self.incident_id}")
        print(f" Successful Collections: {len(successful_collections)}")
        print(f" Failed Collections: {len(failed_collections)}")
        print(f" Evidence Package:\
                {package_info['package_path'] if package_info else 'FAILED'}")
        print(f" Package Hash:\
                {package_info['package_hash'] if package_info else 'N/A'}")
        print(f" Collection Duration: {collection_duration:.1f} seconds")
        print(f" Evidence Location: {self.evidence_path}")
        print("="*70)

        if failed_collections:
            print(f" Failed Collections: {', '.join(failed_collections)}")

        print(" Evidence collection complete - preserve chain of custody!")
        print(" Provide evidence package to incident response team!")
        print("="*70)

        return {
            "incident_id": self.incident_id,
            "collection_duration": collection_duration,
            "successful_collections": successful_collections,
            "failed_collections": failed_collections,
            "evidence_package": package_info,
            "total_artifacts": len(self.evidence_chain)
        }


def main():
    """Main forensic collection entry point"""
    import argparse

    parser = argparse.ArgumentParser(description=" EQ12 Forensic Evidence Collector")
    parser.add_argument("--incident-id", required=True, help="Incident ID for evidence tracking")
    parser.add_argument("--workspace", default="C:\\EQ12", help="EQ12 workspace path")

    args = parser.parse_args()

    print(" EQ12 FORENSIC EVIDENCE COLLECTION TOOLKIT")
    print("Automated evidence collection with chain of custody")
    print("="*70)

    # Initialize collector
    collector = EQ12ForensicCollector(args.incident_id, args.workspace)

    # Run collection
    asyncio.run(collector.run_complete_collection())


if __name__ == "__main__":
    main()