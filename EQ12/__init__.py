"""
EQ12 Parsing Module - Comprehensive toolkit for handling XML, JSON, YAML, CSV, HTML, and log files.

This module provides robust, VS Code + Copilot optimized parsing utilities for the EQ12 stack.
Designed to handle Windows Task XMLs, boundary logs, configuration files, and any data format.

Key features:
- XML normalization and repair (encoding, entity escaping)
- Universal file format detection and parsing
- EQ12 log parsing and JSONL conversion
- JSON schema validation with friendly errors
- PowerShell integration helpers

Usage:
    from eq12.parsing import normalize_xml, ingest_any, logs, validate_json
"""

__version__ = "1.0.0"
__author__ = "EQ12 Development Team"

# Core modules
from .ingest_any import load_any
from .logs import parse_eq12_errorboundary_log
from .normalize_xml import repair_task_xml_file
from .validate_json import validate

__all__ = [
    "load_any",
    "parse_eq12_errorboundary_log",
    "repair_task_xml_file",
    "validate",
]
