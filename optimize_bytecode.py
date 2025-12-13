#!/usr/bin/env python3
"""
EQ12 Bytecode Optimization Script
Optimizes Python bytecode for production deployment
"""

import compileall
from pathlib import Path


def optimize_eq12_bytecode():
    """Optimize bytecode for EQ12 project"""
    root_path = Path(__file__).parent

    # Directories to optimize
    target_dirs = [
        "scripts",
        "buffalo_stack",
        "eq12_config.py",
        "scraper_starter/scraper.py",
        "omni_scraper",
        "graphics",
    ]

    print("🚀 EQ12 Bytecode Optimization Starting...")

    for target in target_dirs:
        target_path = root_path / target
        if target_path.exists():
            if target_path.is_file():
                # Single file optimization
                print(f"Optimizing {target}...")
                compileall.compile_file(
                    str(target_path),
                    force=True,
                    optimize=2,  # Maximum optimization
                    quiet=1,
                )
            else:
                # Directory optimization
                print(f"Optimizing directory {target}...")
                compileall.compile_dir(
                    str(target_path),
                    maxlevels=10,
                    force=True,
                    optimize=2,  # Maximum optimization
                    quiet=1,
                )

    print("✅ Bytecode optimization complete!")
    print("Optimized .pyc files are available in __pycache__ directories")


if __name__ == "__main__":
    optimize_eq12_bytecode()
