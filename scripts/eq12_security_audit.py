"""
EQ12 SECURITY AUDITOR
Scans the codebase for hardcoded secrets and security risks.
"""
import os
import re

ROOT_DIR = "."
DANGEROUS_PATTERNS = [
    r"API_KEY\s*=\s*['\"]sk-",  # OpenAI Keys
    r"PASSWORD\s*=\s*['\"]",    # Hardcoded passwords
    r"token\s*=\s*['\"]",       # Generic tokens
    r"rm\s+-rf",                # Dangerous commands
]

def scan_codebase():
    print("🛡️  EQ12 Security Audit: Scanning for vulnerabilities...")
    issues_found = 0
    
    for root, dirs, files in os.walk(ROOT_DIR):
        # Skip ignored folders
        if ".git" in dirs: dirs.remove(".git")
        if "node_modules" in dirs: dirs.remove("node_modules")
        if "__pycache__" in dirs: dirs.remove("__pycache__")
        if ".venv" in dirs: dirs.remove(".venv")

        for file in files:
            if file.endswith((".py", ".js", ".ts", ".ps1", ".md", ".json", ".yaml")):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        for pattern in DANGEROUS_PATTERNS:
                            if re.search(pattern, content):
                                print(f"   [⚠️ RISK] Found '{pattern}' in {path}")
                                issues_found += 1
                except Exception as e:
                    print(f"   [Error] Could not read {path}: {e}")

    if issues_found == 0:
        print("✅ No obvious hardcoded secrets found.")
    else:
        print(f"⚠️  Found {issues_found} potential security risks.")

if __name__ == "__main__":
    scan_codebase()
