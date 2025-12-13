#!/usr/bin/env python3
"""
EQ12 Expert ASCII Cleaner - Professional Engineering Grade
Remove non-ASCII characters and ensure clean, compatible code files

Author: EQ12 Engineering Team
Version: 2.1.0
Date: 2025-11-22
Python: 3.12+

This script safely removes:
- Non-ASCII characters from Python/PowerShell/JSON files
- Hidden Unicode characters
- Byte Order Marks (BOMs)
- Invalid control characters
- Problematic encoding artifacts

Teaching Notes (30-Day Python Curriculum Integration):
- File operations (Day 25): Reading and writing files safely
- String manipulation (Day 8): Processing and cleaning text
- Error handling (Day 19): Robust file processing with try/except
- Functions (Day 11): Modular, reusable cleaning functions
- Logging (Day 26): Professional logging for operations tracking
"""

import sys
import os
import re
import pathlib
from datetime import datetime
import logging
import json
import shutil

class ASCIIFormatter(logging.Formatter):
    """Custom formatter ensuring ASCII-safe log output"""

    def format(self, record):
        msg = super().format(record)
        return msg.encode('ascii', 'replace').decode('ascii')

def setup_logging():
    """Set up ASCII-safe logging for the cleaning system"""
    log_dir = pathlib.Path("C:/EQ12/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger('eq12_ascii_cleaner')
    logger.setLevel(logging.INFO)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"eq12_ascii_clean_{timestamp}.log"

    file_handler = logging.FileHandler(log_file, encoding='ascii', errors='replace')
    file_handler.setFormatter(ASCIIFormatter('%(asctime)s - %(levelname)s - %(message)s'))

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ASCIIFormatter('%(levelname)s: %(message)s'))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

class EQ12ASCIICleaner:
    """
    Expert-level ASCII cleaning system for EQ12 code files

    Teaching note (Day 20 - Classes): This class encapsulates all cleaning
    logic with clear methods for different file types and operations.
    """

    def __init__(self, dry_run=False, create_backups=True):
        """Initialize the ASCII cleaner with configuration"""
        self.logger = setup_logging()
        self.dry_run = dry_run
        self.create_backups = create_backups
        self.stats = {
            'files_scanned': 0,
            'files_cleaned': 0,
            'files_backed_up': 0,
            'characters_removed': 0,
            'errors': 0
        }

        # File extensions to process
        self.target_extensions = {'.py', '.ps1', '.json', '.md', '.txt', '.cfg', '.ini'}

        # Common problematic Unicode characters and their ASCII replacements
        self.unicode_replacements = {
            # Smart quotes
            '\u2018': "'",  # Left single quotation mark
            '\u2019': "'",  # Right single quotation mark
            '\u201c': '"',  # Left double quotation mark
            '\u201d': '"',  # Right double quotation mark

            # Dashes
            '\u2013': '-',  # En dash
            '\u2014': '--', # Em dash
            '\u2212': '-',  # Minus sign

            # Spaces
            '\u00a0': ' ',  # Non-breaking space
            '\u2000': ' ',  # En quad
            '\u2001': ' ',  # Em quad
            '\u2002': ' ',  # En space
            '\u2003': ' ',  # Em space
            '\u2009': ' ',  # Thin space

            # Other common characters
            '\u2026': '...',  # Horizontal ellipsis
            '\u00b7': '*',    # Middle dot
            '\u2022': '*',    # Bullet
            '\u00ae': '(R)',  # Registered trademark
            '\u00a9': '(C)',  # Copyright
            '\u2122': '(TM)', # Trademark
        }

    def detect_encoding(self, file_path):
        """
        Detect file encoding and BOM presence

        Teaching note (Day 25 - File operations): Different files can have
        different encodings, so we need to detect them before processing.
        """
        try:
            # Read first few bytes to check for BOM
            with open(file_path, 'rb') as f:
                raw_bytes = f.read(4)

            # Check for common BOMs
            if raw_bytes.startswith(b'\xef\xbb\xbf'):
                return 'utf-8-sig', True
            elif raw_bytes.startswith(b'\xff\xfe'):
                return 'utf-16le', True
            elif raw_bytes.startswith(b'\xfe\xff'):
                return 'utf-16be', True
            elif raw_bytes.startswith(b'\xff\xfe\x00\x00'):
                return 'utf-32le', True
            elif raw_bytes.startswith(b'\x00\x00\xfe\xff'):
                return 'utf-32be', True

            # Try to detect encoding by attempting to decode
            encodings_to_try = ['utf-8', 'cp1252', 'iso-8859-1', 'ascii']

            for encoding in encodings_to_try:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        f.read()
                    return encoding, False
                except UnicodeDecodeError:
                    continue

            # Default fallback
            return 'utf-8', False

        except Exception as e:
            self.logger.warning(f"Could not detect encoding for {file_path}: {str(e)}")
            return 'utf-8', False

    def create_backup(self, file_path):
        """
        Create a backup of the original file

        Teaching note (Day 25 - File operations): Always backup files before
        making changes to prevent data loss.
        """
        if not self.create_backups:
            return True

        try:
            backup_dir = pathlib.Path(file_path).parent / "backups"
            backup_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_name = pathlib.Path(file_path).name
            backup_name = f"{original_name}.backup_{timestamp}"
            backup_path = backup_dir / backup_name

            shutil.copy2(file_path, backup_path)
            self.stats['files_backed_up'] += 1
            self.logger.info(f"Backup created: {backup_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create backup for {file_path}: {str(e)}")
            return False

    def clean_text_content(self, content, file_path):
        """
        Clean text content by removing non-ASCII characters

        Teaching note (Day 8 - String manipulation): Using string methods
        and regular expressions to find and replace problematic characters.
        """
        original_length = len(content)
        cleaned_content = content
        changes_made = []

        # Remove BOM if present
        if cleaned_content.startswith('\ufeff'):
            cleaned_content = cleaned_content[1:]
            changes_made.append("Removed BOM")

        # Replace common Unicode characters with ASCII equivalents
        for unicode_char, ascii_replacement in self.unicode_replacements.items():
            if unicode_char in cleaned_content:
                count = cleaned_content.count(unicode_char)
                cleaned_content = cleaned_content.replace(unicode_char, ascii_replacement)
                changes_made.append(f"Replaced {count} instances of U+{ord(unicode_char):04X}")

        # Remove or replace other non-ASCII characters
        def replace_non_ascii(match):
            char = match.group(0)
            # Keep common whitespace characters
            if char in '\t\n\r':
                return char
            # Replace other non-ASCII with placeholder or remove
            return f"[U+{ord(char):04X}]"

        # Find all non-ASCII characters (Day 19 - Error handling with regex)
        try:
            non_ascii_pattern = re.compile(r'[^\x00-\x7F]')
            matches = non_ascii_pattern.findall(cleaned_content)

            if matches:
                # Log what we found
                unique_chars = set(matches)
                for char in unique_chars:
                    count = matches.count(char)
                    self.logger.warning(f"Found non-ASCII character U+{ord(char):04X} ('{char}') {count} times in {file_path}")

                # Replace non-ASCII characters
                cleaned_content = non_ascii_pattern.sub(replace_non_ascii, cleaned_content)
                changes_made.append(f"Replaced {len(matches)} non-ASCII characters")

        except Exception as e:
            self.logger.error(f"Error processing non-ASCII characters in {file_path}: {str(e)}")

        # Remove null bytes and other control characters
        control_chars_removed = 0
        for i in range(32):
            if i not in [9, 10, 13]:  # Keep tab, newline, carriage return
                char = chr(i)
                if char in cleaned_content:
                    count = cleaned_content.count(char)
                    cleaned_content = cleaned_content.replace(char, '')
                    control_chars_removed += count

        if control_chars_removed > 0:
            changes_made.append(f"Removed {control_chars_removed} control characters")

        # Calculate statistics
        characters_removed = original_length - len(cleaned_content)
        self.stats['characters_removed'] += characters_removed

        # Log changes if any were made
        if changes_made:
            self.logger.info(f"Cleaned {file_path}: {', '.join(changes_made)}")

        return cleaned_content, len(changes_made) > 0

    def clean_python_file(self, file_path):
        """
        Clean Python files with special handling for syntax

        Teaching note (Day 11 - Functions): Specialized function for Python
        files that checks syntax after cleaning.
        """
        try:
            # Detect encoding
            encoding, has_bom = self.detect_encoding(file_path)

            # Read file content
            with open(file_path, 'r', encoding=encoding) as f:
                original_content = f.read()

            # Clean the content
            cleaned_content, changes_made = self.clean_text_content(original_content, file_path)

            if changes_made:
                # Verify Python syntax after cleaning
                try:
                    compile(cleaned_content, file_path, 'exec')

                    if not self.dry_run:
                        # Create backup
                        if not self.create_backup(file_path):
                            self.logger.error(f"Skipping {file_path} - backup failed")
                            return False

                        # Write cleaned content
                        with open(file_path, 'w', encoding='ascii', errors='replace') as f:
                            f.write(cleaned_content)

                        self.stats['files_cleaned'] += 1
                        self.logger.info(f"Successfully cleaned Python file: {file_path}")
                    else:
                        self.logger.info(f"DRY RUN: Would clean Python file: {file_path}")

                    return True

                except SyntaxError as e:
                    self.logger.error(f"Syntax error after cleaning {file_path}: {str(e)}")
                    self.stats['errors'] += 1
                    return False
            else:
                self.logger.info(f"No changes needed for Python file: {file_path}")
                return True

        except Exception as e:
            self.logger.error(f"Error cleaning Python file {file_path}: {str(e)}")
            self.stats['errors'] += 1
            return False

    def clean_json_file(self, file_path):
        """
        Clean JSON files with validation

        Teaching note (Day 25 - File operations): JSON files need special
        handling to ensure they remain valid after cleaning.
        """
        try:
            # Detect encoding
            encoding, has_bom = self.detect_encoding(file_path)

            # Read file content
            with open(file_path, 'r', encoding=encoding) as f:
                original_content = f.read()

            # Clean the content
            cleaned_content, changes_made = self.clean_text_content(original_content, file_path)

            if changes_made:
                # Validate JSON after cleaning
                try:
                    json.loads(cleaned_content)

                    if not self.dry_run:
                        # Create backup
                        if not self.create_backup(file_path):
                            self.logger.error(f"Skipping {file_path} - backup failed")
                            return False

                        # Write cleaned content
                        with open(file_path, 'w', encoding='ascii', errors='replace') as f:
                            f.write(cleaned_content)

                        self.stats['files_cleaned'] += 1
                        self.logger.info(f"Successfully cleaned JSON file: {file_path}")
                    else:
                        self.logger.info(f"DRY RUN: Would clean JSON file: {file_path}")

                    return True

                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON validation error after cleaning {file_path}: {str(e)}")
                    self.stats['errors'] += 1
                    return False
            else:
                self.logger.info(f"No changes needed for JSON file: {file_path}")
                return True

        except Exception as e:
            self.logger.error(f"Error cleaning JSON file {file_path}: {str(e)}")
            self.stats['errors'] += 1
            return False

    def clean_generic_file(self, file_path):
        """
        Clean other text files (PowerShell, Markdown, etc.)

        Teaching note (Day 11 - Functions): Generic cleaning function for
        files that don't need special syntax validation.
        """
        try:
            # Detect encoding
            encoding, has_bom = self.detect_encoding(file_path)

            # Read file content
            with open(file_path, 'r', encoding=encoding) as f:
                original_content = f.read()

            # Clean the content
            cleaned_content, changes_made = self.clean_text_content(original_content, file_path)

            if changes_made:
                if not self.dry_run:
                    # Create backup
                    if not self.create_backup(file_path):
                        self.logger.error(f"Skipping {file_path} - backup failed")
                        return False

                    # Write cleaned content
                    with open(file_path, 'w', encoding='ascii', errors='replace') as f:
                        f.write(cleaned_content)

                    self.stats['files_cleaned'] += 1
                    self.logger.info(f"Successfully cleaned file: {file_path}")
                else:
                    self.logger.info(f"DRY RUN: Would clean file: {file_path}")

                return True
            else:
                self.logger.info(f"No changes needed for file: {file_path}")
                return True

        except Exception as e:
            self.logger.error(f"Error cleaning file {file_path}: {str(e)}")
            self.stats['errors'] += 1
            return False

    def clean_directory(self, directory_path, recursive=True):
        """
        Clean all supported files in a directory

        Teaching note (Day 9 - Loops): Using loops to process multiple files
        in a directory structure.
        """
        directory = pathlib.Path(directory_path)

        if not directory.exists():
            self.logger.error(f"Directory does not exist: {directory_path}")
            return False

        self.logger.info(f"Scanning directory: {directory_path}")

        # Get all files to process
        if recursive:
            files_to_process = []
            for ext in self.target_extensions:
                pattern = f"**/*{ext}"
                files_to_process.extend(directory.glob(pattern))
        else:
            files_to_process = []
            for ext in self.target_extensions:
                pattern = f"*{ext}"
                files_to_process.extend(directory.glob(pattern))

        self.logger.info(f"Found {len(files_to_process)} files to process")

        # Process each file
        for file_path in files_to_process:
            self.stats['files_scanned'] += 1

            # Skip backup directories
            if 'backup' in str(file_path).lower():
                continue

            # Skip __pycache__ directories
            if '__pycache__' in str(file_path):
                continue

            # Determine file type and use appropriate cleaner
            if file_path.suffix == '.py':
                self.clean_python_file(file_path)
            elif file_path.suffix == '.json':
                self.clean_json_file(file_path)
            else:
                self.clean_generic_file(file_path)

        return True

    def generate_report(self):
        """
        Generate cleaning report

        Teaching note (Day 25 - File operations): Creating a summary report
        of all cleaning operations performed.
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'mode': 'DRY RUN' if self.dry_run else 'ACTIVE',
            'statistics': self.stats,
            'settings': {
                'create_backups': self.create_backups,
                'target_extensions': list(self.target_extensions),
                'unicode_replacements_count': len(self.unicode_replacements)
            }
        }

        # Save report
        log_dir = pathlib.Path("C:/EQ12/logs")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = log_dir / f"eq12_ascii_clean_report_{timestamp}.json"

        try:
            with open(report_path, 'w', encoding='ascii', errors='replace') as f:
                json.dump(report, f, indent=2, ensure_ascii=True)

            self.logger.info(f"Report saved: {report_path}")

        except Exception as e:
            self.logger.error(f"Failed to save report: {str(e)}")

        # Print summary
        self.logger.info("=== ASCII Cleaning Summary ===")
        self.logger.info(f"Files scanned: {self.stats['files_scanned']}")
        self.logger.info(f"Files cleaned: {self.stats['files_cleaned']}")
        self.logger.info(f"Files backed up: {self.stats['files_backed_up']}")
        self.logger.info(f"Characters removed: {self.stats['characters_removed']}")
        self.logger.info(f"Errors: {self.stats['errors']}")

        return report

def main():
    """
    Main entry point for ASCII cleaning script

    Teaching note (Day 11 - Functions): Main function handles command line
    arguments and orchestrates the cleaning process.
    """
    import argparse

    parser = argparse.ArgumentParser(description='EQ12 Expert ASCII Cleaner')
    parser.add_argument('path', help='Path to file or directory to clean')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backup files')
    parser.add_argument('--recursive', action='store_true', default=True, help='Process directories recursively')

    args = parser.parse_args()

    try:
        # Create cleaner instance
        cleaner = EQ12ASCIICleaner(
            dry_run=args.dry_run,
            create_backups=not args.no_backup
        )

        # Clean the specified path
        target_path = pathlib.Path(args.path)

        if target_path.is_file():
            # Clean single file
            if target_path.suffix == '.py':
                success = cleaner.clean_python_file(target_path)
            elif target_path.suffix == '.json':
                success = cleaner.clean_json_file(target_path)
            else:
                success = cleaner.clean_generic_file(target_path)

            cleaner.stats['files_scanned'] = 1

        elif target_path.is_dir():
            # Clean directory
            success = cleaner.clean_directory(target_path, recursive=args.recursive)

        else:
            cleaner.logger.error(f"Path not found: {args.path}")
            sys.exit(1)

        # Generate report
        cleaner.generate_report()

        # Exit with appropriate code
        if cleaner.stats['errors'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        print("\nCleaning cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
