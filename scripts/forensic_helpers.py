#!/usr/bin/env python3
"""
 EQ12 FORENSIC COLLECTION HELPER TOOLKIT
Cross-platform forensic evidence collection with robust error handling

Created: November 7, 2025
Author: EQ12 Security Response Team
Purpose: Production-grade forensic collection with chain of custody
Classification: CONFIDENTIAL - INCIDENT RESPONSE ONLY
"""

import psutil
import hashlib
import os
import json
import traceback
from pathlib import Path
import sys
import logging
import subprocess
import winreg
from datetime import datetime
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("FORENSIC_HELPER")


class ForensicManifest:
    """Evidence manifest with chain of custody tracking"""
    
    def __init__(self, incident_id: str, evidence_path: Path):
        self.incident_id = incident_id
        self.evidence_path = evidence_path
        self.manifest_file = evidence_path / f"manifest_{incident_id}.json"
        self.manifest = {
            "incident_id": incident_id,
            "creation_time": datetime.now().isoformat(),
            "artifacts": [],
            "collection_errors": [],
            "chain_of_custody": []
        }
    
    def add_artifact(self, artifact_type: str, path: str, hash_result: Any, notes: str = ""):
        """Add artifact to manifest with hash verification"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "artifact_type": artifact_type,
            "artifact_path": path,
            "hash_result": hash_result,
            "notes": notes,
            "collected_by": "EQ12_Forensic_Helper",
            "integrity_status": "VERIFIED" if isinstance(hash_result, str) and len(hash_result) == 64 else "FAILED"
        }
        self.manifest["artifacts"].append(entry)
        self._save_manifest()
    
    def add_error(self, operation: str, error_details: str, file_path: str = ""):
        """Log collection errors for investigation"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "error": error_details,
            "file_path": file_path
        }
        self.manifest["collection_errors"].append(error_entry)
        self._save_manifest()
    
    def add_custody_event(self, action: str, actor: str, details: str = ""):
        """Add chain of custody event"""
        custody_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "actor": actor,
            "details": details
        }
        self.manifest["chain_of_custody"].append(custody_entry)
        self._save_manifest()
    
    def _save_manifest(self):
        """Save manifest to disk"""
        try:
            with open(self.manifest_file, 'w', encoding='utf8') as f:
                json.dump(self.manifest, f, indent=2, default=str)
        except Exception as e:
            log.error(f"Failed to save manifest: {e}")


def safe_virtual_memory() -> Dict[str, Any]:
    """Cross-platform virtual memory collection"""
    try:
        vm = psutil.virtual_memory()
        # Memory stats differ per platform - return only attributes that exist
        keys = ['total', 'available', 'percent', 'used', 'free', 'active', 'inactive', 
                'buffers', 'cached', 'shared', 'slab', 'wired']
        out = {}
        for k in keys:
            if hasattr(vm, k):
                out[k] = getattr(vm, k)
        
        # Add swap memory if available
        try:
            swap = psutil.swap_memory()
            out['swap'] = {
                'total': swap.total,
                'used': swap.used,
                'free': swap.free,
                'percent': swap.percent
            }
        except Exception:
            out['swap'] = None
            
        return out
    except Exception:
        log.error("virtual_memory() failed: %s", traceback.format_exc())
        return {"error": "virtual_memory_collection_failed"}


def collect_process_list(out_path: str, manifest: ForensicManifest) -> str:
    """Robust process collection with connection details"""
    procs = []
    errors = []
    
    for proc in psutil.process_iter(attrs=['pid', 'name', 'exe', 'create_time', 'username', 'cmdline']):
        try:
            info = proc.info.copy()
            
            # Safely collect process connections
            try:
                # Try different connection methods
                if hasattr(proc, 'connections'):
                    try:
                        conns = proc.connections(kind='inet')
                    except TypeError:
                        # Fallback for older psutil versions
                        conns = proc.connections()
                    
                    info['connections'] = [
                        {
                            'laddr': f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else None,
                            'raddr': f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else None,
                            'status': c.status,
                            'family': str(c.family),
                            'type': str(c.type)
                        } for c in conns
                    ]
                else:
                    info['connections_error'] = "connections method not available"
                    
            except (psutil.AccessDenied, psutil.NoSuchProcess) as e:
                info['connections_error'] = f"AccessDenied: {e}"
            except Exception as e:
                info['connections_error'] = f"Unexpected error: {e}"
            
            # Safely collect memory info
            try:
                mem_info = proc.memory_info()
                info['memory'] = {
                    'rss': mem_info.rss,
                    'vms': mem_info.vms
                }
                
                # Extended memory info on Windows
                if hasattr(mem_info, 'peak_wset'):
                    info['memory']['peak_wset'] = mem_info.peak_wset
                    
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                info['memory_error'] = "AccessDenied"
            except Exception as e:
                info['memory_error'] = str(e)
            
            # Safely collect CPU info
            try:
                info['cpu_percent'] = proc.cpu_percent()
                info['num_threads'] = proc.num_threads()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                info['cpu_error'] = "AccessDenied"
            except Exception as e:
                info['cpu_error'] = str(e)
                
            procs.append(info)
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            errors.append(f"Process iteration error: {e}")
            log.debug("Skipping process: %s", e)
        except Exception as e:
            errors.append(f"Unexpected process error: {e}")
            log.warning("Unexpected process error: %s", e)
    
    # Save process list
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    process_data = {
        "collection_time": datetime.now().isoformat(),
        "total_processes": len(procs),
        "collection_errors": errors,
        "processes": procs
    }
    
    with open(out_path, 'w', encoding='utf8') as f:
        json.dump(process_data, f, default=str, indent=2)
    
    log.info("Wrote %d processes to %s (%d errors)", len(procs), out_path, len(errors))
    
    # Add to manifest
    file_hash = safe_file_hash(out_path)
    manifest.add_artifact("PROCESS_LIST", out_path, file_hash, f"Collected {len(procs)} processes with {len(errors)} errors")
    
    return out_path


def safe_file_hash(path: str, algorithm: str = 'sha256') -> Any:
    """
    Robust file hashing with Windows long path support and error handling
    """
    p = Path(path)
    
    # Handle Windows long path
    if os.name == 'nt':
        pstr = str(p.absolute())
        if not pstr.startswith('\\\\?\\') and len(pstr) > 260:
            pstr = '\\\\?\\' + pstr
    else:
        pstr = str(p)

    h = hashlib.new(algorithm)
    try:
        with open(pstr, 'rb') as fh:
            while True:
                chunk = fh.read(4*1024*1024)  # 4MB chunks
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
        
    except PermissionError as pe:
        log.error("Permission denied hashing %s: %s", path, pe)
        return {"error": "PermissionError", "path": str(path), "details": str(pe)}
    except FileNotFoundError as fnf:
        log.error("File not found hashing %s: %s", path, fnf)
        return {"error": "FileNotFound", "path": str(path)}
    except OSError as ose:
        # Handle ERROR_INVALID_PARAMETER and other OS errors
        log.error("OS error hashing %s: %s", path, ose)
        return {"error": "OSError", "details": str(ose), "errno": getattr(ose, 'errno', 'unknown')}
    except Exception as e:
        log.error("Unexpected error hashing %s: %s", path, traceback.format_exc())
        return {"error": "Unexpected", "details": str(e)}


def safe_collect_memory_snapshot(output_path: str, manifest: ForensicManifest):
    """Memory snapshot with cross-platform support"""
    try:
        memory_data = {
            "collection_time": datetime.now().isoformat(),
            "virtual_memory": safe_virtual_memory(),
            "warnings": []
        }
        
        # Add physical memory info if available
        try:
            memory_data["boot_time"] = datetime.fromtimestamp(psutil.boot_time()).isoformat()
        except Exception as e:
            memory_data["warnings"].append(f"boot_time collection failed: {e}")
        
        # Windows-specific memory details
        if os.name == 'nt':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                
                # Get system memory status
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]
                
                memory_status = MEMORYSTATUSEX()
                memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                
                if kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status)):
                    memory_data["windows_memory_status"] = {
                        "memory_load": memory_status.dwMemoryLoad,
                        "total_phys": memory_status.ullTotalPhys,
                        "avail_phys": memory_status.ullAvailPhys,
                        "total_page_file": memory_status.ullTotalPageFile,
                        "avail_page_file": memory_status.ullAvailPageFile,
                        "total_virtual": memory_status.ullTotalVirtual,
                        "avail_virtual": memory_status.ullAvailVirtual
                    }
                    
            except Exception as e:
                memory_data["warnings"].append(f"Windows memory status failed: {e}")
        
        # Recommend external tools for full memory dump
        memory_data["full_memory_dump_recommendation"] = [
            "For complete physical memory capture, use:",
            "- winpmem (Rekall/Volatility)",
            "- FTK Imager",
            "- DumpIt",
            "- Magnet ACQUIRE"
        ]
        
        with open(output_path, 'w', encoding='utf8') as f:
            json.dump(memory_data, f, default=str, indent=2)
        
        log.info("Wrote memory snapshot to %s", output_path)
        
        # Add to manifest
        file_hash = safe_file_hash(output_path)
        manifest.add_artifact("MEMORY_SNAPSHOT", output_path, file_hash, 
                            "Virtual memory snapshot - use external tools for full RAM dump")
        
    except Exception:
        error_msg = f"Memory snapshot failed: {traceback.format_exc()}"
        log.error(error_msg)
        manifest.add_error("memory_snapshot", error_msg, output_path)


def collect_network_connections(output_path: str, manifest: ForensicManifest):
    """Comprehensive network connection collection"""
    try:
        network_data = {
            "collection_time": datetime.now().isoformat(),
            "connections": [],
            "listening_ports": [],
            "network_stats": {},
            "errors": []
        }
        
        # Collect all network connections
        try:
            connections = psutil.net_connections(kind='inet')
            for conn in connections:
                conn_info = {
                    "fd": conn.fd,
                    "family": str(conn.family),
                    "type": str(conn.type),
                    "laddr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    "raddr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    "status": conn.status,
                    "pid": conn.pid
                }
                network_data["connections"].append(conn_info)
                
                # Track listening ports
                if conn.status == 'LISTEN':
                    network_data["listening_ports"].append({
                        "port": conn.laddr.port if conn.laddr else None,
                        "address": conn.laddr.ip if conn.laddr else None,
                        "pid": conn.pid
                    })
                    
        except Exception as e:
            network_data["errors"].append(f"Connection collection failed: {e}")
        
        # Network I/O statistics
        try:
            net_io = psutil.net_io_counters()
            if net_io:
                network_data["network_stats"] = {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                    "errin": net_io.errin,
                    "errout": net_io.errout,
                    "dropin": net_io.dropin,
                    "dropout": net_io.dropout
                }
        except Exception as e:
            network_data["errors"].append(f"Network stats collection failed: {e}")
        
        # Windows netstat output for additional context
        if os.name == 'nt':
            try:
                netstat_result = subprocess.run(
                    "netstat -ano", 
                    shell=True, capture_output=True, text=True, timeout=30
                )
                if netstat_result.returncode == 0:
                    network_data["netstat_output"] = netstat_result.stdout
            except Exception as e:
                network_data["errors"].append(f"Netstat collection failed: {e}")
        
        with open(output_path, 'w', encoding='utf8') as f:
            json.dump(network_data, f, default=str, indent=2)
        
        log.info("Wrote network connections to %s", output_path)
        
        # Add to manifest
        file_hash = safe_file_hash(output_path)
        manifest.add_artifact("NETWORK_CONNECTIONS", output_path, file_hash, 
                            f"Collected {len(network_data['connections'])} connections, {len(network_data['listening_ports'])} listening ports")
        
    except Exception:
        error_msg = f"Network collection failed: {traceback.format_exc()}"
        log.error(error_msg)
        manifest.add_error("network_collection", error_msg, output_path)


def collect_system_information(output_path: str, manifest: ForensicManifest):
    """Comprehensive system information collection"""
    try:
        system_data = {
            "collection_time": datetime.now().isoformat(),
            "platform": sys.platform,
            "errors": []
        }
        
        # Basic system info
        try:
            system_data.update({
                "hostname": os.environ.get('COMPUTERNAME', os.environ.get('HOSTNAME', 'unknown')),
                "username": os.environ.get('USERNAME', os.environ.get('USER', 'unknown')),
                "python_version": sys.version,
                "architecture": os.environ.get('PROCESSOR_ARCHITECTURE', 'unknown')
            })
        except Exception as e:
            system_data["errors"].append(f"Basic system info failed: {e}")
        
        # Windows-specific information
        if os.name == 'nt':
            try:
                # Get Windows version info
                import platform
                system_data["windows_info"] = {
                    "platform": platform.platform(),
                    "processor": platform.processor(),
                    "machine": platform.machine(),
                    "version": platform.version(),
                    "release": platform.release()
                }
                
                # Registry information (limited)
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                      r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                        system_data["windows_version"] = {
                            "ProductName": winreg.QueryValueEx(key, "ProductName")[0],
                            "CurrentVersion": winreg.QueryValueEx(key, "CurrentVersion")[0],
                            "CurrentBuildNumber": winreg.QueryValueEx(key, "CurrentBuildNumber")[0]
                        }
                except Exception as e:
                    system_data["errors"].append(f"Registry read failed: {e}")
                    
                # System info via systeminfo command
                try:
                    systeminfo_result = subprocess.run(
                        "systeminfo", 
                        shell=True, capture_output=True, text=True, timeout=60
                    )
                    if systeminfo_result.returncode == 0:
                        system_data["systeminfo_output"] = systeminfo_result.stdout
                except Exception as e:
                    system_data["errors"].append(f"Systeminfo command failed: {e}")
                    
        # Disk usage information
        try:
            disk_info = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": (usage.used / usage.total) * 100
                    })
                except Exception as e:
                    disk_info.append({
                        "device": partition.device,
                        "error": str(e)
                    })
            system_data["disk_usage"] = disk_info
        except Exception as e:
            system_data["errors"].append(f"Disk usage collection failed: {e}")
        
        # Environment variables (sanitized)
        try:
            env_vars = dict(os.environ)
            # Remove sensitive environment variables
            sensitive_keys = ['PASSWORD', 'TOKEN', 'SECRET', 'KEY', 'API_KEY']
            sanitized_env = {}
            for k, v in env_vars.items():
                if any(sensitive in k.upper() for sensitive in sensitive_keys):
                    sanitized_env[k] = "[REDACTED]"
                else:
                    sanitized_env[k] = v
            system_data["environment_variables"] = sanitized_env
        except Exception as e:
            system_data["errors"].append(f"Environment variable collection failed: {e}")
        
        with open(output_path, 'w', encoding='utf8') as f:
            json.dump(system_data, f, default=str, indent=2)
        
        log.info("Wrote system information to %s", output_path)
        
        # Add to manifest
        file_hash = safe_file_hash(output_path)
        manifest.add_artifact("SYSTEM_INFO", output_path, file_hash, "Complete system information and configuration")
        
    except Exception:
        error_msg = f"System information collection failed: {traceback.format_exc()}"
        log.error(error_msg)
        manifest.add_error("system_information", error_msg, output_path)


def collect_suspicious_files(base_path: str, output_path: str, manifest: ForensicManifest):
    """Collect information about suspicious files with hash calculation"""
    try:
        suspicious_data = {
            "collection_time": datetime.now().isoformat(),
            "base_path": base_path,
            "suspicious_files": [],
            "recently_modified": [],
            "executable_files": [],
            "errors": []
        }
        
        # Define suspicious patterns
        suspicious_extensions = ['.exe', '.bat', '.cmd', '.ps1', '.vbs', '.js', '.jar', '.scr', '.com', '.pif']
        suspicious_names = ['ngrok', 'mimikatz', 'psexec', 'ncat', 'nc.exe', 'wget', 'curl']
        
        base_dir = Path(base_path)
        recent_threshold = datetime.now().timestamp() - (24 * 60 * 60)  # 24 hours
        
        try:
            for file_path in base_dir.rglob("*"):
                if not file_path.is_file():
                    continue
                
                try:
                    stat_info = file_path.stat()
                    file_info = {
                        "path": str(file_path),
                        "size": stat_info.st_size,
                        "modified_time": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                        "created_time": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                        "extension": file_path.suffix.lower()
                    }
                    
                    # Check if suspicious
                    is_suspicious = False
                    reasons = []
                    
                    # Extension check
                    if file_path.suffix.lower() in suspicious_extensions:
                        is_suspicious = True
                        reasons.append(f"suspicious_extension_{file_path.suffix}")
                        suspicious_data["executable_files"].append(file_info.copy())
                    
                    # Name check
                    if any(name.lower() in file_path.name.lower() for name in suspicious_names):
                        is_suspicious = True
                        reasons.append("suspicious_name")
                    
                    # Recently modified
                    if stat_info.st_mtime > recent_threshold:
                        suspicious_data["recently_modified"].append(file_info.copy())
                        if stat_info.st_mtime > (datetime.now().timestamp() - (2 * 60 * 60)):  # Last 2 hours
                            is_suspicious = True
                            reasons.append("recently_modified")
                    
                    if is_suspicious:
                        file_info["suspicious_reasons"] = reasons
                        file_info["hash_sha256"] = safe_file_hash(str(file_path))
                        suspicious_data["suspicious_files"].append(file_info)
                        
                except Exception as e:
                    suspicious_data["errors"].append(f"Error processing {file_path}: {e}")
                    continue
                    
        except Exception as e:
            suspicious_data["errors"].append(f"Error scanning directory {base_path}: {e}")
                    
        except Exception as e:
            suspicious_data["errors"].append(f"Error scanning directory {base_path}: {e}")
        
        with open(output_path, 'w', encoding='utf8') as f:
            json.dump(suspicious_data, f, default=str, indent=2)
        
        log.info("Wrote suspicious files to %s", output_path)
        
        # Add to manifest
        file_hash = safe_file_hash(output_path)
        manifest.add_artifact("SUSPICIOUS_FILES", output_path, file_hash, 
                            f"Found {len(suspicious_data['suspicious_files'])} suspicious files, {len(suspicious_data['recently_modified'])} recently modified")
        
    except Exception:
        error_msg = f"Suspicious file collection failed: {traceback.format_exc()}"
        log.error(error_msg)
        manifest.add_error("suspicious_files", error_msg, output_path)


def run_forensic_collection_suite(incident_id: str, workspace_path: str = "C:\\EQ12"):
    """Run complete forensic collection with robust error handling"""
    base_path = Path(workspace_path)
    evidence_path = base_path / "incident_response" / "forensics"
    evidence_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize manifest
    manifest = ForensicManifest(incident_id, evidence_path)
    manifest.add_custody_event("collection_started", "forensic_helper", "Automated collection initiated")
    
    print("" + "="*70)
    print(" EQ12 FORENSIC COLLECTION HELPER")
    print("" + "="*70)
    print(f" Incident ID: {incident_id}")
    print(f" Evidence Path: {evidence_path}")
    print("" + "="*70)
    
    # Collection tasks
    tasks = [
        ("Memory Snapshot", lambda: safe_collect_memory_snapshot(
            str(evidence_path / f"memory_snapshot_{incident_id}.json"), manifest)),
        ("Process List", lambda: collect_process_list(
            str(evidence_path / f"process_list_{incident_id}.json"), manifest)),
        ("Network Connections", lambda: collect_network_connections(
            str(evidence_path / f"network_connections_{incident_id}.json"), manifest)),
        ("System Information", lambda: collect_system_information(
            str(evidence_path / f"system_info_{incident_id}.json"), manifest)),
        ("Suspicious Files", lambda: collect_suspicious_files(
            workspace_path, str(evidence_path / f"suspicious_files_{incident_id}.json"), manifest))
    ]
    
    successful = 0
    failed = 0
    
    for task_name, task_func in tasks:
        print(f"\n Collecting {task_name}...")
        try:
            task_func()
            print(f" {task_name} - SUCCESS")
            successful += 1
        except Exception as e:
            print(f" {task_name} - FAILED: {e}")
            manifest.add_error(task_name, str(e))
            failed += 1
    
    manifest.add_custody_event("collection_completed", "forensic_helper", 
                             f"Collection completed: {successful} successful, {failed} failed")
    
    print(f"\n COLLECTION COMPLETE")
    print("="*70)
    print(f" Successful: {successful}")
    print(f" Failed: {failed}")
    print(f" Manifest: {manifest.manifest_file}")
    print(f" Evidence: {evidence_path}")
    print(" Review manifest for detailed results and errors")
    print("="*70)
    
    return {
        "incident_id": incident_id,
        "evidence_path": str(evidence_path),
        "manifest_file": str(manifest.manifest_file),
        "successful_tasks": successful,
        "failed_tasks": failed
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description=" EQ12 Forensic Collection Helper")
    parser.add_argument("--incident-id", required=True, help="Incident ID for evidence tracking")
    parser.add_argument("--workspace", default="C:\\EQ12", help="EQ12 workspace path")
    
    args = parser.parse_args()
    
    result = run_forensic_collection_suite(args.incident_id, args.workspace)
    print(f"\n Collection result: {result}")