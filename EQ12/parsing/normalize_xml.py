"""
EQ12 XML Normalization Module

Handles Windows Task XML encoding issues, entity escaping, and validation.
Solves common problems with XML files containing bare ampersands, encoding mismatches,
and malformed XML structures.

Key functions:
- repair_task_xml_file(): Fix encoding and entity issues in Windows Task XMLs
- Auto-detects UTF-16/UTF-8 encoding and normalizes to UTF-8
- Escapes bare &, %DATE%/%TIME% while preserving XML structure
- Validates with lxml.etree strict parser
"""

from __future__ import annotations

import re
from pathlib import Path

import charset_normalizer
from lxml import etree

# Regex to find unescaped entities (& not followed by valid XML entities)
ENTITY_FIX = re.compile(r"&(?!amp;|lt;|gt;|quot;|apos;)")

# Regex to find XML prolog declarations
XML_PROLOG = re.compile(r"^<\?xml.*?\?>", re.IGNORECASE | re.DOTALL)


def _to_utf8_bytes(p: Path) -> bytes:
    """
    Auto-detect encoding and convert to UTF-8 bytes.

    Args:
        p: Path to the file to convert

    Returns:
        UTF-8 encoded bytes
    """
    raw = p.read_bytes()

    # Use charset-normalizer for robust encoding detection
    detection = charset_normalizer.from_bytes(raw).best()
    encoding = detection.encoding if detection else "utf-8"

    # Decode with error replacement, then encode as UTF-8
    return raw.decode(encoding, errors="replace").encode("utf-8")


def _fix_xml_prolog(text: str) -> str:
    """
    Remove existing XML prolog and add correct UTF-8 prolog.

    Args:
        text: XML text content

    Returns:
        XML with corrected prolog
    """
    # Remove any existing XML declaration
    text = XML_PROLOG.sub("", text, count=1)

    # Add correct UTF-8 declaration
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{text.lstrip()}'


def _escape_text_nodes(text: str) -> str:
    """
    Escape unescaped ampersands while preserving existing XML entities.
    Keeps %DATE%, %TIME% tokens as-is but makes them XML-safe.

    Args:
        text: XML text content

    Returns:
        XML with properly escaped entities
    """
    return ENTITY_FIX.sub("&amp;", text)


def repair_task_xml_file(path_in: str | Path, path_out: str | Path | None = None) -> dict[str, any]:
    """
    Repair Windows Task XML file encoding and entity issues.

    This function:
    1. Auto-detects file encoding (UTF-16/UTF-8) and converts to UTF-8
    2. Fixes XML prolog declaration
    3. Escapes bare ampersands while preserving valid XML entities
    4. Preserves %DATE%/%TIME% and command arguments properly
    5. Validates the result with strict XML parser

    Args:
        path_in: Input XML file path
        path_out: Output file path (defaults to overwriting input)

    Returns:
        Dict with keys: path, fixed, errors

    Raises:
        etree.XMLSyntaxError: If XML is still invalid after repair attempts
        FileNotFoundError: If input file doesn't exist
        PermissionError: If unable to write output file
    """
    src = Path(path_in)

    if not src.exists():
        return {"path": str(src), "fixed": False, "errors": f"File not found: {src}"}

    try:
        # Step 1: Convert to UTF-8
        utf8_bytes = _to_utf8_bytes(src)
        utf8_text = utf8_bytes.decode("utf-8")

        # Step 2: Fix XML prolog
        utf8_text = _fix_xml_prolog(utf8_text)

        # Step 3: Escape entities
        utf8_text = _escape_text_nodes(utf8_text)

        # Step 4: Validate with strict parser (raises on error)
        parser = etree.XMLParser(recover=False, strip_cdata=False)
        etree.fromstring(utf8_text.encode("utf-8"), parser=parser)

        # Step 5: Write output
        out_path = Path(path_out) if path_out else src
        out_path.write_text(utf8_text, encoding="utf-8", newline="\n")

        return {"path": str(out_path), "fixed": True, "errors": None}

    except etree.XMLSyntaxError as e:
        return {"path": str(src), "fixed": False, "errors": f"XML syntax error: {e}"}

    except Exception as e:
        return {"path": str(src), "fixed": False, "errors": f"Unexpected error: {e}"}


def validate_xml_file(path: str | Path) -> dict[str, any]:
    """
    Validate XML file without modification.

    Args:
        path: XML file path to validate

    Returns:
        Dict with keys: path, valid, errors
    """
    file_path = Path(path)

    if not file_path.exists():
        return {
            "path": str(file_path),
            "valid": False,
            "errors": f"File not found: {file_path}",
        }

    try:
        content = file_path.read_text(encoding="utf-8")
        parser = etree.XMLParser(recover=False)
        etree.fromstring(content.encode("utf-8"), parser=parser)

        return {"path": str(file_path), "valid": True, "errors": None}

    except UnicodeDecodeError as e:
        return {
            "path": str(file_path),
            "valid": False,
            "errors": f"Encoding error: {e}",
        }

    except etree.XMLSyntaxError as e:
        return {
            "path": str(file_path),
            "valid": False,
            "errors": f"XML syntax error: {e}",
        }

    except Exception as e:
        return {
            "path": str(file_path),
            "valid": False,
            "errors": f"Unexpected error: {e}",
        }


# CLI entry point for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python normalize_xml.py <xml_file> [output_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    result = repair_task_xml_file(input_file, output_file)

    if result["fixed"]:
        print(f"✅ Successfully repaired: {result['path']}")
    else:
        print(f"❌ Failed to repair {result['path']}: {result['errors']}")
        sys.exit(1)
