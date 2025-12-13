# EQ12 Universal Repair Assistant

## Overview
Complete automation suite for VS Code troubleshooting, security scanning, and code quality management.

## Quick Start Commands

### Security & Secrets
```bash
# Complete security scan and remediation
python scripts/eq12_gitleaks_guardian.py --action comprehensive

# Quick secret scan only  
python scripts/eq12_gitleaks_guardian.py --action scan
```

### Script Quality
```powershell
# Complete script integrity check (all languages)
.\scripts\eq12_script_integrity_suite.ps1 -Action All -AutoFix

# Python only linting
.\scripts\eq12_script_integrity_suite.ps1 -Action Lint -Language Python
```

### VS Code Issues
```powershell
# Complete VS Code troubleshooting
.\scripts\eq12_vscode_troubleshooter_simple.ps1 -Action Full

# Quick health check
.\scripts\eq12_vscode_troubleshooter_simple.ps1 -Action Quick
```

### One-Click Solutions
Use VS Code Command Palette (Ctrl+Shift+P):
- `Tasks: Run Task` → `EQ12: Emergency Repair Suite` (runs all repairs)
- `Tasks: Run Task` → `EQ12: Quick Health Check` (diagnosis only)

## Expert Copilot Prompts

Copy and paste these into GitHub Copilot Chat for automated repairs:

### 🔐 Security Remediation
```
You are an expert security auditor and remediation AI. Perform a comprehensive security analysis and automatic remediation:

**SECURITY SCAN AND REMEDIATION:**
1. Scan ALL files in the workspace for hardcoded credentials, API keys, passwords, tokens, or secrets
2. Identify patterns: AWS keys (AKIA*), OpenAI keys (sk-*), GitHub tokens (gh*_*), Slack tokens (xox*), etc.
3. For each secret found:
   - Replace with secure environment variable references (os.getenv(), process.env., $env:, Environment...
```

### 🧹 Script Quality
```  
You are an expert multi-language code quality AI. Perform comprehensive script analysis and repair across all languages:

**PYTHON FIXES:**
1. Fix all syntax errors, missing imports, and undefined variables
2. Update deprecated functions to modern alternatives (e.g., datetime.utcnow() → datetime.now(timezone.utc))
3. Add proper type hints and docstrings
4. Apply Black formatting and fix Flake8/Pylint issues
5. Add error handling and input validation
6. Fix security issues flagged by Bandit

**JA...
```

### ⚡ Performance & Threading
```
You are an expert threading and async programming AI. Fix all context access violations and threading issues:

**THREADING AND CONTEXT FIXES:**
1. Fix UI thread violations - use proper Invoke/Dispatcher calls for cross-thread UI access
2. Ensure proper async/await patterns throughout - never mix blocking and async code
3. Add proper object lifetime management and disposal patterns
4. Fix race conditions and add appropriate locking mechanisms
5. Validate Entity Framework context usage - ensure pr...
```

### 🎯 Complete Health Check
```
You are the ultimate code health and repair AI. Perform a comprehensive analysis and fix ALL issues across the entire workspace:

**EXECUTE ALL REPAIR CATEGORIES:**
1. **Security Audit**: Scan for and remediate all hardcoded secrets, implement proper environment variable usage
2. **Code Quality**: Fix linting errors, formatting issues, and code smells across all languages
3. **Threading Safety**: Resolve context access violations, async issues, and resource management problems
4. **Performance**...
```

## File Structure
```
C:\EQ12\
├── scripts/              # Automation scripts
├── logs/                 # Execution logs and reports  
├── configs/              # Configuration files
└── .vscode/tasks.json    # VS Code task definitions
```

## Support
- Logs: Check `C:\EQ12\logs\` for detailed execution reports
- Issues: Review JSON reports for specific problems and solutions
- Configuration: All settings stored in `C:\EQ12\configs\`
