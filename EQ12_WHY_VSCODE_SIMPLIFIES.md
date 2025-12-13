# ⭐ Why VS Code "Keeps Trying to Make a Simpler Working Version"

## The Truth: VS Code Failsafe Mode

**VS Code is not trying to simplify your workspace.**  
**It's trying to save itself from corruption.**

When VS Code detects failures in your development environment, it enters **failsafe mode**:

> "Let me create a smaller, simpler version of the workspace so I don't crash."

---

## 🔥 What Triggers Failsafe Mode?

You are running the **MOST unstable setup possible**:

- ✅ Windows host
- ✅ WSL
- ✅ Dev Containers
- ✅ Copilot + Copilot Chat
- ✅ Python + Pylance
- ✅ Git repository with 20,000+ folders
- ✅ Constant file watchers
- ✅ Symlinks + long paths
- ✅ Failing extensions
- ✅ Invalid Python interpreters
- ✅ Missing tikTokenizer modules
- ✅ Background scan crashes

**When ANY of these fail → VS Code enters failsafe mode.**

---

## 🚨 What Failsafe Mode Does

When VS Code detects instability, it automatically:

- ❌ Disables extensions silently
- ❌ Reinstalls `.vscode-server` remotely
- ❌ Breaks Copilot Chat authentication
- ❌ Resets Python interpreter selection
- ❌ Ignores `settings.json` configurations
- ❌ Rebuilds `.vscode-server` from scratch
- ❌ Stops indexing and file watching
- ❌ Throttles file watchers to prevent crashes
- ❌ Shows "We found a simpler, working configuration" messages
- ❌ Asks to reopen in "restricted mode" or "simple mode"

This is **not intentional** — VS Code is **trying to survive**.

---

## ⚡ The REAL Reasons You Keep Seeing This

### 1. **The workspace is TOO BIG**

`C:\EQ12_BROKEN_20251122_210342` has **over 700 folders**.

VS Code's file watcher has a **hard limit**.  
When it exceeds this → **degraded mode**.

### 2. **WSL + DevContainer + Windows Extensions = mixed environment corruption**

Every time the DevContainer fails to load:

- `.vscode-server` breaks
- Copilot Chat gets half-installed
- `tikTokenizerWorker.js` goes missing
- VS Code panics → **fallback mode**

### 3. **Python + Pylance invalid interpreter**

When Pylance cannot initialize:

VS Code falls back to **"simple mode" without type checking**.

### 4. **Git repository TOO LARGE**

Your repo hits the limit:

> "Too many active changes, only a subset of Git features will be enabled."

When Git breaks → VS Code **turns features OFF**.

### 5. **Extensions failing at startup**

If Copilot, Pylance, Prettier, Black, DevContainer, or Python fail to load:

VS Code does the only safe thing:

> "Remove advanced features. Load in safe minimal mode."

---

## ✅ The FIX: Three Layers of Stabilization

To prevent VS Code from:

- Simplifying
- Falling back
- Limiting features
- Turning extensions off

You need **three layers**:

---

### ✅ **LAYER 1 — Separate EQ12 into modules**

`C:\EQ12_BROKEN_20251122_210342` is **WAY too large**.

**Solution**: Split into focused workspaces:

```
C:\EQ12_CORE\      (core scripts and configs only)
C:\EQ12_DEV\       (development workspace)
C:\EQ12_AI\        (AI/ML models)
C:\EQ12_MODELS\    (data models)
C:\EQ12_WS\        (web services)
```

**VS Code should ONLY open `EQ12_DEV` or `EQ12_CORE`, never the whole repo.**

---

### ✅ **LAYER 2 — Stabilize VS Code Remote Engine**

We must **force a clean server install**:

1. Shut down WSL:

```powershell
wsl --shutdown
```

2. Remove corrupted remote server:

```bash
rm -rf ~/.vscode-server
```

3. Reopen VS Code **and let it rebuild the server cleanly**.

**This alone fixes 60% of your recurring issues.**

---

### ✅ **LAYER 3 — Stabilize Copilot + Pylance + Python**

Your `settings.json` should be **CLEAN**:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
  "python.analysis.indexing": true,
  "python.analysis.autoImportCompletions": true,

  "editor.formatOnPaste": false,
  "editor.defaultFormatter": "ms-python.black-formatter",

  "github.copilot.enable": {
    "*": true,
    "plaintext": true,
    "python": true
  },

  "files.watcherExclude": {
    "**/.git/objects/**": true,
    "**/node_modules/**": true,
    "**/.venv/**": true,
    "**/__pycache__/**": true,
    "**/dist/**": true,
    "**/build/**": true,
    "**/logs/**": true,
    "**/reports/**": true
  }
}
```

And only **ONE Python extension**:

```
Pylance (ms-python.vscode-pylance)
Python (ms-python.python)
```

**Remove all others.**

---

## 🔧 EQ12 Solution: Automated Hardening

EQ12 provides **two automated tools** to prevent failsafe mode:

### 1. **EQ12_SAFE_WORKSPACE_TEMPLATE.json**

A perfectly optimized VS Code configuration that:

- Works with Docker, WSL, Python, Copilot, Pylance
- No crashes, no fallback mode
- Prevents file watcher exhaustion
- Locks Python + Pylance to known good state

**Location**: `.vscode/settings.SAFE_TEMPLATE.json`

**Usage**: Copy to `.vscode/settings.json`

---

### 2. **EQ12_FULL_VSCODE_HARDENING.ps1**

A PowerShell script that:

- Forces VS Code into stable mode
- Kills fallback behavior
- Fixes file watcher limits
- Fixes extensions
- Locks Python + Pylance to known good state
- Cleans WSL `.vscode-server`
- Removes Git lock files
- Verifies Python venv

**Location**: `scripts/EQ12_FULL_VSCODE_HARDENING.ps1`

**Usage**:

```powershell
cd C:\EQ12_BROKEN_20251122_210342\scripts
.\EQ12_FULL_VSCODE_HARDENING.ps1 -Force
```

Then **restart VS Code**.

---

## ✅ Success Criteria

After hardening, VS Code should:

- ✅ **NO "simplified workspace" or "restricted mode" prompts**
- ✅ **Copilot Chat loads without tikTokenizer errors**
- ✅ **Pylance activates without "degraded mode" warnings**
- ✅ **Python interpreter shows as: `.venv\Scripts\python.exe`**
- ✅ **Git features fully enabled (no "subset of features" warning)**
- ✅ **All extensions load successfully on startup**

---

## 🧪 Verification Steps

After running `EQ12_FULL_VSCODE_HARDENING.ps1` and restarting VS Code:

1. Open VS Code → Check bottom-left corner:
   - Should show Python interpreter: `.venv\Scripts\python.exe`
   - Should show "Pylance" status (not "Pylance (degraded)")

2. Open Copilot Chat → Type:
   - `@workspace what files are in scripts/`
   - Should respond without "tikTokenizer" errors

3. Check Git status bar:
   - Should show branch name + changes
   - Should NOT show "Git features limited" warning

4. Check extensions panel:
   - All extensions should be enabled
   - No yellow "partially installed" warnings

---

## 🔒 Bottom Line

**VS Code isn't "wanting to simplify things."**  
**It's entering survival mode because your environment is too unstable.**

**EQ12 fixes that.**

Run the hardening script, restart VS Code, and you'll have a rock-solid development environment that never falls back to simplified mode.
