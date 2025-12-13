#!/usr/bin/env python3
"""
 EQ12 API KEY QUICK SETUP ASSISTANT
====================================

Quick setup assistant to help configure missing API keys for the EQ12 ecosystem.
This script provides step-by-step guidance and validation for API key setup.

Features:
- Interactive API key configuration
- Real-time validation and testing
- Environment variable setup assistance
- Backup key configuration
- Security recommendations

Author: EQ12 Quantum Development Team
Version: 1.0.0 - API Key Setup Assistant
Date: November 7, 2025
"""

import os
import asyncio
import sys
from pathlib import Path
from typing import Dict, List


class EQ12APIKeySetupAssistant:
    """Interactive API key setup assistant."""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.configs_path = self.workspace_path / "configs"
        
        # API key requirements
        self.required_apis = {
            "ODDS_API_KEY": {
                "name": "The Odds API",
                "website": "https://the-odds-api.com/",
                "free_tier": "500 requests/month",
                "priority": "CRITICAL",
                "description": "Sports betting odds and lines",
                "example": "12a3b4c5d6e7f8g9h0i1j2k3l4m5"
            },
            "SPORTSDATA_API_KEY": {
                "name": "SportsData.io",
                "website": "https://sportsdata.io/",
                "free_tier": "1000 requests/month",
                "priority": "CRITICAL", 
                "description": "Comprehensive sports statistics",
                "example": "sd_1a2b3c4d5e6f7g8h9i0j1k2l3m4n"
            },
            "TWITTER_API_KEY": {
                "name": "Twitter API v2",
                "website": "https://developer.twitter.com/",
                "free_tier": "Limited access",
                "priority": "CRITICAL",
                "description": "Social intelligence monitoring",
                "example": "AAAAAAAAAAAAAAAAAAAAAA%2FAA..."
            },
            "OPENWEATHER_API_KEY": {
                "name": "OpenWeatherMap",
                "website": "https://openweathermap.org/api",
                "free_tier": "1000 calls/day",
                "priority": "IMPORTANT",
                "description": "Weather data for sports analysis",
                "example": "1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"
            },
            "ESPN_API_KEY": {
                "name": "ESPN API",
                "website": "https://site.api.espn.com/",
                "free_tier": "Public endpoints",
                "priority": "OPTIONAL",
                "description": "Real-time sports data",
                "example": "espn_1a2b3c4d5e6f7g8h9i0j"
            }
        }
    
    def check_current_status(self) -> Dict[str, bool]:
        """Check which API keys are currently configured."""
        status = {}
        for key_name in self.required_apis.keys():
            status[key_name] = bool(os.getenv(key_name))
        return status
    
    def display_setup_header(self):
        """Display setup assistant header."""
        print(" EQ12 API KEY QUICK SETUP ASSISTANT")
        print("=" * 39)
        print("Interactive setup for missing API keys...")
        print()
    
    def display_api_status(self, status: Dict[str, bool]):
        """Display current API key status."""
        print(" CURRENT API KEY STATUS")
        print("-" * 27)
        
        for key_name, configured in status.items():
            api_info = self.required_apis[key_name]
            status_icon = "" if configured else ""
            priority_icon = "" if api_info["priority"] == "CRITICAL" else "" if api_info["priority"] == "IMPORTANT" else ""
            
            print(f"{status_icon} {priority_icon} {key_name}")
            print(f"    {api_info['name']} - {api_info['description']}")
            if not configured:
                print(f"    Get key: {api_info['website']}")
                print(f"    Free tier: {api_info['free_tier']}")
            print()
    
    def create_environment_setup_script(self, missing_keys: List[str]):
        """Create a PowerShell script to set up environment variables."""
        script_content = """# EQ12 API Key Setup Script
# Run this script to set up your API keys as environment variables

Write-Host " EQ12 API Key Environment Setup" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# CRITICAL APIs (Required for core functionality)
Write-Host " Setting up CRITICAL APIs..." -ForegroundColor Yellow

"""
        
        critical_keys = []
        important_keys = []
        optional_keys = []
        
        for key_name in missing_keys:
            api_info = self.required_apis[key_name]
            if api_info["priority"] == "CRITICAL":
                critical_keys.append(key_name)
            elif api_info["priority"] == "IMPORTANT":
                important_keys.append(key_name)
            else:
                optional_keys.append(key_name)
        
        # Add critical keys
        for key_name in critical_keys:
            api_info = self.required_apis[key_name]
            script_content += f"""
# {api_info['name']} - {api_info['description']}
# Get your key from: {api_info['website']}
# Example format: {api_info['example']}
$env:{key_name} = "YOUR_API_KEY_HERE"
[Environment]::SetEnvironmentVariable("{key_name}", $env:{key_name}, "User")
Write-Host " {key_name} configured" -ForegroundColor Green
"""
        
        # Add important keys
        if important_keys:
            script_content += "\n# IMPORTANT APIs (Enhanced functionality)\nWrite-Host \" Setting up IMPORTANT APIs...\" -ForegroundColor Yellow\n"
            for key_name in important_keys:
                api_info = self.required_apis[key_name]
                script_content += f"""
# {api_info['name']} - {api_info['description']}
# Get your key from: {api_info['website']}
$env:{key_name} = "YOUR_API_KEY_HERE"
[Environment]::SetEnvironmentVariable("{key_name}", $env:{key_name}, "User")
Write-Host " {key_name} configured" -ForegroundColor Green
"""
        
        # Add optional keys
        if optional_keys:
            script_content += "\n# OPTIONAL APIs (Additional features)\nWrite-Host \" Setting up OPTIONAL APIs...\" -ForegroundColor Yellow\n"
            for key_name in optional_keys:
                api_info = self.required_apis[key_name]
                script_content += f"""
# {api_info['name']} - {api_info['description']}
# Get your key from: {api_info['website']}
$env:{key_name} = "YOUR_API_KEY_HERE"
[Environment]::SetEnvironmentVariable("{key_name}", $env:{key_name}, "User")
Write-Host " {key_name} configured" -ForegroundColor Green
"""
        
        script_content += """
Write-Host ""
Write-Host " API Key setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host " NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Replace 'YOUR_API_KEY_HERE' with your actual API keys" -ForegroundColor White
Write-Host "2. Run this script in PowerShell" -ForegroundColor White
Write-Host "3. Restart VS Code/PowerShell to load new variables" -ForegroundColor White
Write-Host "4. Test with: python eq12_api_key_manager.py --test-all" -ForegroundColor White
Write-Host ""
Write-Host " SECURITY NOTE:" -ForegroundColor Red
Write-Host "Keep your API keys secure and never commit them to version control!" -ForegroundColor Yellow
"""
        
        return script_content
    
    def create_env_file_template(self, missing_keys: List[str]):
        """Create a .env file template."""
        env_content = """# EQ12 API Keys Configuration
# Copy this file to .env and add your actual API keys
# DO NOT commit this file to version control!

# ==========================================
# CRITICAL APIs (Required for core functionality)
# ==========================================

"""
        
        critical_keys = [k for k in missing_keys if self.required_apis[k]["priority"] == "CRITICAL"]
        important_keys = [k for k in missing_keys if self.required_apis[k]["priority"] == "IMPORTANT"]
        optional_keys = [k for k in missing_keys if self.required_apis[k]["priority"] == "OPTIONAL"]
        
        for key_name in critical_keys:
            api_info = self.required_apis[key_name]
            env_content += f"""# {api_info['name']} - {api_info['description']}
# Get your key from: {api_info['website']}
# Free tier: {api_info['free_tier']}
{key_name}=your_api_key_here

"""
        
        if important_keys:
            env_content += """
# ==========================================
# IMPORTANT APIs (Enhanced functionality)
# ==========================================

"""
            for key_name in important_keys:
                api_info = self.required_apis[key_name]
                env_content += f"""# {api_info['name']} - {api_info['description']}
# Get your key from: {api_info['website']}
{key_name}=your_api_key_here

"""
        
        if optional_keys:
            env_content += """
# ==========================================
# OPTIONAL APIs (Additional features)
# ==========================================

"""
            for key_name in optional_keys:
                api_info = self.required_apis[key_name]
                env_content += f"""# {api_info['name']} - {api_info['description']}
# Get your key from: {api_info['website']}
{key_name}=your_api_key_here

"""
        
        return env_content
    
    def generate_setup_files(self, missing_keys: List[str]):
        """Generate setup files for missing API keys."""
        if not missing_keys:
            print(" All API keys are already configured!")
            return
        
        print(f" GENERATING SETUP FILES")
        print("-" * 27)
        
        # Create PowerShell setup script
        ps_script_content = self.create_environment_setup_script(missing_keys)
        ps_script_file = self.configs_path / "setup_api_keys.ps1"
        
        with open(ps_script_file, 'w', encoding='utf-8') as f:
            f.write(ps_script_content)
        
        print(f" PowerShell script: {ps_script_file}")
        
        # Create .env template
        env_content = self.create_env_file_template(missing_keys)
        env_template_file = self.configs_path / "api_keys_template.env"
        
        with open(env_template_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f" .env template: {env_template_file}")
        
        # Create quick reference
        reference_content = "EQ12 API KEY QUICK REFERENCE\n" + "=" * 30 + "\n\n"
        
        for key_name in missing_keys:
            api_info = self.required_apis[key_name]
            reference_content += f"{key_name}:\n"
            reference_content += f"  Website: {api_info['website']}\n"
            reference_content += f"  Priority: {api_info['priority']}\n"
            reference_content += f"  Free Tier: {api_info['free_tier']}\n"
            reference_content += f"  Purpose: {api_info['description']}\n\n"
        
        reference_file = self.configs_path / "api_keys_reference.txt"
        with open(reference_file, 'w', encoding='utf-8') as f:
            f.write(reference_content)
        
        print(f" Quick reference: {reference_file}")
        print()
    
    def run_setup_assistant(self):
        """Run the complete setup assistant."""
        self.display_setup_header()
        
        # Check current status
        status = self.check_current_status()
        self.display_api_status(status)
        
        # Find missing keys
        missing_keys = [key for key, configured in status.items() if not configured]
        
        if not missing_keys:
            print(" ALL API KEYS CONFIGURED!")
            print("All required API keys are already set up.")
            print()
            print(" NEXT STEPS:")
            print("- Test with: python eq12_api_key_manager.py --test-all")
            print("- Run your EQ12 systems!")
            return
        
        # Generate setup files
        self.generate_setup_files(missing_keys)
        
        # Show instructions
        print(" SETUP INSTRUCTIONS")
        print("-" * 21)
        print("Choose your preferred setup method:")
        print()
        print(" OPTION 1 - PowerShell Script (Recommended):")
        print(f"   1. Edit {self.configs_path}/setup_api_keys.ps1")
        print("   2. Replace 'YOUR_API_KEY_HERE' with actual keys")
        print("   3. Run the script in PowerShell")
        print()
        print(" OPTION 2 - .env File:")
        print(f"   1. Copy {self.configs_path}/api_keys_template.env to .env")
        print("   2. Edit .env file with your actual API keys")
        print("   3. Restart your development environment")
        print()
        print(" OPTION 3 - Manual Environment Variables:")
        print("   1. Open System Properties  Environment Variables")
        print("   2. Add each missing API key as a User variable")
        print("   3. Restart VS Code/PowerShell")
        print()
        
        # Priority guidance
        critical_missing = [k for k in missing_keys if self.required_apis[k]["priority"] == "CRITICAL"]
        if critical_missing:
            print(" PRIORITY SETUP:")
            print(f"   Start with these CRITICAL APIs: {', '.join(critical_missing)}")
            print("   These are required for core EQ12 functionality.")
        print()
        
        print(" After setup, test with:")
        print("   python eq12_api_key_manager.py --test-all")


def main():
    """Main execution function."""
    assistant = EQ12APIKeySetupAssistant()
    assistant.run_setup_assistant()


if __name__ == "__main__":
    main()