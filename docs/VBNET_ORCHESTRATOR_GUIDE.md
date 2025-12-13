# EQ12 VB.NET Auto-Scan & Repair Orchestrator - User Guide

## 🎯 **What This Does**

The **VB.NET Orchestrator** is your intelligent automation layer that:

1. **Scans all VB.NET files** in the EQ12 workspace for common issues
2. **Coordinates multi-language repairs** (Python, JavaScript, Markdown, Docker)
3. **Auto-fixes** common VB.NET problems (Unicode quotes, missing options, etc.)
4. **Generates unified audit reports** across entire codebase
5. **Protects background processes** (won't interrupt 20K prompt execution)
6. **Integrates with GitHub Copilot** for deep debugging

---

## 📋 **Quick Start**

### **1. Scan VB.NET Files**
```powershell
.\scripts\EQ12_VBNET_SCAN_ORCHESTRATOR.ps1 -Action scan
```

**What it does**:
- Scans all .vb and .vbproj files
- Checks for common VB.NET issues
- Runs multi-language scans (Python, Markdown, Docker, Security)
- Generates comprehensive audit report

**Output**: `reports/EQ12_Unified_Audit_YYYYMMDD_HHMMSS.md`

---

### **2. Auto-Repair Issues**
```powershell
.\scripts\EQ12_VBNET_SCAN_ORCHESTRATOR.ps1 -Action repair
```

**What it fixes**:
- ✅ Unicode quotes → ASCII quotes (`""` → `""`)
- ✅ Missing `Option Strict On` declarations
- ✅ Missing `Option Explicit On` declarations
- 💾 Creates `.bak` backups before modifying files

**Safe to run**: All changes are auto-backed up

---

### **3. Generate Unified Audit**
```powershell
.\scripts\EQ12_VBNET_SCAN_ORCHESTRATOR.ps1 -Action audit
```

**What it analyzes**:
- VB.NET source files + projects
- Python files (Flake8 linting)
- Markdown files (markdownlint)
- Dockerfiles (Hadolint)
- Security (GitLeaks secret scan)

**Output**: Comprehensive markdown report with all findings

---

### **4. Trigger Copilot Deep Scan**
```powershell
.\scripts\EQ12_VBNET_SCAN_ORCHESTRATOR.ps1 -Action copilot
```

**What it does**:
- Generates detailed Copilot prompt
- Opens prompt in default editor
- Provides exact instructions for GitHub Copilot to:
  - Fix all VB.NET issues
  - Fix Python/JS/Markdown issues
  - Run security scans
  - Generate unified report

---

## 🔍 **VB.NET Issues Detected**

### **1. Missing Option Strict/Explicit**
```vb
' BEFORE
Public Class MyClass
    ' Missing option declarations
End Class

' AFTER (Auto-Fixed)
Option Strict On
Option Explicit On
Public Class MyClass
End Class
```

**Why it matters**: Prevents implicit type conversions and undeclared variables

---

### **2. Unicode Quote Characters**
```vb
' BEFORE
Dim message As String = "Hello World"  ' Unicode quotes

' AFTER (Auto-Fixed)
Dim message As String = "Hello World"  ' ASCII quotes
```

**Why it matters**: Prevents compilation errors and encoding issues

---

### **3. Loop Control Variable Reassignment**
```vb
' DETECTED (Manual Fix Required)
For i As Integer = 0 To 10
    i = i + 1  ' ❌ Reassigning loop variable
Next

' FIXED
For i As Integer = 0 To 10
    Dim temp As Integer = i + 1  ' ✅ Use separate variable
Next
```

**Why it matters**: Causes unpredictable loop behavior

---

### **4. Uninitialized Variables**
```vb
' DETECTED
Dim count As Integer  ' Not initialized

' RECOMMENDED
Dim count As Integer = 0  ' Initialized with default
```

**Why it matters**: Prevents null reference exceptions

---

### **5. Technical Debt Markers**
```vb
' DETECTED
' TODO: Optimize this algorithm
' FIXME: Handle edge case
```

**Action**: Review and address or document properly

---

## 🌐 **Multi-Language Coordination**

The orchestrator automatically runs:

### **Python (Flake8)**
- Checks: Unused variables (F841), line length (E501), import order
- Output: `logs/python_scan_YYYYMMDD_HHMMSS.log`

### **Markdown (markdownlint)**
- Checks: Heading hierarchy, inline code, list formatting
- Output: `logs/markdown_scan_YYYYMMDD_HHMMSS.log`

### **Docker (Hadolint)**
- Checks: Layer ordering, health checks, image optimization
- Output: `logs/docker_scan_YYYYMMDD_HHMMSS.log`

### **Security (GitLeaks)**
- Checks: Hardcoded credentials, API keys, tokens
- Output: `logs/gitleaks_scan_YYYYMMDD_HHMMSS.json`

---

## 🛡️ **Background Process Protection**

**Automatic Detection**: The orchestrator checks for:
- `eq12_prompt_executor.py` (20K prompt runner)
- `EQ12_PROMPT_RUNNER.ps1` (PowerShell wrapper)

**Low-Impact Mode**: If detected, orchestrator:
- ✅ Reduces resource usage
- ✅ Avoids disk-intensive operations
- ✅ Delays heavy I/O
- ✅ Warns before destructive actions

**Manual Override**:
```powershell
.\EQ12_VBNET_SCAN_ORCHESTRATOR.ps1 -Action scan -SkipBackgroundCheck
```
⚠️ Use with caution - may impact background performance

---

## 📊 **Example Audit Report**

```markdown
# EQ12 Unified System Audit Report

**Generated**: 2025-11-27 15:32:45 UTC

## Executive Summary

### VB.NET Analysis
- Source Files Scanned: 3,789
- Project Files Found: 63
- Issues Detected: 147
- Auto-Fixable Issues: 89

### Multi-Language Scans
- Python: ✅ PASS
- Markdown: ⚠️ ISSUES FOUND (12 files)
- Docker: ✅ PASS
- Security: ✅ NO LEAKS

## VB.NET Detailed Findings

### Issue Breakdown by Type

#### AmbiguousStringLiteral (45)
**Severity**: Warning
**Fix**: Replace with standard " or ' characters

#### MissingOptionStrict (32)
**Severity**: Warning
**Fix**: Add 'Option Strict On' at top of file

#### LoopControlReassignment (8)
**Severity**: Error
**Fix**: Use separate variable inside loop body

...
```

---

## 🎯 **Integration with EQ12 Stack**

### **VB.NET Projects Scanned**
1. `visual_studio_projects\EQ12SportsBettingTerminal`
   - 9+ modules (BankrollEngine, ArbitrageEngine, ApiHandlers, etc.)
   - Major betting automation system
   
2. `src\props`
   - 8 modules (OddsIngestor, KellyCalculator, ParlayBuilder, etc.)
   - NBA props betting system (80% complete)
   
3. `vbnet_projects\EQ12WindowsManager`
   - Windows system automation
   
4. `vbnet_projects\EQ12.DockerManager`
   - Docker container orchestration

---

## 🔧 **Advanced Usage**

### **Target Specific Project**
```powershell
.\EQ12_VBNET_SCAN_ORCHESTRATOR.ps1 -Action scan -TargetPath "visual_studio_projects\EQ12SportsBettingTerminal"
```

### **Repair Specific Project**
```powershell
.\EQ12_VBNET_SCAN_ORCHESTRATOR.ps1 -Action repair -TargetPath "src\props"
```

### **Schedule Automated Scans**
```powershell
# Daily scan at 2 AM
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\EQ12_BROKEN_20251122_210342\scripts\EQ12_VBNET_SCAN_ORCHESTRATOR.ps1 -Action audit"
Register-ScheduledTask -TaskName "EQ12_Daily_Audit" -Trigger $trigger -Action $action
```

---

## 📚 **Recommended GitHub Repositories**

The orchestrator suggests these repos for enhanced functionality:

### **VB.NET / .NET**
- **Roslyn**: https://github.com/dotnet/roslyn (Already integrated)
- **StyleCop**: https://github.com/StyleCop/StyleCop
- **SonarAnalyzer**: https://github.com/SonarSource/sonar-dotnet

### **Python**
- **Ruff**: https://github.com/astral-sh/ruff (Fast linter + formatter)
- **Black**: https://github.com/psf/black (Opinionated formatter)
- **Flake8**: https://github.com/PyCQA/flake8

### **Security**
- **GitLeaks**: https://github.com/zricethezav/gitleaks (Secrets scanner)
- **TruffleHog**: https://github.com/trufflesecurity/trufflehog
- **Bandit**: https://github.com/PyCQA/bandit (Python security linter)

### **Docker**
- **Hadolint**: https://github.com/hadolint/hadolint (Dockerfile linter)
- **Dive**: https://github.com/wagoodman/dive (Image layer analysis)
- **Trivy**: https://github.com/aquasecurity/trivy (Vulnerability scanner)

### **AI/ML**
- **Transformers**: https://github.com/huggingface/transformers
- **LangChain**: https://github.com/langchain-ai/langchain
- **AutoGPT**: https://github.com/Significant-Gravitas/AutoGPT

---

## 🚨 **Troubleshooting**

### **Issue**: Python scan skipped
**Cause**: Flake8 not installed
**Fix**: `pip install flake8`

---

### **Issue**: Markdown scan skipped
**Cause**: markdownlint not installed
**Fix**: `npm install -g markdownlint-cli`

---

### **Issue**: Docker scan skipped
**Cause**: Hadolint not installed
**Fix**: Download from https://github.com/hadolint/hadolint/releases

---

### **Issue**: Security scan skipped
**Cause**: GitLeaks not installed
**Fix**: Download from https://github.com/zricethezav/gitleaks/releases

---

### **Issue**: "Background processes detected"
**Expected**: Orchestrator enters low-impact mode
**Action**: This is normal when 20K prompts are running
**Override**: Use `-SkipBackgroundCheck` (not recommended)

---

## ✅ **Success Criteria**

After running the orchestrator, you should have:

1. ✅ **Comprehensive audit report** (unified findings)
2. ✅ **Auto-fixed VB.NET issues** (Unicode quotes, missing options)
3. ✅ **Multi-language scan logs** (Python, Markdown, Docker, Security)
4. ✅ **Backups of modified files** (*.bak)
5. ✅ **Actionable recommendations** (what to fix manually)
6. ✅ **GitHub repo suggestions** (tools to install)

---

## 🎯 **Next Steps**

### **After Scan**
1. Review audit report: `code reports\EQ12_Unified_Audit_*.md`
2. Run auto-repair: `.\EQ12_VBNET_SCAN_ORCHESTRATOR.ps1 -Action repair`
3. Address manual fixes (loop control, TODO markers)

### **After Repair**
1. Test VB.NET projects: `dotnet build` or `msbuild`
2. Commit changes: `git add .` → `git commit -m "chore: auto-fix VB.NET issues"`
3. Re-run scan to verify: `.\EQ12_VBNET_SCAN_ORCHESTRATOR.ps1 -Action scan`

### **After Audit**
1. Install missing tools (flake8, markdownlint, hadolint, gitleaks)
2. Schedule automated scans (daily/weekly)
3. Integrate with CI/CD pipeline (GitHub Actions)

---

## 🔄 **Integration with Existing Workflow**

### **Phase 1** (Current)
- ✅ 20K prompts running (169/20,000, ~54 hours)
- ✅ VB.NET orchestrator ready (non-disruptive)

### **Phase 2** (After Prompts)
- Run full audit
- Auto-repair all fixable issues
- Address manual fixes
- Complete Task #18 (GitHub/HuggingFace/OpenRouter integration)

### **Phase 3** (Production)
- Schedule daily scans
- Integrate with CI/CD
- Build VB.NET Master Control Panel (uses orchestrator as backend)

---

**Status**: Production-Ready
**Priority**: Run after 20K prompts complete
**ROI**: High (automated code quality enforcement)
**Created**: 2025-11-27
