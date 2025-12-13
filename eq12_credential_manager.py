#!/usr/bin/env python3
"""
EQ12 Secure Credential Manager

Manages API keys and sensitive configuration safely:
- Stores credentials in encrypted local files
- Never commits secrets to version control
- Provides secure access for EQ12 applications
- Includes key rotation and validation features
"""

import base64
import getpass
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# EQ12 Configuration
EQ12_HOME = Path(os.getenv("EQ12_HOME", r"C:\EQ12"))
KEYS_DIR = EQ12_HOME / "keys"
CREDENTIALS_FILE = KEYS_DIR / "credentials.json"
ENCRYPTED_FILE = KEYS_DIR / "credentials.enc"

# Ensure keys directory exists
KEYS_DIR.mkdir(parents=True, exist_ok=True)


class EQ12CredentialManager:
    """Secure credential management for EQ12"""

    def __init__(self):
        self.keys_dir = KEYS_DIR
        self.credentials_file = CREDENTIALS_FILE
        self.encrypted_file = ENCRYPTED_FILE

    def _get_encryption_key(self, password: str) -> bytes:
        """Derive encryption key from password"""
        salt = b"eq12_salt_2025"  # In production, use random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt_credentials(self, password: str) -> bool:
        """Encrypt existing credentials file"""
        if not self.credentials_file.exists():
            print("❌ No credentials.json found to encrypt")
            return False

        try:
            # Read existing credentials
            with open(self.credentials_file) as f:
                credentials = json.load(f)

            # Encrypt with password
            key = self._get_encryption_key(password)
            fernet = Fernet(key)

            encrypted_data = fernet.encrypt(json.dumps(credentials).encode())

            # Save encrypted file
            with open(self.encrypted_file, "wb") as f:
                f.write(encrypted_data)

            print("✅ Credentials encrypted successfully")
            print(f"🔒 Encrypted file: {self.encrypted_file}")

            # Optionally remove plaintext file
            confirm = input("Remove plaintext credentials.json? (y/N): ")
            if confirm.lower().startswith("y"):
                self.credentials_file.unlink()
                print("🗑️ Plaintext credentials removed")

            return True

        except Exception as e:
            print(f"❌ Encryption failed: {e}")
            return False

    def decrypt_credentials(self, password: str) -> dict | None:
        """Decrypt credentials with password"""
        if not self.encrypted_file.exists():
            print("❌ No encrypted credentials found")
            return None

        try:
            key = self._get_encryption_key(password)
            fernet = Fernet(key)

            with open(self.encrypted_file, "rb") as f:
                encrypted_data = f.read()

            decrypted_data = fernet.decrypt(encrypted_data)
            credentials = json.loads(decrypted_data.decode())

            return credentials

        except Exception as e:
            print(f"❌ Decryption failed: {e}")
            return None

    def load_credentials(self) -> dict[str, str]:
        """Load credentials from file or environment"""
        credentials = {}

        # Try environment variables first
        env_keys = [
            "OPENAI_API_KEY",
            "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_CHAT_ID",
            "ODDS_API_KEY",
            "DISCORD_BOT_TOKEN",
            "NGROK_TOKEN",
        ]

        for key in env_keys:
            value = os.environ.get(key)
            if value and not value.startswith("REPLACE_"):
                credentials[key] = value

        # Try encrypted file if password provided
        if len(sys.argv) > 1 and sys.argv[1] == "--decrypt":
            password = getpass.getpass("Enter encryption password: ")
            encrypted_creds = self.decrypt_credentials(password)
            if encrypted_creds:
                credentials.update(encrypted_creds)

        # Try plaintext file as fallback
        elif self.credentials_file.exists():
            try:
                with open(self.credentials_file) as f:
                    file_creds = json.load(f)
                    credentials.update(file_creds)
            except Exception as e:
                print(f"⚠️ Could not load credentials file: {e}")

        return credentials

    def save_credentials(self, credentials: dict[str, str]) -> bool:
        """Save credentials to file"""
        try:
            # Add metadata
            credentials_with_meta = {
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "version": "1.0",
                    "encrypted": False,
                },
                "credentials": credentials,
            }

            with open(self.credentials_file, "w") as f:
                json.dump(credentials_with_meta, f, indent=2)

            # Set secure permissions (Windows)
            if os.name == "nt":
                os.system(
                    f'icacls "{self.credentials_file}" /grant:r "%USERNAME%":F /remove Everyone'
                )

            print(f"✅ Credentials saved to {self.credentials_file}")
            print("⚠️ Remember to encrypt this file for production use")
            return True

        except Exception as e:
            print(f"❌ Failed to save credentials: {e}")
            return False

    def validate_credentials(self, credentials: dict[str, str]) -> dict[str, bool]:
        """Validate credential format and basic checks"""
        validation = {}

        # OpenAI API Key
        openai_key = credentials.get("OPENAI_API_KEY", "")
        validation["OPENAI_API_KEY"] = openai_key.startswith("sk-") and len(openai_key) > 40

        # Telegram Bot Token
        telegram_token = credentials.get("TELEGRAM_BOT_TOKEN", "")
        validation["TELEGRAM_BOT_TOKEN"] = ":" in telegram_token and len(telegram_token) > 30

        # Telegram Chat ID
        telegram_chat = credentials.get("TELEGRAM_CHAT_ID", "")
        validation["TELEGRAM_CHAT_ID"] = telegram_chat.isdigit() and len(telegram_chat) > 5

        # Odds API Key
        odds_key = credentials.get("ODDS_API_KEY", "")
        validation["ODDS_API_KEY"] = len(odds_key) > 20 and odds_key.replace("-", "").isalnum()

        return validation

    def setup_interactive(self) -> dict[str, str]:
        """Interactive credential setup"""
        print("=== EQ12 Credential Setup ===")
        print("Enter your API keys (press Enter to skip):")
        print("")

        credentials = {}

        # OpenAI API Key
        openai_key = getpass.getpass("OpenAI API Key (sk-...): ").strip()
        if openai_key and openai_key.startswith("sk-"):
            credentials["OPENAI_API_KEY"] = openai_key

        # Telegram Bot Token
        telegram_token = input("Telegram Bot Token: ").strip()
        if telegram_token and ":" in telegram_token:
            credentials["TELEGRAM_BOT_TOKEN"] = telegram_token

        # Telegram Chat ID
        telegram_chat = input("Telegram Chat ID: ").strip()
        if telegram_chat and telegram_chat.isdigit():
            credentials["TELEGRAM_CHAT_ID"] = telegram_chat

        # Odds API Key
        odds_key = input("Odds API Key: ").strip()
        if odds_key:
            credentials["ODDS_API_KEY"] = odds_key

        # Discord Bot Token
        discord_token = input("Discord Bot Token (optional): ").strip()
        if discord_token:
            credentials["DISCORD_BOT_TOKEN"] = discord_token

        # ngrok Token
        ngrok_token = input("ngrok Token (optional): ").strip()
        if ngrok_token:
            credentials["NGROK_TOKEN"] = ngrok_token

        return credentials


def main():
    """Main credential manager interface"""
    manager = EQ12CredentialManager()

    if len(sys.argv) < 2:
        print("EQ12 Credential Manager")
        print("")
        print("Usage:")
        print("  python eq12_credential_manager.py setup     # Interactive setup")
        print("  python eq12_credential_manager.py validate  # Validate existing")
        print("  python eq12_credential_manager.py encrypt   # Encrypt credentials")
        print("  python eq12_credential_manager.py --decrypt # Load encrypted")
        print("  python eq12_credential_manager.py status    # Show status")
        return

    command = sys.argv[1]

    if command == "setup":
        credentials = manager.setup_interactive()
        if credentials:
            validation = manager.validate_credentials(credentials)

            print("\n=== Validation Results ===")
            for key, valid in validation.items():
                status = "✅" if valid else "❌"
                print(f"{status} {key}: {'Valid' if valid else 'Invalid format'}")

            if all(validation.values()):
                manager.save_credentials(credentials)

                # Offer encryption
                encrypt = input("\nEncrypt credentials? (recommended) (y/N): ")
                if encrypt.lower().startswith("y"):
                    password = getpass.getpass("Choose encryption password: ")
                    manager.encrypt_credentials(password)
            else:
                print("\n❌ Some credentials have invalid format. Please check and retry.")

    elif command == "validate":
        credentials = manager.load_credentials()
        validation = manager.validate_credentials(credentials)

        print("=== Credential Validation ===")
        for key, valid in validation.items():
            status = "✅" if valid else "❌"
            present = "Present" if key in credentials else "Missing"
            print(f"{status} {key}: {present}")

    elif command == "encrypt":
        password = getpass.getpass("Choose encryption password: ")
        manager.encrypt_credentials(password)

    elif command == "status":
        print("=== EQ12 Credential Status ===")
        print(f"Keys Directory: {KEYS_DIR}")
        print(f"Credentials File: {'✅ Exists' if CREDENTIALS_FILE.exists() else '❌ Missing'}")
        print(f"Encrypted File: {'✅ Exists' if ENCRYPTED_FILE.exists() else '❌ Missing'}")

        # Check environment variables
        env_count = sum(
            1
            for key in ["OPENAI_API_KEY", "TELEGRAM_BOT_TOKEN", "ODDS_API_KEY"]
            if os.environ.get(key) and not os.environ.get(key).startswith("REPLACE_")
        )
        print(f"Environment Variables: {env_count} configured")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
