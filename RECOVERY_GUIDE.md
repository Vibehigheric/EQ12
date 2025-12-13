# EQ12 Workspace Recovery - Quick Start Guide

## 🚨 CRITICAL: Your Workspace Has THREE Fatal Issues

1. **Pylance Indexing Death Loop** - 9,789 files indexed (limit: 2,000)
2. **VS Code Remote Freezing** - `.bashrc` contains interactive prompts
3. **Python Interpreter Invalid** - Multiple conflicting virtual environments

---

## ✅ COMPLETE FIX (Automated)

Run this ONE command:

```bash
bash /workspaces/EQ12/eq12_master_fix.sh
```

This executes all repairs in the correct order:
- ✅ Fixes WSL `.bashrc` (stops freezing)
- ✅ Purges corrupted VS Code server files
- ✅ Cleans duplicate virtual environments
- ✅ Rebuilds Python `.venv`
- ✅ Repairs Pylance configuration
- ✅ Validates prompt folders
- ✅ Cleans Python cache

---

## 🔧 MANUAL FIX (Step-by-Step)

### Step 1: Fix WSL .bashrc
```bash
bash /workspaces/EQ12/scripts/fix_wsl_bashrc.sh
```

### Step 2: Clean VS Code Remote
```bash
bash /workspaces/EQ12/scripts/cleanup_vscode_remote.sh
```

### Step 3: Restore Workspace
```bash
bash /workspaces/EQ12/eq12_workspace_sanity_restore.sh
```

### Step 4: Repair Prompt Folders
```bash
bash /workspaces/EQ12/scripts/eq12_prompt_repair.sh
```

---

## 📋 POST-FIX STEPS

After running the fix scripts:

1. **Exit WSL completely**
   ```bash
   exit
   ```

2. **Shutdown WSL (from Windows PowerShell)**
   ```powershell
   wsl --shutdown
   ```

3. **Restart VS Code**
   - Close ALL VS Code windows
   - Reopen ONLY: `/workspaces/EQ12`

4. **Select Python Interpreter**
   - Press: `Ctrl+Shift+P`
   - Type: `Python: Select Interpreter`
   - Choose: `/workspaces/EQ12/.venv/bin/python`

5. **Verify Pylance**
   - Open any `.py` file
   - Check status bar shows Python version
   - Test autocomplete (type `import ` and wait)

---

## 🎯 VERIFICATION CHECKLIST

After recovery, verify:

- [ ] No "userEnvProbe taking longer than 10 seconds" error
- [ ] VS Code Remote connects instantly
- [ ] Pylance shows correct Python version in status bar
- [ ] Autocomplete works in `.py` files
- [ ] No "JavaScript heap out of memory" errors
- [ ] Only ONE `.venv` exists at `/workspaces/EQ12/.venv`
- [ ] `pyrightconfig.json` exists and excludes logs/backups
- [ ] `.vscode/settings.json` has correct interpreter path

---

## 📊 FILES CREATED/MODIFIED

### Configuration Files
- `/workspaces/EQ12/pyrightconfig.json` - Pylance exclusions
- `/workspaces/EQ12/.vscode/settings.json` - Updated Python paths
- `~/.bashrc` - Safe, non-interactive version
- `~/.profile` - Safe shell profile

### Repair Scripts
- `/workspaces/EQ12/eq12_master_fix.sh` - Master recovery script
- `/workspaces/EQ12/scripts/fix_wsl_bashrc.sh` - WSL shell fix
- `/workspaces/EQ12/scripts/cleanup_vscode_remote.sh` - VS Code cleanup
- `/workspaces/EQ12/scripts/eq12_prompt_repair.sh` - Prompt folder repair

### DevContainer Config
- `/workspaces/EQ12/.devcontainer/devcontainer.json` - Container config
- `/workspaces/EQ12/.devcontainer/Dockerfile` - Container image
- `/workspaces/EQ12/.devcontainer/post-create.sh` - Setup script

### Documentation
- `/workspaces/EQ12/prompts/copilot_master_system_analyzer.md` - System audit prompt

---

## 🚀 OPTIONAL: Use DevContainer (Maximum Stability)

For a completely isolated, reproducible environment:

1. **Install Docker Desktop** (if not installed)

2. **Reopen in Container**
   - Press: `Ctrl+Shift+P`
   - Type: `Dev Containers: Reopen in Container`
   - Wait for container to build (~5-10 minutes first time)

3. **Benefits**
   - ✅ No WSL conflicts
   - ✅ Consistent environment
   - ✅ Isolated from host issues
   - ✅ Reproducible across machines
   - ✅ Easy to reset (rebuild container)

---

## 🆘 TROUBLESHOOTING

### Issue: "Python interpreter invalid" persists
```bash
# Delete ALL venvs and recreate
rm -rf /workspaces/EQ12/.venv*
rm -rf /workspaces/EQ12/envs
rm -rf /workspaces/EQ12/scripts/.venv
python3.12 -m venv /workspaces/EQ12/.venv
source /workspaces/EQ12/.venv/bin/activate
pip install -r /workspaces/EQ12/requirements.txt
```

### Issue: Pylance still indexing too many files
```bash
# Verify pyrightconfig.json exists
cat /workspaces/EQ12/pyrightconfig.json

# Reload VS Code window
# Ctrl+Shift+P → Developer: Reload Window
```

### Issue: VS Code Remote still freezing
```bash
# Check for interactive commands in .bashrc
grep -E "(read -p|select|menu)" ~/.bashrc

# If found, run the fix again
bash /workspaces/EQ12/scripts/fix_wsl_bashrc.sh
```

### Issue: Extensions not working
```bash
# Reinstall VS Code server
rm -rf ~/.vscode-server
# Then reconnect to WSL in VS Code
```

---

## 📞 SUPPORT

For additional help:
- Review: `/workspaces/EQ12/AGENTS.md`
- Check logs: `/workspaces/EQ12/logs/`
- Run system analyzer: Use Copilot prompt at `/workspaces/EQ12/prompts/copilot_master_system_analyzer.md`

---

## ⚡ QUICK COMMANDS

```bash
# Run complete fix
bash /workspaces/EQ12/eq12_master_fix.sh

# Check Python environment
source /workspaces/EQ12/.venv/bin/activate && python --version

# Verify file count (should be <2000)
find /workspaces/EQ12 -name "*.py" | wc -l

# Clean Python cache
find /workspaces/EQ12 -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Restart Pylance
# Ctrl+Shift+P → Developer: Reload Window
```

---

**Last Updated**: 2025-11-22
**Status**: ✅ All scripts tested and validated
**Safe to Run**: Yes (all operations are idempotent)
