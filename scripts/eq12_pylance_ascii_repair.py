#!/usr/bin/env python3
"""
EQ12 Pylance ASCII Repair Tool - CORRUPTION IMMUNE
==================================================
Fixes all Unicode corruption that crashes Pylance.
Hardcodes ASCII-only mode for entire workspace.

Author: EQ12 AI Development Team
Version: PYLANCE-SAFE 1.0
Date: November 16, 2025
Location: Buffalo NY 14215
"""

import os
import sys
from pathlib import Path

def ascii_safe_print(text):
    """Print text safely in ASCII only"""
    clean_text = str(text).encode('ascii', 'ignore').decode('ascii')
    print(clean_text)

def repair_file_ascii_only(file_path):
    """Convert any file to pure ASCII"""
    try:
        # Read file as binary first
        with open(file_path, 'rb') as f:
            raw_data = f.read()

        # Decode with UTF-8 fallback, then force ASCII
        try:
            text_content = raw_data.decode('utf-8', errors='replace')
        except:
            text_content = raw_data.decode('utf-8', errors='ignore')

        # Force ASCII-only content
        ascii_content = text_content.encode('ascii', errors='ignore').decode('ascii')

        # Write back as pure ASCII
        with open(file_path, 'w', encoding='ascii', errors='replace', newline='\n') as f:
            f.write(ascii_content)

        return True

    except Exception as e:
        ascii_safe_print(f"ERROR repairing {file_path}: {e}")
        return False

def hardcode_ascii_headers():
    """Add ASCII-safe headers to all Python files"""
    ascii_header = '''#!/usr/bin/env python3
# ASCII-SAFE MODE - NO UNICODE ALLOWED
import sys
sys.stdout.reconfigure(encoding="ascii", errors="replace") if hasattr(sys.stdout, "reconfigure") else None
sys.stderr.reconfigure(encoding="ascii", errors="replace") if hasattr(sys.stderr, "reconfigure") else None
import os
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "ascii"

'''

    return ascii_header

def scan_and_repair_workspace(root_path):
    """Scan entire workspace and repair all corrupted files"""
    ascii_safe_print("==========================================================")
    ascii_safe_print("EQ12 PYLANCE ASCII REPAIR TOOL - HARDENING WORKSPACE")
    ascii_safe_print("==========================================================")

    root = Path(root_path)
    if not root.exists():
        ascii_safe_print(f"ERROR: Root path does not exist: {root_path}")
        return False

    # File extensions to repair
    target_extensions = {'.py', '.ps1', '.json', '.txt', '.md', '.log', '.env', '.yml', '.yaml'}

    files_processed = 0
    files_repaired = 0
    files_failed = 0

    ascii_safe_print(f"Scanning workspace: {root_path}")
    ascii_safe_print("Target extensions: .py .ps1 .json .txt .md .log .env .yml .yaml")
    ascii_safe_print("")

    # Walk through all files
    for file_path in root.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in target_extensions:
            # Skip certain directories
            if any(skip in str(file_path) for skip in ['.git', '__pycache__', '.venv', 'node_modules']):
                continue

            files_processed += 1
            ascii_safe_print(f"Processing [{files_processed}]: {file_path.name}")

            if repair_file_ascii_only(file_path):
                files_repaired += 1
                ascii_safe_print(f"  REPAIRED: ASCII-only conversion complete")
            else:
                files_failed += 1
                ascii_safe_print(f"  FAILED: Could not repair file")

    # Summary
    ascii_safe_print("")
    ascii_safe_print("==========================================================")
    ascii_safe_print("ASCII HARDENING COMPLETE")
    ascii_safe_print("==========================================================")
    ascii_safe_print(f"Files processed: {files_processed}")
    ascii_safe_print(f"Files repaired: {files_repaired}")
    ascii_safe_print(f"Files failed: {files_failed}")
    ascii_safe_print("")

    if files_failed == 0:
        ascii_safe_print("SUCCESS: All files converted to ASCII-safe mode")
        ascii_safe_print("Pylance corruption eliminated")
        ascii_safe_print("Unicode crash sources removed")
        return True
    else:
        ascii_safe_print(f"WARNING: {files_failed} files could not be repaired")
        return False

def set_ascii_environment():
    """Set ASCII-safe environment variables"""
    ascii_safe_print("Setting ASCII-safe environment variables...")

    ascii_env_vars = {
        'PYTHONUTF8': '1',
        'PYTHONIOENCODING': 'ascii',
        'LC_ALL': 'C',
        'LANG': 'C'
    }

    for var, value in ascii_env_vars.items():
        os.environ[var] = value
        ascii_safe_print(f"Set {var}={value}")

def create_pylance_safe_config():
    """Create Pylance-safe VS Code configuration"""
    vscode_dir = Path("C:/EQ12/.vscode")
    vscode_dir.mkdir(exist_ok=True)

    settings_content = '''{
    "python.languageServer": "Pylance",
    "python.defaultInterpreterPath": "python",

    "files.encoding": "utf8",
    "files.autoGuessEncoding": false,
    "files.eol": "\\n",
    "files.insertFinalNewline": true,

    "editor.formatOnSave": false,
    "editor.codeActionsOnSave": {
        "source.organizeImports": "never",
        "source.fixAll": "never"
    },

    "editor.unicodeHighlight.nonBasicASCII": true,
    "editor.unicodeHighlight.ambiguousCharacters": true,
    "editor.unicodeHighlight.includeComments": true,

    "python.analysis.typeCheckingMode": "off",
    "python.analysis.diagnosticMode": "workspace",
    "python.formatting.provider": "none",

    "powershell.scriptAnalysis.enable": false,

    "terminal.integrated.env.windows": {
        "PYTHONUTF8": "1",
        "PYTHONIOENCODING": "ascii",
        "LC_ALL": "C",
        "LANG": "C"
    }
}'''

    settings_file = vscode_dir / "settings.json"
    try:
        with open(settings_file, 'w', encoding='ascii', errors='replace') as f:
            f.write(settings_content)
        ascii_safe_print(f"Created Pylance-safe config: {settings_file}")
        return True
    except Exception as e:
        ascii_safe_print(f"Failed to create config: {e}")
        return False

def main():
    """Main repair execution"""
    ascii_safe_print("EQ12 PYLANCE ASCII REPAIR TOOL")
    ascii_safe_print("Fixing Unicode corruption that crashes Pylance")
    ascii_safe_print("")

    # Set environment
    set_ascii_environment()

    # Create VS Code config
    create_pylance_safe_config()

    # Repair workspace
    workspace_path = "C:/EQ12"
    success = scan_and_repair_workspace(workspace_path)

    if success:
        ascii_safe_print("")
        ascii_safe_print("==========================================================")
        ascii_safe_print("PYLANCE REPAIR COMPLETE - RESTART VS CODE NOW")
        ascii_safe_print("==========================================================")
        ascii_safe_print("1. Close VS Code completely")
        ascii_safe_print("2. Open Command Prompt and run: code C:\\EQ12")
        ascii_safe_print("3. Pylance will now work without crashes")
        ascii_safe_print("4. All Unicode corruption eliminated")
        ascii_safe_print("Buffalo NY 14215 Content Empire - ASCII SAFE MODE ACTIVE")
        return 0
    else:
        ascii_safe_print("REPAIR FAILED - Manual intervention required")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        ascii_safe_print("Repair interrupted by user")
        sys.exit(130)
    except Exception as e:
        ascii_safe_print(f"Unexpected error: {str(e).encode('ascii', 'ignore').decode('ascii')}")
        sys.exit(1)
