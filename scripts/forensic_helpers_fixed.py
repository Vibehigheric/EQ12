#!/usr/bin/env python3
"""
 EQ12 FORENSIC COLLECTION HELPER TOOLKIT (FIXED)
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
from datetime import datetime
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("FORENSIC_HELPER")


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


def run_forensic_collection_suite(incident_id: str, workspace_path: str = "C:\\EQ12"):
    """Run complete forensic collection with robust error handling"""
    base_path = Path(workspace_path)
    evidence_path = base_path / "incident_response" / "forensics"
    evidence_path.mkdir(parents=True, exist_ok=True)
    
    print("" + "="*70)
    print(" EQ12 FORENSIC COLLECTION HELPER")
    print("" + "="*70)
    print(f" Incident ID: {incident_id}")
    print(f" Evidence Path: {evidence_path}")
    print("" + "="*70)
    
    successful = 0
    failed = 0
    
    # Task 1: Process Collection
    print(f"\n Collecting Process Information...")
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time', 'username', 'cmdline']):
            try:
                info = proc.info
                if info['create_time']:
                    info['create_time'] = datetime.fromtimestamp(info['create_time']).isoformat()
                processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        process_file = evidence_path / f"processes_{incident_id}.json"
        with open(process_file, 'w', encoding='utf8') as f:
            json.dump({"processes": processes, "count": len(processes)}, f, indent=2, default=str)
        
        print(f" Process Information - SUCCESS ({len(processes)} processes)")
        successful += 1
    except Exception as e:
        print(f" Process Information - FAILED: {e}")
        failed += 1
    
    # Task 2: Network Connections
    print(f"\n Collecting Network Connections...")
    try:
        connections = []
        for conn in psutil.net_connections(kind='inet'):
            connections.append({
                'laddr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                'raddr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                'status': conn.status,
                'pid': conn.pid
            })
        
        network_file = evidence_path / f"network_{incident_id}.json"
        with open(network_file, 'w', encoding='utf8') as f:
            json.dump({"connections": connections, "count": len(connections)}, f, indent=2)
        
        print(f" Network Connections - SUCCESS ({len(connections)} connections)")
        successful += 1
    except Exception as e:
        print(f" Network Connections - FAILED: {e}")
        failed += 1
    
    # Task 3: System Information
    print(f"\n Collecting System Information...")
    try:
        system_info = {
            "platform": sys.platform,
            "hostname": os.environ.get('COMPUTERNAME', os.environ.get('HOSTNAME', 'unknown')),
            "username": os.environ.get('USERNAME', os.environ.get('USER', 'unknown')),
            "python_version": sys.version,
            "collection_time": datetime.now().isoformat()
        }
        
        # Add memory info
        try:
            vm = psutil.virtual_memory()
            system_info["memory"] = {
                "total": vm.total,
                "available": vm.available,
                "percent": vm.percent,
                "used": vm.used,
                "free": vm.free
            }
        except Exception as e:
            system_info["memory_error"] = str(e)
        
        system_file = evidence_path / f"system_{incident_id}.json"
        with open(system_file, 'w', encoding='utf8') as f:
            json.dump(system_info, f, indent=2)
        
        print(f" System Information - SUCCESS")
        successful += 1
    except Exception as e:
        print(f" System Information - FAILED: {e}")
        failed += 1
    
    # Task 4: File Hashes
    print(f"\n Collecting File Hashes...")
    try:
        target_files = [
            str(base_path / "EdgeGodParlays" / "ngrok.exe"),
            str(base_path / "scripts" / "*.py"),
        ]
        
        file_hashes = []
        for pattern in target_files:
            try:
                if '*' in pattern:
                    # Handle wildcard patterns
                    from glob import glob
                    files = glob(pattern)
                else:
                    files = [pattern] if Path(pattern).exists() else []
                
                for file_path in files:
                    hash_result = safe_file_hash(file_path)
                    file_hashes.append({
                        "file_path": file_path,
                        "hash_result": hash_result,
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                file_hashes.append({
                    "file_path": pattern,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        hash_file = evidence_path / f"file_hashes_{incident_id}.json"
        with open(hash_file, 'w', encoding='utf8') as f:
            json.dump({"file_hashes": file_hashes, "count": len(file_hashes)}, f, indent=2)
        
        print(f" File Hashes - SUCCESS ({len(file_hashes)} files)")
        successful += 1
    except Exception as e:
        print(f" File Hashes - FAILED: {e}")
        failed += 1
    
    # Create summary manifest
    print(f"\n Creating Evidence Manifest...")
    try:
        manifest = {
            "incident_id": incident_id,
            "collection_time": datetime.now().isoformat(),
            "evidence_path": str(evidence_path),
            "successful_tasks": successful,
            "failed_tasks": failed,
            "total_tasks": successful + failed,
            "collection_status": "COMPLETE" if failed == 0 else "PARTIAL"
        }
        
        manifest_file = evidence_path / f"manifest_{incident_id}.json"
        with open(manifest_file, 'w', encoding='utf8') as f:
            json.dump(manifest, f, indent=2)
        
        print(f" Evidence Manifest - SUCCESS")
    except Exception as e:
        print(f" Evidence Manifest - FAILED: {e}")
    
    print(f"\n COLLECTION COMPLETE")
    print("="*70)
    print(f" Successful: {successful}")
    print(f" Failed: {failed}")
    print(f" Evidence: {evidence_path}")
    print("="*70)
    
    return {
        "incident_id": incident_id,
        "evidence_path": str(evidence_path),
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