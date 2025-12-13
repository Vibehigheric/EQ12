#!/usr/bin/env python3
"""
EQ12 Python Bytecode Cleanup Utility
Removes stale, corrupted, and unnecessary .pyc files
"""

import shutil
from datetime import datetime
from pathlib import Path


def cleanup_pyc_files(root_path=".", force_all=False, dry_run=False):
    """Clean up .pyc files in the specified directory"""
    root = Path(root_path)
    cleaned_count = 0
    bytes_cleaned = 0

    print("🧹 EQ12 .pyc Cleanup Utility")
    print(f"Root path: {root.absolute()}")
    print(f"Mode: {'DRY RUN' if dry_run else 'ACTIVE CLEANUP'}")
    print("=" * 50)

    if force_all:
        # Remove all __pycache__ directories
        pycache_dirs = list(root.rglob("__pycache__"))
        print(f"Found {len(pycache_dirs)} __pycache__ directories")

        for pycache_dir in pycache_dirs:
            try:
                if not dry_run:
                    # Calculate size before removal
                    size = sum(f.stat().st_size for f in pycache_dir.rglob("*") if f.is_file())
                    bytes_cleaned += size
                    shutil.rmtree(pycache_dir)

                print(f"✓ Removed: {pycache_dir}")
                cleaned_count += 1
            except Exception as e:
                print(f"✗ Failed: {pycache_dir} - {e}")
    else:
        # Selective cleanup
        pyc_files = list(root.rglob("*.pyc"))
        print(f"Found {len(pyc_files)} .pyc files")

        for pyc_file in pyc_files:
            should_remove = False
            reason = ""

            try:
                # Check if source exists
                if "__pycache__" in str(pyc_file):
                    parent_dir = pyc_file.parent.parent
                    source_name = pyc_file.stem.split(".")[0] + ".py"
                    source_path = parent_dir / source_name
                else:
                    source_path = pyc_file.with_suffix(".py")

                if not source_path.exists():
                    should_remove = True
                    reason = "Orphaned (no source file)"
                else:
                    # Check if source is newer
                    pyc_mtime = datetime.fromtimestamp(pyc_file.stat().st_mtime)
                    source_mtime = datetime.fromtimestamp(source_path.stat().st_mtime)

                    if source_mtime > pyc_mtime:
                        should_remove = True
                        reason = "Stale (source newer)"

                    # Check age (older than 30 days)
                    age = datetime.now() - pyc_mtime
                    if age.days > 30:
                        should_remove = True
                        reason = f"Old ({age.days} days)"

                if should_remove:
                    file_size = pyc_file.stat().st_size
                    if not dry_run:
                        pyc_file.unlink()
                        bytes_cleaned += file_size

                    print(f"✓ Removed: {pyc_file.name} - {reason}")
                    cleaned_count += 1

            except Exception as e:
                print(f"✗ Error processing {pyc_file}: {e}")

    print("=" * 50)
    print(f"Files processed: {cleaned_count}")
    print(f"Space cleaned: {bytes_cleaned / 1024 / 1024:.2f} MB")

    if dry_run:
        print("This was a DRY RUN - no files were actually removed")
        print("Run with --execute to perform actual cleanup")


def main():
    """Main cleanup function with CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 .pyc Cleanup Utility")
    parser.add_argument(
        "--path", default=".", help="Root path to clean (default: current directory)"
    )
    parser.add_argument(
        "--force-all", action="store_true", help="Remove all __pycache__ directories"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without actually removing",
    )
    parser.add_argument("--execute", action="store_true", help="Actually perform the cleanup")

    args = parser.parse_args()

    if not args.execute and not args.dry_run:
        print("Use --dry-run to see what would be cleaned, or --execute to actually clean")
        return

    cleanup_pyc_files(root_path=args.path, force_all=args.force_all, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
