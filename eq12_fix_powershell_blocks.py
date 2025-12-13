#!/usr/bin/env python3
"""
EQ12 PowerShell Auto-Repair System
Automatically fixes common PowerShell syntax errors in EQ12 scripts.
"""

import re
import pathlib
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def auto_repair_ps1(file_path):
    """Auto-repair PowerShell syntax issues in a .ps1 file."""
    try:
        file_obj = pathlib.Path(file_path)
        if not file_obj.exists():
            logger.warning(f"File not found: {file_path}")
            return False
        
        # Read the file content
        text = file_obj.read_text(encoding="utf-8")
        original_text = text
        
        # Track repairs made
        repairs_made = []
        
        # 1. Fix unterminated strings (quotes)
        # Replace Write-Host "text' with Write-Host "text"
        pattern1 = r'Write-Host\s+"([^"]*)\''
        if re.search(pattern1, text):
            text = re.sub(pattern1, r'Write-Host "\1"', text)
            repairs_made.append("Fixed unterminated strings")
        
        # 2. Fix missing try/catch/finally blocks
        # Find try blocks without proper catch
        try_pattern = r'try\s*\{'
        catch_pattern = r'\}\s*catch\s*\{'
        finally_pattern = r'\}\s*finally\s*\{'
        
        # Count try blocks and catch blocks
        try_count = len(re.findall(try_pattern, text))
        catch_count = len(re.findall(catch_pattern, text))
        
        # If we have more try blocks than catch blocks, add basic catch blocks
        if try_count > catch_count:
            # Find try blocks that don't have a following catch
            lines = text.split('\n')
            new_lines = []
            in_try_block = False
            brace_count = 0
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                
                # Check if this line starts a try block
                if re.search(r'try\s*\{', line):
                    in_try_block = True
                    brace_count = 1
                elif in_try_block:
                    # Count braces to find the end of the try block
                    brace_count += line.count('{') - line.count('}')
                    
                    # If we've closed the try block
                    if brace_count <= 0:
                        # Check if the next non-empty line is a catch
                        next_catch = False
                        for j in range(i + 1, min(i + 3, len(lines))):
                            if j < len(lines):
                                next_line = lines[j].strip()
                                if next_line and re.search(r'catch\s*\{', next_line):
                                    next_catch = True
                                    break
                                elif next_line and not re.match(r'^\s*$', next_line):
                                    break
                        
                        # If no catch found, add one
                        if not next_catch:
                            new_lines.append("catch {")
                            new_lines.append('    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red')
                            new_lines.append("}")
                            repairs_made.append("Added missing catch block")
                        
                        in_try_block = False
                        brace_count = 0
            
            text = '\n'.join(new_lines)
        
        # 3. Add UTF-8 encoding header if missing
        if not text.startswith('[Console]::OutputEncoding'):
            encoding_header = '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8\n$ErrorActionPreference = "Stop"\n\n'
            text = encoding_header + text
            repairs_made.append("Added UTF-8 encoding header")
        
        # 4. Fix common parameter issues
        # Replace -Verbose with -VerboseLogging if used as parameter
        if 'param(' in text and '-Verbose' in text:
            # Only replace in parameter definitions, not in function calls
            param_section = re.search(r'param\s*\((.*?)\)', text, re.DOTALL)
            if param_section and '-Verbose' in param_section.group(1):
                text = text.replace('$Verbose', '$VerboseLogging')
                text = text.replace('[switch]$Verbose', '[switch]$VerboseLogging')
                repairs_made.append("Fixed Verbose parameter conflict")
        
        # Only write if we made changes
        if text != original_text:
            # Create backup
            backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            file_obj.rename(backup_path)
            
            # Write repaired version
            file_obj.write_text(text, encoding="utf-8")
            
            logger.info(f" Repaired {len(repairs_made)} issues in {file_path}")
            for repair in repairs_made:
                logger.info(f"   - {repair}")
            logger.info(f"   - Backup created: {backup_path}")
            return True
        else:
            logger.info(f" No repairs needed for {file_path}")
            return True
            
    except Exception as e:
        logger.error(f" Failed to repair {file_path}: {e}")
        return False

def main():
    """Main function to repair all PowerShell files in EQ12."""
    workspace = pathlib.Path("C:/EQ12")
    
    logger.info(" EQ12 PowerShell Auto-Repair System Starting")
    logger.info(f"Scanning workspace: {workspace}")
    
    # Find all .ps1 files
    ps1_files = list(workspace.glob("*.ps1"))
    ps1_files.extend(workspace.glob("scripts/*.ps1"))
    
    logger.info(f"Found {len(ps1_files)} PowerShell files to check")
    
    repaired_count = 0
    failed_count = 0
    
    for ps1_file in ps1_files:
        if auto_repair_ps1(ps1_file):
            repaired_count += 1
        else:
            failed_count += 1
    
    logger.info(f" Auto-repair complete: {repaired_count} successful, {failed_count} failed")
    
    # Also create the missing weather system stub
    create_weather_stub()

def create_weather_stub():
    """Create weather system stub if it doesn't exist."""
    weather_file = pathlib.Path("C:/EQ12/eq12_enhanced_stadium_weather_system.py")
    
    if weather_file.exists():
        logger.info(" Weather system file already exists")
        return
    
    stub_content = '''#!/usr/bin/env python3
"""
EQ12 Enhanced Stadium Weather System (Stub)
Temporary placeholder until full OpenWeather API integration is complete.
"""

import logging
import argparse
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_weather_analysis():
    """Stub weather analysis function."""
    logger.info(" Stub: Weather intelligence temporarily disabled.")
    return {
        "status": "stub", 
        "impact": 0, 
        "sentiment": 0,
        "timestamp": datetime.now().isoformat(),
        "message": "Weather analysis will be enabled with OpenWeather API key"
    }

def main():
    """Main function for weather system."""
    parser = argparse.ArgumentParser(description="EQ12 Weather System")
    parser.add_argument("--action", default="analyze", help="Action to perform")
    parser.add_argument("--workspace", default="C:\\EQ12", help="Workspace path")
    
    args = parser.parse_args()
    
    logger.info(" EQ12 Weather System (Stub Mode)")
    result = run_weather_analysis()
    logger.info(f"Result: {result}")
    
    return result

if __name__ == "__main__":
    main()
'''
    
    try:
        weather_file.write_text(stub_content, encoding="utf-8")
        logger.info(f" Created weather system stub: {weather_file}")
    except Exception as e:
        logger.error(f" Failed to create weather stub: {e}")

if __name__ == "__main__":
    main()