#!/usr/bin/env python3
"""
EQ12 Package Initialization
Main automation and scraping ecosystem for EQ12 project
"""

__version__ = "2.0.0"
__author__ = "EQ12 Team"
__description__ = "EQ12 Automation and Scraping Ecosystem"

# Import core modules for easy access
from .eq12_config import (
    EQ12_CONFIG,
    EQ12_LOGS,
    EQ12_ROOT,
    get_api_key,
    get_eq12_required_keys,
    load_eq12_env,
    setup_eq12_logging,
    validate_eq12_environment,
    write_eq12_snapshot,
)

# Package-level constants
PACKAGE_NAME = "eq12"
BUFFALO_STACK_VERSION = "14215"

# Supported automation modules
AUTOMATION_MODULES = [
    "civil_service_tracker",
    "edgegod_parlays_bot",
    "travel_bot",
    "dropship_sync",
    "odds_parser",
    "parlay_builder",
]

# Export public API
__all__ = [
    "AUTOMATION_MODULES",
    "BUFFALO_STACK_VERSION",
    "EQ12_CONFIG",
    "EQ12_LOGS",
    "EQ12_ROOT",
    "PACKAGE_NAME",
    "get_api_key",
    "get_eq12_required_keys",
    "load_eq12_env",
    "setup_eq12_logging",
    "validate_eq12_environment",
    "write_eq12_snapshot",
]
