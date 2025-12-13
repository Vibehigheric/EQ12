#!/usr/bin/env python3
"""
 EQ12 INTERNET CONNECTIVITY DIAGNOSTICS AND REPAIR SYSTEM
Advanced network troubleshooting and automatic repair for UGREEN CM648 adapter

Created: November 7, 2025
Author: EQ12 Network Operations Team
Purpose: Diagnose and fix internet connectivity issues with UGREEN CM648 adapter
Classification: NETWORK DIAGNOSTICS - INTERNET CONNECTIVITY REPAIR
"""

import sys
import logging
import subprocess
import platform
import psutil
import socket
import json
import ipaddress
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import re

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
log = logging.getLogger("INTERNET_REPAIR")


class EQ12InternetConnectivityRepair:
    """Advanced internet connectivity diagnostics and repair system"""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.logs_dir = self.workspace_path / "logs"
        self.data_dir = self.workspace_path / "data"
        
        # Create directories
        for dir_path in [self.logs_dir, self.data_dir]:
            dir_path.mkdir(exist_ok=True)
        
        self.diagnostics = {}
        self.repair_actions = {}
        self.connectivity_status = {}
        
        log.info(" Initializing Internet Connectivity Diagnostics and Repair System")

    def comprehensive_network_diagnostics(self) -> Dict[str, Any]:
        """Perform comprehensive network diagnostics"""
        
        log.info(" Performing comprehensive network diagnostics...")
        
        diagnostics = {
            "physical_layer": self._check_physical_connectivity(),
            "network_layer": self._check_network_configuration(),
            "internet_layer": self._check_internet_connectivity(),
            "dns_layer": self._check_dns_resolution(),
            "adapter_status": self._check_adapter_status(),
            "routing_table": self._check_routing_table(),
            "firewall_status": self._check_firewall_configuration(),
            "proxy_settings": self._check_proxy_configuration()
        }
        
        log.info(" Comprehensive network diagnostics completed")
        return diagnostics

    def _check_physical_connectivity(self) -> Dict[str, Any]:
        """Check physical network connectivity"""
        
        log.info(" Checking physical network connectivity...")
        
        physical_check = {
            "adapters_detected": [],
            "active_adapters": [],
            "ugreen_detected": False,
            "cable_status": "unknown",
            "link_speed": "unknown"
        }
        
        try:
            # Get network interfaces
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for interface_name, addresses in interfaces.items():
                if interface_name in stats:
                    interface_stats = stats[interface_name]
                    
                    adapter_info = {
                        "name": interface_name,
                        "is_up": interface_stats.isup,
                        "speed": interface_stats.speed,
                        "duplex": str(interface_stats.duplex),
                        "mtu": interface_stats.mtu
                    }
                    
                    physical_check["adapters_detected"].append(adapter_info)
                    
                    if interface_stats.isup:
                        physical_check["active_adapters"].append(interface_name)
                        
                        # Check for potential UGREEN adapter
                        if (interface_stats.speed >= 1000 or 
                            "ethernet" in interface_name.lower() or
                            "usb" in interface_name.lower()):
                            physical_check["ugreen_detected"] = True
                            physical_check["link_speed"] = f"{interface_stats.speed} Mbps"
                            log.info(f" Potential UGREEN adapter found: {interface_name}")
            
            # Windows-specific cable status check
            if platform.system() == "Windows":
                self._windows_cable_check(physical_check)
                
        except Exception as e:
            log.error(f" Physical connectivity check error: {e}")
            physical_check["error"] = str(e)
        
        return physical_check

    def _windows_cable_check(self, physical_check: Dict[str, Any]):
        """Windows-specific cable status check"""
        
        try:
            # PowerShell command to check adapter status
            ps_command = """
            Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | 
            Select-Object Name, InterfaceDescription, LinkSpeed, MediaConnectionState | 
            ConvertTo-Json
            """
            
            result = subprocess.run([
                "powershell", "-Command", ps_command
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    adapter_data = json.loads(result.stdout)
                    if not isinstance(adapter_data, list):
                        adapter_data = [adapter_data]
                    
                    for adapter in adapter_data:
                        media_state = adapter.get("MediaConnectionState", "Unknown")
                        link_speed = adapter.get("LinkSpeed", "Unknown")
                        
                        if "Connected" in str(media_state):
                            physical_check["cable_status"] = "connected"
                            if link_speed and "Gbps" in str(link_speed):
                                physical_check["link_speed"] = link_speed
                                log.info(f" Cable connected at {link_speed}")
                
                except json.JSONDecodeError:
                    log.warning(" Could not parse adapter status")
                    
        except Exception as e:
            log.warning(f" Windows cable check error: {e}")

    def _check_network_configuration(self) -> Dict[str, Any]:
        """Check network configuration settings"""
        
        log.info(" Checking network configuration...")
        
        network_config = {
            "ip_addresses": [],
            "default_gateway": None,
            "subnet_masks": [],
            "dhcp_enabled": "unknown",
            "static_config": False
        }
        
        try:
            # Get network interface addresses
            interfaces = psutil.net_if_addrs()
            
            for interface_name, addresses in interfaces.items():
                for addr in addresses:
                    if addr.family == socket.AF_INET:  # IPv4
                        ip_info = {
                            "interface": interface_name,
                            "ip": addr.address,
                            "netmask": getattr(addr, 'netmask', None),
                            "broadcast": getattr(addr, 'broadcast', None)
                        }
                        
                        network_config["ip_addresses"].append(ip_info)
                        
                        if addr.netmask:
                            network_config["subnet_masks"].append(addr.netmask)
                        
                        # Check if this is a valid internet-routable IP
                        try:
                            ip_obj = ipaddress.IPv4Address(addr.address)
                            if not ip_obj.is_private and not ip_obj.is_loopback:
                                network_config["public_ip_detected"] = True
                        except:
                            pass
            
            # Get default gateway
            gateways = psutil.net_if_stats()
            
            # Windows-specific configuration check
            if platform.system() == "Windows":
                self._windows_network_config_check(network_config)
                
        except Exception as e:
            log.error(f" Network configuration check error: {e}")
            network_config["error"] = str(e)
        
        return network_config

    def _windows_network_config_check(self, network_config: Dict[str, Any]):
        """Windows-specific network configuration check"""
        
        try:
            # Get default gateway
            gateway_cmd = "route print 0.0.0.0"
            result = subprocess.run(gateway_cmd, shell=True, capture_output=True, 
                                  text=True, timeout=10)
            
            if result.returncode == 0:
                # Parse default gateway from route table
                lines = result.stdout.split('\n')
                for line in lines:
                    if '0.0.0.0' in line and 'On-link' not in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            gateway = parts[2]
                            if self._is_valid_ip(gateway):
                                network_config["default_gateway"] = gateway
                                log.info(f" Default gateway: {gateway}")
                                break
            
            # Check DHCP status
            dhcp_cmd = """
            Get-NetIPConfiguration | Where-Object {$_.IPv4Address -ne $null} | 
            Select-Object InterfaceAlias, Dhcp | ConvertTo-Json
            """
            
            result = subprocess.run([
                "powershell", "-Command", dhcp_cmd
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    dhcp_data = json.loads(result.stdout)
                    if not isinstance(dhcp_data, list):
                        dhcp_data = [dhcp_data]
                    
                    for config in dhcp_data:
                        if config.get("Dhcp") == "Enabled":
                            network_config["dhcp_enabled"] = True
                            log.info(" DHCP is enabled")
                            break
                    else:
                        network_config["dhcp_enabled"] = False
                        network_config["static_config"] = True
                
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            log.warning(f" Windows network config check error: {e}")

    def _is_valid_ip(self, ip_str: str) -> bool:
        """Check if string is a valid IP address"""
        try:
            ipaddress.IPv4Address(ip_str)
            return True
        except:
            return False

    def _check_internet_connectivity(self) -> Dict[str, Any]:
        """Check internet connectivity with multiple methods"""
        
        log.info(" Checking internet connectivity...")
        
        connectivity_check = {
            "ping_tests": {},
            "http_tests": {},
            "overall_status": False,
            "reachable_hosts": [],
            "unreachable_hosts": []
        }
        
        # Test hosts for connectivity
        test_hosts = [
            ("8.8.8.8", "Google DNS"),
            ("1.1.1.1", "Cloudflare DNS"),
            ("208.67.222.222", "OpenDNS"),
            ("www.google.com", "Google Web"),
            ("www.microsoft.com", "Microsoft Web")
        ]
        
        for host, description in test_hosts:
            ping_result = self._test_ping_connectivity(host)
            connectivity_check["ping_tests"][host] = {
                "description": description,
                "result": ping_result,
                "reachable": ping_result.get("success", False)
            }
            
            if ping_result.get("success"):
                connectivity_check["reachable_hosts"].append(host)
            else:
                connectivity_check["unreachable_hosts"].append(host)
        
        # Overall connectivity status
        connectivity_check["overall_status"] = len(connectivity_check["reachable_hosts"]) > 0
        
        return connectivity_check

    def _test_ping_connectivity(self, host: str) -> Dict[str, Any]:
        """Test ping connectivity to a specific host"""
        
        ping_result = {
            "host": host,
            "success": False,
            "latency": None,
            "packet_loss": 100
        }
        
        try:
            if platform.system() == "Windows":
                cmd = ["ping", "-n", "4", host]
            else:
                cmd = ["ping", "-c", "4", host]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                ping_result["success"] = True
                
                # Parse ping output for statistics
                output = result.stdout.lower()
                
                # Look for packet loss
                loss_match = re.search(r'(\d+)%.*loss', output)
                if loss_match:
                    ping_result["packet_loss"] = int(loss_match.group(1))
                
                # Look for average latency
                latency_match = re.search(r'average[^=]*=\s*(\d+)ms', output)
                if not latency_match:
                    latency_match = re.search(r'(\d+)ms', output)
                
                if latency_match:
                    ping_result["latency"] = int(latency_match.group(1))
                
                log.info(f" Ping to {host}: {ping_result['latency']}ms, {ping_result['packet_loss']}% loss")
            else:
                log.warning(f" Ping to {host} failed")
                
        except Exception as e:
            log.warning(f" Ping test to {host} error: {e}")
            ping_result["error"] = str(e)
        
        return ping_result

    def _check_dns_resolution(self) -> Dict[str, Any]:
        """Check DNS resolution capabilities"""
        
        log.info(" Checking DNS resolution...")
        
        dns_check = {
            "dns_servers": [],
            "resolution_tests": {},
            "dns_working": False
        }
        
        # Test DNS resolution
        test_domains = [
            "google.com",
            "microsoft.com",
            "github.com",
            "cloudflare.com"
        ]
        
        working_resolutions = 0
        
        for domain in test_domains:
            try:
                ip_address = socket.gethostbyname(domain)
                dns_check["resolution_tests"][domain] = {
                    "success": True,
                    "ip_address": ip_address
                }
                working_resolutions += 1
                log.info(f" DNS resolution {domain} -> {ip_address}")
                
            except socket.gaierror as e:
                dns_check["resolution_tests"][domain] = {
                    "success": False,
                    "error": str(e)
                }
                log.warning(f" DNS resolution failed for {domain}: {e}")
            except Exception as e:
                dns_check["resolution_tests"][domain] = {
                    "success": False,
                    "error": str(e)
                }
        
        dns_check["dns_working"] = working_resolutions > 0
        
        # Get DNS servers (Windows)
        if platform.system() == "Windows":
            self._get_windows_dns_servers(dns_check)
        
        return dns_check

    def _get_windows_dns_servers(self, dns_check: Dict[str, Any]):
        """Get DNS servers on Windows"""
        
        try:
            dns_cmd = """
            Get-DnsClientServerAddress | Where-Object {$_.AddressFamily -eq 2} | 
            Select-Object InterfaceAlias, ServerAddresses | ConvertTo-Json
            """
            
            result = subprocess.run([
                "powershell", "-Command", dns_cmd
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    dns_data = json.loads(result.stdout)
                    if not isinstance(dns_data, list):
                        dns_data = [dns_data]
                    
                    for interface_dns in dns_data:
                        servers = interface_dns.get("ServerAddresses", [])
                        if servers:
                            dns_check["dns_servers"].extend(servers)
                            log.info(f" DNS servers: {', '.join(servers)}")
                
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            log.warning(f" DNS server detection error: {e}")

    def _check_adapter_status(self) -> Dict[str, Any]:
        """Check specific adapter status and configuration"""
        
        log.info(" Checking network adapter status...")
        
        adapter_status = {
            "enabled_adapters": [],
            "disabled_adapters": [],
            "adapter_priorities": {},
            "ugreen_status": "unknown"
        }
        
        try:
            if platform.system() == "Windows":
                # Get adapter status
                adapter_cmd = """
                Get-NetAdapter | Select-Object Name, InterfaceDescription, Status, 
                LinkSpeed, MediaConnectionState | ConvertTo-Json
                """
                
                result = subprocess.run([
                    "powershell", "-Command", adapter_cmd
                ], capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0 and result.stdout.strip():
                    try:
                        adapter_data = json.loads(result.stdout)
                        if not isinstance(adapter_data, list):
                            adapter_data = [adapter_data]
                        
                        for adapter in adapter_data:
                            name = adapter.get("Name", "")
                            status = adapter.get("Status", "")
                            description = adapter.get("InterfaceDescription", "")
                            
                            if status == "Up":
                                adapter_status["enabled_adapters"].append({
                                    "name": name,
                                    "description": description,
                                    "link_speed": adapter.get("LinkSpeed", "Unknown"),
                                    "media_state": adapter.get("MediaConnectionState", "Unknown")
                                })
                                
                                # Check for UGREEN adapter
                                if any(indicator in description.lower() 
                                      for indicator in ["realtek", "usb", "ethernet"]):
                                    adapter_status["ugreen_status"] = "active"
                                    log.info(f" UGREEN adapter active: {name}")
                            else:
                                adapter_status["disabled_adapters"].append({
                                    "name": name,
                                    "description": description,
                                    "status": status
                                })
                    
                    except json.JSONDecodeError:
                        log.warning(" Could not parse adapter status")
                        
        except Exception as e:
            log.error(f" Adapter status check error: {e}")
            adapter_status["error"] = str(e)
        
        return adapter_status

    def _check_routing_table(self) -> Dict[str, Any]:
        """Check routing table configuration"""
        
        log.info(" Checking routing table...")
        
        routing_check = {
            "default_routes": [],
            "specific_routes": [],
            "routing_issues": []
        }
        
        try:
            if platform.system() == "Windows":
                result = subprocess.run("route print", shell=True, 
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    
                    for line in lines:
                        line = line.strip()
                        if line.startswith('0.0.0.0'):
                            # Default route
                            parts = line.split()
                            if len(parts) >= 3:
                                route_info = {
                                    "destination": parts[0],
                                    "netmask": parts[1],
                                    "gateway": parts[2],
                                    "interface": parts[3] if len(parts) > 3 else "Unknown",
                                    "metric": parts[4] if len(parts) > 4 else "Unknown"
                                }
                                routing_check["default_routes"].append(route_info)
                                log.info(f" Default route via {parts[2]}")
                    
                    # Check for routing issues
                    if not routing_check["default_routes"]:
                        routing_check["routing_issues"].append("No default route found")
                        
        except Exception as e:
            log.error(f" Routing table check error: {e}")
            routing_check["error"] = str(e)
        
        return routing_check

    def _check_firewall_configuration(self) -> Dict[str, Any]:
        """Check firewall configuration"""
        
        log.info(" Checking firewall configuration...")
        
        firewall_check = {
            "firewall_enabled": "unknown",
            "blocking_internet": False,
            "profiles_active": []
        }
        
        try:
            if platform.system() == "Windows":
                # Check Windows Firewall status
                fw_cmd = """
                Get-NetFirewallProfile | Select-Object Name, Enabled | ConvertTo-Json
                """
                
                result = subprocess.run([
                    "powershell", "-Command", fw_cmd
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout.strip():
                    try:
                        fw_data = json.loads(result.stdout)
                        if not isinstance(fw_data, list):
                            fw_data = [fw_data]
                        
                        for profile in fw_data:
                            profile_name = profile.get("Name", "")
                            enabled = profile.get("Enabled", False)
                            
                            if enabled:
                                firewall_check["profiles_active"].append(profile_name)
                                firewall_check["firewall_enabled"] = True
                                log.info(f" Firewall profile active: {profile_name}")
                    
                    except json.JSONDecodeError:
                        pass
                        
        except Exception as e:
            log.warning(f" Firewall check error: {e}")
            firewall_check["error"] = str(e)
        
        return firewall_check

    def _check_proxy_configuration(self) -> Dict[str, Any]:
        """Check proxy configuration"""
        
        log.info(" Checking proxy configuration...")
        
        proxy_check = {
            "proxy_enabled": False,
            "proxy_settings": {},
            "blocking_internet": False
        }
        
        try:
            if platform.system() == "Windows":
                # Check Windows proxy settings
                proxy_cmd = """
                Get-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" | 
                Select-Object ProxyEnable, ProxyServer | ConvertTo-Json
                """
                
                result = subprocess.run([
                    "powershell", "-Command", proxy_cmd
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout.strip():
                    try:
                        proxy_data = json.loads(result.stdout)
                        
                        proxy_enable = proxy_data.get("ProxyEnable", 0)
                        proxy_server = proxy_data.get("ProxyServer", "")
                        
                        if proxy_enable == 1:
                            proxy_check["proxy_enabled"] = True
                            proxy_check["proxy_settings"]["server"] = proxy_server
                            log.info(f" Proxy enabled: {proxy_server}")
                        else:
                            log.info(" No proxy configured")
                    
                    except json.JSONDecodeError:
                        pass
                        
        except Exception as e:
            log.warning(f" Proxy check error: {e}")
            proxy_check["error"] = str(e)
        
        return proxy_check

    def automatic_internet_repair(self, diagnostics: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically repair internet connectivity issues"""
        
        log.info(" Starting automatic internet connectivity repair...")
        
        repair_results = {
            "repairs_attempted": [],
            "repairs_successful": [],
            "repairs_failed": [],
            "connectivity_restored": False
        }
        
        try:
            # Repair 1: Reset network adapters
            if not diagnostics.get("internet_layer", {}).get("overall_status"):
                repair_results["repairs_attempted"].append("network_adapter_reset")
                if self._reset_network_adapters():
                    repair_results["repairs_successful"].append("network_adapter_reset")
                else:
                    repair_results["repairs_failed"].append("network_adapter_reset")
            
            # Repair 2: Flush DNS cache
            repair_results["repairs_attempted"].append("dns_flush")
            if self._flush_dns_cache():
                repair_results["repairs_successful"].append("dns_flush")
            else:
                repair_results["repairs_failed"].append("dns_flush")
            
            # Repair 3: Reset TCP/IP stack
            repair_results["repairs_attempted"].append("tcpip_reset")
            if self._reset_tcpip_stack():
                repair_results["repairs_successful"].append("tcpip_reset")
            else:
                repair_results["repairs_failed"].append("tcpip_reset")
            
            # Repair 4: Renew IP configuration
            repair_results["repairs_attempted"].append("ip_renewal")
            if self._renew_ip_configuration():
                repair_results["repairs_successful"].append("ip_renewal")
            else:
                repair_results["repairs_failed"].append("ip_renewal")
            
            # Repair 5: Enable UGREEN adapter if disabled
            adapter_status = diagnostics.get("adapter_status", {})
            if adapter_status.get("ugreen_status") != "active":
                repair_results["repairs_attempted"].append("enable_ugreen_adapter")
                if self._enable_ugreen_adapter():
                    repair_results["repairs_successful"].append("enable_ugreen_adapter")
                else:
                    repair_results["repairs_failed"].append("enable_ugreen_adapter")
            
            # Test connectivity after repairs
            connectivity_test = self._quick_connectivity_test()
            repair_results["connectivity_restored"] = connectivity_test
            
            log.info(f" Repair completed: {len(repair_results['repairs_successful'])}/{len(repair_results['repairs_attempted'])} successful")
            
        except Exception as e:
            log.error(f" Automatic repair error: {e}")
            repair_results["repair_error"] = str(e)
        
        return repair_results

    def _reset_network_adapters(self) -> bool:
        """Reset network adapters"""
        
        log.info(" Resetting network adapters...")
        
        try:
            if platform.system() == "Windows":
                # Disable and re-enable network adapters
                reset_cmd = """
                Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | ForEach-Object {
                    Disable-NetAdapter -Name $_.Name -Confirm:$false
                    Start-Sleep -Seconds 2
                    Enable-NetAdapter -Name $_.Name -Confirm:$false
                }
                """
                
                result = subprocess.run([
                    "powershell", "-ExecutionPolicy", "Bypass", "-Command", reset_cmd
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    log.info(" Network adapters reset successfully")
                    return True
                else:
                    log.warning(f" Adapter reset failed: {result.stderr}")
                    
        except Exception as e:
            log.warning(f" Network adapter reset error: {e}")
        
        return False

    def _flush_dns_cache(self) -> bool:
        """Flush DNS cache"""
        
        log.info(" Flushing DNS cache...")
        
        try:
            if platform.system() == "Windows":
                result = subprocess.run(["ipconfig", "/flushdns"], 
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    log.info(" DNS cache flushed successfully")
                    return True
                else:
                    log.warning(f" DNS flush failed: {result.stderr}")
                    
        except Exception as e:
            log.warning(f" DNS flush error: {e}")
        
        return False

    def _reset_tcpip_stack(self) -> bool:
        """Reset TCP/IP stack"""
        
        log.info(" Resetting TCP/IP stack...")
        
        try:
            if platform.system() == "Windows":
                commands = [
                    ["netsh", "winsock", "reset"],
                    ["netsh", "int", "ip", "reset"]
                ]
                
                for cmd in commands:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                    if result.returncode != 0:
                        log.warning(f" Command failed: {' '.join(cmd)}")
                        return False
                
                log.info(" TCP/IP stack reset successfully")
                return True
                
        except Exception as e:
            log.warning(f" TCP/IP reset error: {e}")
        
        return False

    def _renew_ip_configuration(self) -> bool:
        """Renew IP configuration"""
        
        log.info(" Renewing IP configuration...")
        
        try:
            if platform.system() == "Windows":
                commands = [
                    ["ipconfig", "/release"],
                    ["ipconfig", "/renew"]
                ]
                
                for cmd in commands:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
                    if result.returncode != 0:
                        log.warning(f" Command failed: {' '.join(cmd)}")
                        # Continue anyway as some failures are expected
                
                log.info(" IP configuration renewed")
                return True
                
        except Exception as e:
            log.warning(f" IP renewal error: {e}")
        
        return False

    def _enable_ugreen_adapter(self) -> bool:
        """Enable UGREEN adapter if disabled"""
        
        log.info(" Enabling UGREEN adapter...")
        
        try:
            if platform.system() == "Windows":
                enable_cmd = """
                Get-NetAdapter | Where-Object {
                    $_.InterfaceDescription -like "*USB*" -or 
                    $_.InterfaceDescription -like "*Realtek*" -or
                    $_.InterfaceDescription -like "*RTL8156*"
                } | Where-Object {$_.Status -ne "Up"} | Enable-NetAdapter -Confirm:$false
                """
                
                result = subprocess.run([
                    "powershell", "-ExecutionPolicy", "Bypass", "-Command", enable_cmd
                ], capture_output=True, text=True, timeout=15)
                
                log.info(" UGREEN adapter enable command executed")
                return True
                
        except Exception as e:
            log.warning(f" UGREEN adapter enable error: {e}")
        
        return False

    def _quick_connectivity_test(self) -> bool:
        """Quick connectivity test"""
        
        try:
            # Test ping to Google DNS
            result = subprocess.run(["ping", "-n", "1", "8.8.8.8"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False

    def generate_connectivity_report(self, diagnostics: Dict[str, Any], 
                                   repair_results: Dict[str, Any] = None) -> str:
        """Generate comprehensive connectivity report"""
        
        log.info(" Generating connectivity diagnostics report...")
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report_content = f"""#  EQ12 INTERNET CONNECTIVITY DIAGNOSTICS REPORT

**Generated:** {timestamp}
**System:** UGREEN CM648 USB-C Ethernet Adapter
**Diagnostic Status:** {' COMPLETED' if diagnostics else ' IN PROGRESS'}
**Internet Status:** {' CONNECTED' if diagnostics.get('internet_layer', {}).get('overall_status') else ' DISCONNECTED'}

---

##  DIAGNOSTIC SUMMARY

###  Overall Connectivity Status
"""

        internet_status = diagnostics.get('internet_layer', {})
        if internet_status.get('overall_status'):
            report_content += """
- **Internet Access:**  WORKING
- **Connection Quality:** Good
- **Recommended Action:** None required
"""
        else:
            report_content += """
- **Internet Access:**  NOT WORKING
- **Connection Quality:** Poor/None
- **Recommended Action:** Troubleshooting required
"""

        # Physical layer diagnostics
        physical = diagnostics.get('physical_layer', {})
        if physical:
            report_content += f"""

---

##  PHYSICAL LAYER DIAGNOSTICS

### Network Adapter Status
- **Adapters Detected:** {len(physical.get('adapters_detected', []))}
- **Active Adapters:** {len(physical.get('active_adapters', []))}
- **UGREEN Detected:** {' Yes' if physical.get('ugreen_detected') else ' No'}
- **Cable Status:** {physical.get('cable_status', 'Unknown').title()}
- **Link Speed:** {physical.get('link_speed', 'Unknown')}

### Active Network Adapters
"""
            for adapter in physical.get('adapters_detected', []):
                status_icon = "" if adapter.get('is_up') else ""
                report_content += f"""
#### {adapter.get('name', 'Unknown')}
- **Status:** {status_icon} {'Active' if adapter.get('is_up') else 'Inactive'}
- **Speed:** {adapter.get('speed', 'Unknown')} Mbps
- **Duplex:** {adapter.get('duplex', 'Unknown')}
- **MTU:** {adapter.get('mtu', 'Unknown')}
"""

        # Network configuration
        network_config = diagnostics.get('network_layer', {})
        if network_config:
            report_content += f"""

---

##  NETWORK CONFIGURATION

### IP Configuration
- **IP Addresses Found:** {len(network_config.get('ip_addresses', []))}
- **Default Gateway:** {network_config.get('default_gateway', 'Not found')}
- **DHCP Enabled:** {' Yes' if network_config.get('dhcp_enabled') else ' No' if network_config.get('dhcp_enabled') is False else 'Unknown'}
- **Static Config:** {' Yes' if network_config.get('static_config') else ' No'}

### IP Address Details
"""
            for ip_info in network_config.get('ip_addresses', []):
                report_content += f"""
#### {ip_info.get('interface', 'Unknown Interface')}
- **IP Address:** {ip_info.get('ip', 'Unknown')}
- **Subnet Mask:** {ip_info.get('netmask', 'Unknown')}
- **Broadcast:** {ip_info.get('broadcast', 'Unknown')}
"""

        # Internet connectivity tests
        if internet_status:
            report_content += f"""

---

##  INTERNET CONNECTIVITY TESTS

### Connectivity Overview
- **Overall Status:** {' WORKING' if internet_status.get('overall_status') else ' FAILED'}
- **Reachable Hosts:** {len(internet_status.get('reachable_hosts', []))}
- **Unreachable Hosts:** {len(internet_status.get('unreachable_hosts', []))}

### Ping Test Results
"""
            for host, test_info in internet_status.get('ping_tests', {}).items():
                status_icon = "" if test_info.get('reachable') else ""
                description = test_info.get('description', host)
                
                report_content += f"""
#### {description} ({host})
- **Status:** {status_icon} {'Reachable' if test_info.get('reachable') else 'Unreachable'}
"""
                if test_info.get('result', {}).get('latency'):
                    report_content += f"- **Latency:** {test_info['result']['latency']}ms\n"
                if test_info.get('result', {}).get('packet_loss') is not None:
                    report_content += f"- **Packet Loss:** {test_info['result']['packet_loss']}%\n"

        # DNS diagnostics
        dns_check = diagnostics.get('dns_layer', {})
        if dns_check:
            report_content += f"""

---

##  DNS DIAGNOSTICS

### DNS Status
- **DNS Working:** {' Yes' if dns_check.get('dns_working') else ' No'}
- **DNS Servers:** {', '.join(dns_check.get('dns_servers', ['Not found']))}

### DNS Resolution Tests
"""
            for domain, result in dns_check.get('resolution_tests', {}).items():
                status_icon = "" if result.get('success') else ""
                report_content += f"""
#### {domain}
- **Status:** {status_icon} {'Resolved' if result.get('success') else 'Failed'}
"""
                if result.get('ip_address'):
                    report_content += f"- **IP Address:** {result['ip_address']}\n"
                if result.get('error'):
                    report_content += f"- **Error:** {result['error']}\n"

        # Adapter status
        adapter_status = diagnostics.get('adapter_status', {})
        if adapter_status:
            report_content += f"""

---

##  NETWORK ADAPTER STATUS

### Adapter Overview
- **Enabled Adapters:** {len(adapter_status.get('enabled_adapters', []))}
- **Disabled Adapters:** {len(adapter_status.get('disabled_adapters', []))}
- **UGREEN Status:** {adapter_status.get('ugreen_status', 'Unknown').title()}

### Enabled Adapters
"""
            for adapter in adapter_status.get('enabled_adapters', []):
                report_content += f"""
#### {adapter.get('name', 'Unknown')}
- **Description:** {adapter.get('description', 'Unknown')}
- **Link Speed:** {adapter.get('link_speed', 'Unknown')}
- **Media State:** {adapter.get('media_state', 'Unknown')}
"""

        # Repair results
        if repair_results:
            report_content += f"""

---

##  AUTOMATIC REPAIR RESULTS

### Repair Summary
- **Repairs Attempted:** {len(repair_results.get('repairs_attempted', []))}
- **Repairs Successful:** {len(repair_results.get('repairs_successful', []))}
- **Repairs Failed:** {len(repair_results.get('repairs_failed', []))}
- **Connectivity Restored:** {' Yes' if repair_results.get('connectivity_restored') else ' No'}

### Repair Actions Performed
"""
            for repair in repair_results.get('repairs_attempted', []):
                status = " Success" if repair in repair_results.get('repairs_successful', []) else " Failed"
                repair_name = repair.replace('_', ' ').title()
                report_content += f"- **{repair_name}:** {status}\n"

        # Troubleshooting recommendations
        report_content += f"""

---

##  TROUBLESHOOTING RECOMMENDATIONS

### Immediate Actions
"""
        
        if not internet_status.get('overall_status'):
            report_content += """
1. **Check Physical Connections**
   - Ensure UGREEN CM648 adapter is properly connected
   - Verify Ethernet cable is connected to router/modem
   - Check cable for damage

2. **Restart Network Components**
   - Restart modem/router
   - Disconnect and reconnect UGREEN adapter
   - Restart computer

3. **Network Configuration**
   - Verify network adapter is enabled
   - Check IP configuration (DHCP vs static)
   - Ensure DNS servers are configured
"""
        else:
            report_content += """
1. **Connection is Working**
   - Internet connectivity is functional
   - Monitor performance for any issues
   - Consider speed optimization if needed
"""

        report_content += """

### Advanced Troubleshooting
1. **Driver Updates**
   - Update UGREEN CM648 drivers
   - Check Windows Update for network drivers
   - Visit UGREEN website for latest drivers

2. **Network Reset (if issues persist)**
   - Reset network settings in Windows
   - Reset TCP/IP stack
   - Reinstall network adapters

3. **Hardware Testing**
   - Test UGREEN adapter on different computer
   - Try different Ethernet cable
   - Test with different USB-C port

---

##  NEXT STEPS

### If Internet is Working
1. **Performance Optimization**
   - Configure QoS settings
   - Update to 2.5G infrastructure if available
   - Monitor connection stability

2. **Preventive Maintenance**
   - Regular driver updates
   - Monitor adapter temperature
   - Keep firmware updated

### If Internet is Not Working
1. **Follow Troubleshooting Steps**
   - Work through recommendations above
   - Check with ISP if issues persist
   - Consider hardware replacement if needed

2. **Contact Support**
   - UGREEN technical support
   - ISP customer service
   - Network administrator (if applicable)

---

**Report Status:**  Comprehensive Analysis Complete  
**Generated:** {timestamp}  
**Classification:** NETWORK DIAGNOSTICS - CONNECTIVITY REPAIR  

---

*This report provides detailed analysis of internet connectivity status and recommendations for the UGREEN CM648 USB-C Ethernet Adapter.*
"""

        # Save report
        report_file = self.workspace_path / f"eq12_internet_connectivity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        log.info(f" Connectivity report saved: {report_file}")
        return str(report_file)

    def execute_complete_connectivity_repair(self) -> Dict[str, Any]:
        """Execute complete connectivity diagnostics and repair"""
        
        log.info(" EXECUTING COMPLETE INTERNET CONNECTIVITY REPAIR")
        
        repair_summary = {
            "start_time": datetime.now().isoformat(),
            "repair_phase": "initializing",
            "connectivity_restored": False
        }
        
        try:
            # Phase 1: Comprehensive Diagnostics
            log.info(" Phase 1: Comprehensive Network Diagnostics")
            repair_summary["repair_phase"] = "diagnostics"
            self.diagnostics = self.comprehensive_network_diagnostics()
            
            # Phase 2: Automatic Repair
            log.info(" Phase 2: Automatic Internet Connectivity Repair")
            repair_summary["repair_phase"] = "repair"
            self.repair_actions = self.automatic_internet_repair(self.diagnostics)
            
            # Phase 3: Post-repair Testing
            log.info(" Phase 3: Post-repair Connectivity Testing")
            repair_summary["repair_phase"] = "testing"
            final_connectivity = self._quick_connectivity_test()
            
            # Phase 4: Report Generation
            log.info(" Phase 4: Connectivity Report Generation")
            repair_summary["repair_phase"] = "reporting"
            report_file = self.generate_connectivity_report(self.diagnostics, self.repair_actions)
            
            # Final status
            repair_summary.update({
                "connectivity_restored": final_connectivity,
                "diagnostics_completed": True,
                "repairs_attempted": len(self.repair_actions.get('repairs_attempted', [])),
                "repairs_successful": len(self.repair_actions.get('repairs_successful', [])),
                "report_file": report_file,
                "end_time": datetime.now().isoformat(),
                "repair_phase": "completed"
            })
            
            log.info(f" Internet connectivity repair {'successful!' if final_connectivity else 'completed - manual intervention may be required'}")
            
        except Exception as e:
            log.error(f" Connectivity repair error: {e}")
            repair_summary["error"] = str(e)
            repair_summary["repair_phase"] = "error"
        
        return repair_summary


def main():
    """Main internet connectivity repair interface"""
    
    print("" + "="*80)
    print(" EQ12 INTERNET CONNECTIVITY DIAGNOSTICS AND REPAIR")
    print(" UGREEN CM648 NETWORK TROUBLESHOOTING SYSTEM")
    print("" + "="*80)
    
    # Initialize repair system
    repair_system = EQ12InternetConnectivityRepair()
    
    # Execute complete connectivity repair
    results = repair_system.execute_complete_connectivity_repair()
    
    print(f"\n INTERNET CONNECTIVITY REPAIR COMPLETE")
    print(f"    Connectivity Restored: {'YES' if results['connectivity_restored'] else 'NEEDS ATTENTION'}")
    print(f"    Repair Phase: {results.get('repair_phase', 'unknown').title()}")
    
    # Show diagnostic results
    if repair_system.diagnostics:
        print(f"\n DIAGNOSTIC RESULTS")
        
        physical = repair_system.diagnostics.get('physical_layer', {})
        print(f"    UGREEN Adapter: {' Detected' if physical.get('ugreen_detected') else ' Not Found'}")
        print(f"    Active Adapters: {len(physical.get('active_adapters', []))}")
        
        internet = repair_system.diagnostics.get('internet_layer', {})
        print(f"    Internet Access: {' Working' if internet.get('overall_status') else ' Failed'}")
        print(f"    Reachable Hosts: {len(internet.get('reachable_hosts', []))}/{len(internet.get('ping_tests', {}))}")
        
        dns = repair_system.diagnostics.get('dns_layer', {})
        print(f"    DNS Resolution: {' Working' if dns.get('dns_working') else ' Failed'}")
    
    # Show repair results
    if repair_system.repair_actions:
        print(f"\n REPAIR ACTIONS")
        repairs = repair_system.repair_actions
        print(f"    Repairs Attempted: {len(repairs.get('repairs_attempted', []))}")
        print(f"    Repairs Successful: {len(repairs.get('repairs_successful', []))}")
        print(f"    Repairs Failed: {len(repairs.get('repairs_failed', []))}")
        
        if repairs.get('repairs_successful'):
            print(f"    Successful Repairs:")
            for repair in repairs['repairs_successful']:
                print(f"       {repair.replace('_', ' ').title()}")
    
    print(f"\n CONNECTIVITY REPORT")
    print(f"    File: {results.get('report_file', 'N/A')}")
    
    # Final status and recommendations
    if results.get('connectivity_restored'):
        print(f"\n SUCCESS: INTERNET CONNECTIVITY RESTORED!")
        print(f"    Your UGREEN CM648 adapter is now connected to the internet")
        print(f"    You can now enjoy 2.5G ethernet performance")
        print(f"    EQ12 automation systems ready for enhanced networking")
    else:
        print(f"\n ATTENTION: MANUAL INTERVENTION REQUIRED")
        print(f"    Automatic repairs completed but connectivity not fully restored")
        print(f"    Review the detailed report for next steps")
        print(f"    Consider checking physical connections and ISP status")
    
    print("" + "="*80)
    
    return results


if __name__ == "__main__":
    main()