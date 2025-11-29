# ============================================================
# EQ12 COMMIT EXPERT - Complete Setup Guide
# ============================================================

## 📚 What's Inside This Starter Kit

This starter kit provides **everything you need** to become a commit expert across:
- **Git**: Version control and signed commits
- **VB.NET**: Database transactions with commit/rollback
- **SQL**: Transaction patterns and testing
- **PowerShell**: Automated commit workflows

---

## 📂 Files Included

| File | Purpose | Language |
|------|---------|----------|
| `commit_training.vb` | VB.NET transaction training module | VB.NET |
| `commit_test.sql` | SQL transaction test suite | SQL |
| `eq12_auto_commit.ps1` | PowerShell Git automation | PowerShell |
| `pre-commit-hook.sh` | Git pre-commit validation | Bash |
| `commit_message_template.txt` | Commit message guide | Text |
| `gpg_setup_guide.md` | GPG key generation guide | Markdown |
| `git_init_script.ps1` | Initialize Git repository | PowerShell |
| `README_COMMIT_EXPERT.md` | This file | Markdown |

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Initialize Git Repository (if not already done)

```powershell
cd C:\EQ12_BROKEN_20251122_210342
.\commit_expert_starter_kit\git_init_script.ps1
```

This will:
- ✅ Initialize `.git` repository
- ✅ Create `.gitignore` with security patterns
- ✅ Configure Git user (if not already set)
- ✅ Create initial commit

### Step 2: Set Up GPG Signing (Recommended)

```powershell
# Generate GPG key (follow prompts)
gpg --gen-key

# List your keys
gpg --list-keys

# Copy your key ID (40-character hex string)
# Example: 3AA5C34371567BD2

# Configure Git to use it
git config --global user.signingkey YOUR_KEY_ID
git config --global commit.gpgsign true
```

### Step 3: Install Pre-Commit Hook

```powershell
# Copy hook to Git hooks directory
Copy-Item .\commit_expert_starter_kit\pre-commit-hook.sh .\.git\hooks\pre-commit

# Make executable (if on WSL/Git Bash)
chmod +x .git/hooks/pre-commit
```

### Step 4: Test VB.NET Transaction Training

```powershell
# Compile the VB.NET training module
cd commit_expert_starter_kit
dotnet new console -lang VB -n CommitTraining
Copy-Item commit_training.vb CommitTraining\Program.vb -Force
cd CommitTraining
dotnet build
dotnet run
```

### Step 5: Run SQL Tests

```bash
# Using SQLite
sqlite3 C:\EQ12\data\commit_test.db < commit_test.sql

# Or import into SQL Server Management Studio
```

---

## 📖 Detailed Learning Path

### Module 1: Git Commits (1 hour)

**Goal:** Master Git commit workflow and signed commits

**Exercises:**

1. **Create your first signed commit:**
   ```powershell
   # Stage files
   git add .
   
   # Create signed commit
   git commit -S -m "feat(training): complete commit expert module 1"
   
   # Verify signature
   git log --show-signature -1
   ```

2. **Use the automated commit script:**
   ```powershell
   .\eq12_auto_commit.ps1 -Template "feat" -Scope "git" -Description "automated commit workflow" -Sign
   ```

3. **Test commit rollback:**
   ```powershell
   # Make a commit
   git commit -m "test commit to rollback"
   
   # Undo it (keep changes staged)
   git reset --soft HEAD~1
   
   # Or undo completely
   git reset --hard HEAD~1
   ```

**Key Concepts:**
- ✅ Staging area vs working directory
- ✅ Commit = permanent snapshot
- ✅ Signed commits = authenticity proof
- ✅ Reset = undo commits

---

### Module 2: VB.NET Database Transactions (2 hours)

**Goal:** Master BeginTransaction → Commit → Rollback patterns

**Exercises:**

1. **Run Lesson 1: Basic Transaction**
   - Transfer money between accounts
   - Observe successful COMMIT
   - Trigger ROLLBACK with insufficient funds
   - Review audit log at `C:\EQ12\logs\commit_audit.log`

2. **Run Lesson 2: Advanced Transaction**
   - Process multi-leg bet slip
   - See atomic operations (all or nothing)
   - Test rollback on validation failure

3. **Run Lesson 3: Isolation Levels**
   - Understand READ COMMITTED vs SERIALIZABLE
   - Test concurrent transaction behavior

**Key Concepts:**
- ✅ `BeginTransaction` creates scope
- ✅ `Commit()` makes changes permanent
- ✅ `Rollback()` undoes everything
- ✅ `Using` ensures cleanup
- ✅ Always pair BeginTransaction with Commit/Rollback

**Code Pattern to Memorize:**
```vb
Using transaction = conn.BeginTransaction()
    Try
        ' Do operations here
        transaction.Commit()
    Catch ex As Exception
        transaction.Rollback()
        Throw
    End Try
End Using
```

---

### Module 3: SQL Transactions (1 hour)

**Goal:** Understand SQL-level commit/rollback

**Exercises:**

1. **Run Test 1: Basic COMMIT**
   - Transfer $500 between accounts
   - Observe both accounts updated
   - Query audit log

2. **Run Test 2: ROLLBACK**
   - Attempt transfer with insufficient funds
   - See validation fail
   - Confirm account unchanged

3. **Run Test 3: Multi-Table Atomic Operation**
   - Process order (3 tables affected)
   - All succeed or all rollback

4. **Run Test 4: Savepoint Pattern**
   - Process 2 orders
   - First succeeds, second rolls back
   - First remains committed

**Key Concepts:**
- ✅ `BEGIN TRANSACTION` starts scope
- ✅ `COMMIT` finalizes changes
- ✅ `ROLLBACK` undoes all
- ✅ `SAVEPOINT` allows partial rollback

---

### Module 4: PowerShell Git Automation (1 hour)

**Goal:** Automate commit workflows for EQ12 system

**Exercises:**

1. **Manual Commit with Template:**
   ```powershell
   .\eq12_auto_commit.ps1 `
       -Template "feat" `
       -Scope "automation" `
       -Description "add scheduled task" `
       -Sign `
       -PreCommit
   ```

2. **Auto-Commit After Script:**
   ```powershell
   # Run your script
   python eq12_live_sports_scanner.py
   
   # Auto-commit if successful
   .\eq12_auto_commit.ps1 -Auto -ScriptResult $LASTEXITCODE -Sign -Push
   ```

3. **Dry Run (Test Without Committing):**
   ```powershell
   .\eq12_auto_commit.ps1 `
       -Message "test commit" `
       -DryRun
   ```

**Key Features:**
- ✅ Pre-commit validation (secrets, file sizes, syntax)
- ✅ Semantic commit messages
- ✅ GPG signing integration
- ✅ Auto-push option
- ✅ Audit logging

---

## 🎯 Commit Expert Checklist

### Git Mastery

- [x] Initialize Git repository
- [x] Generate GPG key
- [x] Configure commit signing
- [x] Write semantic commit messages
- [x] Use pre-commit hooks
- [x] Understand reset vs revert
- [x] Manage `.gitignore` for secrets

### VB.NET Transaction Mastery

- [x] Always use `BeginTransaction` for multi-step operations
- [x] Pair every `BeginTransaction` with `Commit` or `Rollback`
- [x] Use `Using` blocks for automatic cleanup
- [x] Validate business logic BEFORE commit
- [x] Log transactions for audit trail
- [x] Test rollback scenarios

### SQL Transaction Mastery

- [x] Use `BEGIN TRANSACTION` for atomic operations
- [x] Always include `COMMIT` or `ROLLBACK`
- [x] Test with bad data to verify rollback works
- [x] Use savepoints for complex workflows
- [x] Choose appropriate isolation level
- [x] Keep transactions short (minimal lock time)

### Automation Mastery

- [x] Auto-commit after successful script execution
- [x] Include exit code in commit message
- [x] Sign automated commits
- [x] Log all commit activity
- [x] Use templates for consistency
- [x] Never commit secrets

---

## 🔧 Configuration Reference

### Git Configuration

```bash
# User identity
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# GPG signing
git config --global user.signingkey YOUR_GPG_KEY_ID
git config --global commit.gpgsign true
git config --global gpg.program "C:\Program Files (x86)\GnuPG\bin\gpg.exe"

# Credential storage
git config --global credential.helper manager

# Default branch
git config --global init.defaultBranch main

# Editor
git config --global core.editor "code --wait"
```

### PowerShell Execution Policy (if needed)

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📝 Commit Message Template

**Semantic Format:**
```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic change)
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(odds): add live betting scanner
fix(db): correct transaction rollback logic
docs(readme): update commit workflow guide
chore(automation): schedule nightly commits
```

---

## 🐛 Troubleshooting

### Problem: "fatal: not a git repository"

**Solution:**
```powershell
git init
git add .
git commit -m "Initial commit"
```

### Problem: GPG signing fails

**Solution:**
```powershell
# Verify GPG is installed
gpg --version

# Check if key exists
gpg --list-keys

# Generate new key if needed
gpg --gen-key

# Configure Git
git config --global user.signingkey YOUR_KEY_ID
```

### Problem: Pre-commit hook not running

**Solution:**
```bash
# Make hook executable (Git Bash/WSL)
chmod +x .git/hooks/pre-commit

# Verify it exists
ls -la .git/hooks/pre-commit
```

### Problem: "Transaction not associated with connection"

**Solution (VB.NET):**
```vb
' Ensure transaction is passed to command
Using cmd As New SqlCommand("...", conn, transaction)
    ' NOT: Using cmd As New SqlCommand("...", conn)
```

---

## 🎓 Advanced Topics

### 1. Nested Transactions (SQL Server)

SQL Server supports nested transactions with `@@TRANCOUNT`:

```sql
BEGIN TRANSACTION  -- @@TRANCOUNT = 1
    BEGIN TRANSACTION  -- @@TRANCOUNT = 2
    COMMIT  -- @@TRANCOUNT = 1
COMMIT  -- @@TRANCOUNT = 0
```

Only the outermost `COMMIT` finalizes changes.

### 2. Distributed Transactions (VB.NET)

For multi-database transactions:

```vb
Imports System.Transactions

Using scope As New TransactionScope()
    ' Operations on Database 1
    Using conn1 As New SqlConnection(connString1)
        ' ...
    End Using
    
    ' Operations on Database 2
    Using conn2 As New SqlConnection(connString2)
        ' ...
    End Using
    
    scope.Complete() ' Commit both
End Using
```

### 3. Git Commit Hooks for CI/CD

Automate testing before commit:

```bash
# .git/hooks/pre-commit
pytest tests/
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

---

## 📚 Additional Resources

### Official Documentation

- [Git Commit Best Practices](https://git-scm.com/docs/git-commit)
- [VB.NET Transactions (Microsoft)](https://learn.microsoft.com/en-us/dotnet/api/system.data.common.dbtransaction)
- [SQL Server Transactions](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transactions-transact-sql)
- [GPG Signing Guide](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits)

### EQ12-Specific

- `AGENTS.md` - Coding standards (requires signed commits)
- `COPILOT_PROMPT.md` - Copilot instructions
- `_do_signed_commit.ps1` - Existing signed commit helper

---

## 🏆 Graduation Criteria

You are a **Commit Expert** when you can:

1. ✅ Explain the difference between `git reset --soft`, `--mixed`, and `--hard`
2. ✅ Write a VB.NET transaction that handles rollback on validation failure
3. ✅ Create a SQL script with savepoints for partial rollback
4. ✅ Automate commits with GPG signing via PowerShell
5. ✅ Debug a transaction isolation level issue
6. ✅ Set up pre-commit hooks that prevent security leaks
7. ✅ Write semantic commit messages without looking at the template

---

## 🚀 Next Steps

After completing this training:

1. **Apply to EQ12 Projects:**
   - Add transaction logging to `eq12_live_sports_scanner.py`
   - Implement auto-commit in nightly Task Scheduler jobs
   - Add GPG signing to all automation scripts

2. **Enhance Workflow:**
   - Create commit message templates for each project
   - Set up GitHub Actions for automated testing
   - Implement database migration scripts with rollback

3. **Share Knowledge:**
   - Document commit patterns in project wikis
   - Review team commits for quality
   - Mentor others on transaction best practices

---

**Version:** 1.0  
**Last Updated:** 2025-11-29  
**Maintained By:** EQ12 System

---

**Need Help?**

- Check `C:\EQ12\logs\commit_audit.log` for commit history
- Review existing production code in `src/props/*.vb` for transaction patterns
- Run scripts with `-Verbose` flag for detailed output

**Happy Committing! 🎉**
