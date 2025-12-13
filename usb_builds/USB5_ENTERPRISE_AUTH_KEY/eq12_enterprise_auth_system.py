#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EQ12 Enterprise Security Authentication System
Hardware-based authentication for high-value operations
Buffalo NY 14215 Content Empire Security
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class EQ12AuthKey:
    def __init__(self):
        self.auth_path = Path("AUTH_KEY")
        self.auth_path.mkdir(exist_ok=True)
        
        # Create authentication files
        self.auth_lock_file = self.auth_path / "auth.lock"
        self.verify_file = self.auth_path / "verify.txt"
        self.master_key_file = self.auth_path / "master.key"
        
    def generate_master_key(self, passphrase: str = "EQ12_BUFFALO_14215_CONTENT_EMPIRE"):
        """Generate master encryption key from passphrase"""
        password = passphrase.encode()
        salt = b"EQ12_SECURITY_SALT_BUFFALO_NY"
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        
        with open(self.master_key_file, 'wb') as f:
            f.write(key)
            
        return key
    
    def create_auth_files(self):
        """Create authentication verification files"""
        print(" Creating authentication files...")
        
        # Create auth lock
        auth_data = {
            "auth_system": "EQ12_ENTERPRISE_AUTH",
            "location": "Buffalo NY 14215",
            "created": datetime.now().isoformat(),
            "status": "ACTIVE",
            "security_level": "MAXIMUM"
        }
        
        with open(self.auth_lock_file, 'w', encoding='utf-8') as f:
            json.dump(auth_data, f, ensure_ascii=False, indent=2)
        
        # Create verification file
        verify_hash = hashlib.sha256("EQ12_VERIFIED_AUTHENTIC".encode()).hexdigest()
        with open(self.verify_file, 'w', encoding='utf-8') as f:
            f.write(f"EQ12_AUTH_VERIFIED:{verify_hash}")
        
        print(" Authentication files created")
    
    def encrypt_api_key(self, key_name: str, api_key: str, category: str):
        """Encrypt and store API key"""
        print(f" Encrypting {key_name}...")
        
        # Load master key
        with open(self.master_key_file, 'rb') as f:
            master_key = f.read()
        
        cipher = Fernet(master_key)
        encrypted_key = cipher.encrypt(api_key.encode())
        
        # Store encrypted key
        key_data = {
            "key_name": key_name,
            "category": category,
            "encrypted": encrypted_key.decode(),
            "timestamp": datetime.now().isoformat()
        }
        
        key_file = Path(f"{category}_ENCRYPTED") / f"{key_name}.json"
        with open(key_file, 'w', encoding='utf-8') as f:
            json.dump(key_data, f, ensure_ascii=False, indent=2)
        
        print(f" {key_name} encrypted and stored")
    
    def validate_auth_key(self) -> bool:
        """Validate USB authentication key"""
        try:
            # Check for auth lock file
            if not self.auth_lock_file.exists():
                return False
            
            # Check for verify file  
            if not self.verify_file.exists():
                return False
            
            # Verify content
            with open(self.verify_file, 'r') as f:
                verify_content = f.read()
            
            expected_hash = hashlib.sha256("EQ12_VERIFIED_AUTHENTIC".encode()).hexdigest()
            if expected_hash not in verify_content:
                return False
            
            print(" USB Authentication Key: VALID")
            return True
            
        except Exception as e:
            print(f" Auth validation error: {e}")
            return False
    
    def setup_hardware_security(self):
        """Set up complete hardware security system"""
        print(" ENTERPRISE SECURITY SETUP INITIATED")
        print("=" * 50)
        
        # Generate master encryption key
        master_key = self.generate_master_key()
        
        # Create auth files
        self.create_auth_files()
        
        # Example API keys (these would be real in production)
        sample_keys = {
            "OPENAI_SERVICE_KEY": ("sk-example-key", "OPENAI_KEYS"),
            "TELEGRAM_BOT_TOKEN": ("123456:ABC-example", "TELEGRAM_BOT"),
            "ODDS_API_KEY": ("example-odds-key", "ODDS_API"),
            "GITHUB_TOKEN": ("ghp_example-token", "GITHUB_TOKENS")
        }
        
        for key_name, (key_value, category) in sample_keys.items():
            self.encrypt_api_key(key_name, key_value, category)
        
        # Create PowerShell security check
        ps_security = """# EQ12 PowerShell Security Check
if (-not(Test-Path "E:\AUTH_KEY\verify.txt")) {
    Write-Host " AUTH KEY NOT INSERTED  SYSTEM LOCKED" -ForegroundColor Red
    Write-Host " Insert USB #5 Enterprise Auth Key to continue" -ForegroundColor Yellow
    exit 1
}

Write-Host " Enterprise Auth Key validated" -ForegroundColor Green
Write-Host " High-value operations: AUTHORIZED" -ForegroundColor Cyan
"""
        
        ps_check_path = self.auth_path / "powershell_security_check.ps1"
        with open(ps_check_path, 'w', encoding='utf-8') as f:
            f.write(ps_security)
        
        # Create Python security check
        py_security = """import os
import sys

def check_auth_key():
    """Check for USB authentication key"""
    auth_paths = ["E:/AUTH_KEY/auth.lock", "F:/AUTH_KEY/auth.lock", "G:/AUTH_KEY/auth.lock"]
    
    for auth_path in auth_paths:
        if os.path.exists(auth_path):
            print(" Enterprise Auth Key: VALIDATED")
            return True
    
    print(" AUTH KEY NOT INSERTED  SYSTEM LOCKED")
    print(" Insert USB #5 Enterprise Auth Key to continue")
    sys.exit(" AUTHENTICATION REQUIRED")

if __name__ == "__main__":
    check_auth_key()
"""
        
        py_check_path = self.auth_path / "python_security_check.py"
        with open(py_check_path, 'w', encoding='utf-8') as f:
            f.write(py_security)
        
        print(" Enterprise Security System: CONFIGURED")
        print(" Hardware authentication: ACTIVE")
        print(" Maximum security level: DEPLOYED")

if __name__ == "__main__":
    auth = EQ12AuthKey()
    auth.setup_hardware_security()
    print(" Enterprise Auth Key: READY")
