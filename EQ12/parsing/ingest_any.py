"""
EQ12 Universal File Parser

Auto-detects and parses any common file format: XML, JSON, YAML, CSV, HTML, LOG.
Returns normalized Python dict/list structures for easy processing.

Key functions:
- load_any(): Auto-detect format and parse to Python objects
- Supports: JSON, YAML, XML, HTML, CSV, EQ12 logs, raw bytes
- Robust error handling with fallbacks
- Optimized for EQ12 data processing workflows
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from lxml import etree

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def _xml_to_dict(node: etree.Element) -> dict[str, Any]:
    """
    Convert XML element to dictionary representation.

    Args:
        node: XML element node

    Returns:
        Dictionary representation of XML
    """
    result = {}

    # Add attributes
    if node.attrib:
        result.update(node.attrib)

    # Process children
    children = list(node)
    if children:
        for child in children:
            tag = child.tag
            child_dict = _xml_to_dict(child)

            # Handle multiple elements with same tag
            if tag in result:
                if not isinstance(result[tag], list):
                    result[tag] = [result[tag]]
                result[tag].append(child_dict)
            else:
                result[tag] = child_dict

    # Add text content
    text = (node.text or "").strip()
    if text:
        if children or node.attrib:
            result["#text"] = text
        else:
            return text

    return result if result else None


def _parse_eq12_log_line(line: str) -> dict[str, Any] | None:
    """
    Parse EQ12 log format: [timestamp] - module - level - message

    Args:
        line: Log line to parse

    Returns:
        Parsed log entry or None if not EQ12 format
    """
    import re
    from datetime import datetime

    # EQ12 log pattern: [2025-10-05 10:30:45] - module_name - INFO - Message
    pattern = r"^\[([^\]]+)\]\s*-\s*([^-]+)\s*-\s*([^-]+)\s*-\s*(.+)$"
    match = re.match(pattern, line.strip())

    if not match:
        return None

    timestamp_str, module, level, message = match.groups()

    try:
        # Try to parse timestamp
        timestamp = datetime.fromisoformat(timestamp_str.replace("T", " "))
    except ValueError:
        timestamp = timestamp_str

    return {
        "timestamp": (timestamp.isoformat() if hasattr(timestamp, "isoformat") else timestamp),
        "module": module.strip(),
        "level": level.strip().upper(),
        "message": message.strip(),
    }


def _try_parse_json(data: bytes) -> Any:
    """Try to parse data as JSON."""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _try_parse_yaml(data: bytes) -> Any:
    """Try to parse data as YAML."""
    if not YAML_AVAILABLE:
        return None

    try:
        return yaml.safe_load(io.BytesIO(data))
    except (yaml.YAMLError, UnicodeDecodeError):
        return None


def _try_parse_xml(data: bytes) -> dict[str, Any] | None:
    """Try to parse data as XML."""
    try:
        root = etree.fromstring(data)
        return {root.tag: _xml_to_dict(root)}
    except (etree.XMLSyntaxError, UnicodeDecodeError):
        return None


def _try_parse_html(data: bytes) -> dict[str, Any] | None:
    """Try to parse data as HTML."""
    try:
        soup = BeautifulSoup(data, "html5lib")

        return {
            "title": soup.title.string if soup.title else None,
            "meta": {
                (m.get("name") or m.get("property") or "unknown"): m.get("content")
                for m in soup.find_all("meta")
                if m.get("content")
            },
            "links": [a.get("href") for a in soup.find_all("a") if a.get("href")],
            "text": soup.get_text().strip()[:1000],  # First 1000 chars
        }
    except Exception:
        return None


def _try_parse_csv(data: bytes) -> list[dict[str, str]] | None:
    """Try to parse data as CSV."""
    try:
        text = data.decode("utf-8", "replace")

        # Try to detect if it looks like CSV
        if "\n" not in text or ("," not in text and "\t" not in text):
            return None

        # Try comma-separated first
        try:
            rows = list(csv.DictReader(io.StringIO(text)))
            if rows and len(rows) > 0:
                return rows
        except csv.Error:
            pass

        # Try tab-separated
        try:
            rows = list(csv.DictReader(io.StringIO(text), delimiter="\t"))
            if rows and len(rows) > 0:
                return rows
        except csv.Error:
            pass

        return None

    except UnicodeDecodeError:
        return None


def _try_parse_eq12_log(data: bytes) -> list[dict[str, Any]] | None:
    """Try to parse as EQ12 log format."""
    try:
        text = data.decode("utf-8", "replace")
        lines = text.split("\n")

        parsed_lines = []
        for line in lines:
            if line.strip():
                parsed = _parse_eq12_log_line(line)
                if parsed:
                    parsed_lines.append(parsed)

        # If we parsed at least 50% of non-empty lines, consider it a log
        non_empty_lines = [l for l in lines if l.strip()]
        if non_empty_lines and len(parsed_lines) >= len(non_empty_lines) * 0.5:
            return parsed_lines

        return None

    except UnicodeDecodeError:
        return None


def load_any(path_or_bytes: str | Path | bytes) -> Any:
    """
    Auto-detect file format and parse to Python objects.

    Tries formats in order: JSON, YAML, XML, HTML, CSV, EQ12 logs, raw.

    Args:
        path_or_bytes: File path or raw bytes to parse

    Returns:
        Parsed data structure (dict, list, or dict with 'raw' key)

    Example:
        # Parse any file
        data = load_any("config.json")
        data = load_any("tasks.xml")
        data = load_any("report.csv")
        data = load_any(Path("logs/boundary.log"))
    """
    # Handle path input
    if isinstance(path_or_bytes, (str, Path)):
        file_path = Path(path_or_bytes)

        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}

        try:
            data = file_path.read_bytes()
            file_path.suffix.lower()
        except Exception as e:
            return {"error": f"Could not read file: {e}"}
    else:
        data = path_or_bytes

    # Try formats in order of likelihood/performance

    # 1. Try JSON (most common, fastest)
    result = _try_parse_json(data)
    if result is not None:
        return result

    # 2. Try YAML (if available)
    if YAML_AVAILABLE:
        result = _try_parse_yaml(data)
        if result is not None:
            return result

    # 3. Try XML
    result = _try_parse_xml(data)
    if result is not None:
        return result

    # 4. Try HTML
    result = _try_parse_html(data)
    if result is not None:
        return result

    # 5. Try CSV
    result = _try_parse_csv(data)
    if result is not None:
        return result

    # 6. Try EQ12 log format
    result = _try_parse_eq12_log(data)
    if result is not None:
        return {"log_entries": result}

    # 7. Fallback to raw data
    try:
        text = data.decode("utf-8", "replace")
        return {"raw_text": text}
    except Exception:
        return {"raw_bytes": data}


def detect_format(path_or_bytes: str | Path | bytes) -> str:
    """
    Detect the likely format of a file without fully parsing it.

    Args:
        path_or_bytes: File path or raw bytes

    Returns:
        Format name: 'json', 'yaml', 'xml', 'html', 'csv', 'log', 'text', 'binary'
    """
    # Handle path input
    if isinstance(path_or_bytes, (str, Path)):
        file_path = Path(path_or_bytes)

        if not file_path.exists():
            return "missing"

        ext = file_path.suffix.lower()

        # Quick extension-based detection
        if ext in [".json", ".jsonl"]:
            return "json"
        if ext in [".yaml", ".yml"]:
            return "yaml"
        if ext in [".xml", ".xsd", ".xsl"]:
            return "xml"
        if ext in [".html", ".htm"]:
            return "html"
        if ext in [".csv", ".tsv"]:
            return "csv"
        if ext in [".log", ".txt"]:
            return "log"

        try:
            data = file_path.read_bytes()
        except Exception:
            return "error"
    else:
        data = path_or_bytes

    # Content-based detection for first 1KB
    sample = data[:1024] if len(data) > 1024 else data

    try:
        sample_text = sample.decode("utf-8", "replace")

        # Check for format markers
        if sample_text.strip().startswith(("{", "[")):
            return "json"
        if sample_text.strip().startswith("<?xml"):
            return "xml"
        if any(tag in sample_text.lower() for tag in ["<html", "<head", "<body"]):
            return "html"
        if sample_text.count(",") > 3 and "\n" in sample_text:
            return "csv"
        if "[" in sample_text and "] -" in sample_text:
            return "log"
        if sample_text.count("\n") > 0:
            return "text"
        return "text"

    except UnicodeDecodeError:
        return "binary"


# CLI entry point for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ingest_any.py <file_path>")
        print("       python ingest_any.py --detect <file_path>")
        sys.exit(1)

    if sys.argv[1] == "--detect":
        if len(sys.argv) < 3:
            print("Usage: python ingest_any.py --detect <file_path>")
            sys.exit(1)

        file_path = sys.argv[2]
        format_name = detect_format(file_path)
        print(f"Detected format: {format_name}")
    else:
        file_path = sys.argv[1]
        result = load_any(file_path)
        print(json.dumps(result, indent=2, default=str))
