#!/usr/bin/env python3
"""
EQ12 ASCII Filter Utility
==========================
Cleans any Copilot output to pure ASCII
Prevents Unicode corruption from entering EQ12 workspace

Author: EQ12 AI Development Team
Version: ASCII-FILTER 1.0
Date: November 16, 2025
Location: Buffalo NY 14215 Content Empire
"""

import sys
import re
from ascii_safety import enforce_ascii, sanitize_string, ascii_safe_print

def clean_to_ascii(text):
    """
    Convert any text to pure ASCII
    Replaces common Unicode characters with ASCII equivalents
    """
    if not text:
        return ""

    # Unicode to ASCII replacement mappings
    unicode_replacements = {
        # Smart quotes
        '"': '"', '"': '"',  # Left and right double quotes
        ''': "'", ''': "'",  # Left and right single quotes

        # Dashes and hyphens
        '—': '--',  # Em dash
        '–': '-',   # En dash

        # Ellipsis
        '…': '...',

        # Bullets and symbols
        '•': '-',   # Bullet
        '◦': '-',   # White bullet
        '▪': '-',   # Black small square
        '▫': '-',   # White small square

        # Arrows
        '←': '<-',  # Left arrow
        '→': '->',  # Right arrow
        '↑': '^',   # Up arrow
        '↓': 'v',   # Down arrow

        # Mathematical symbols
        '×': 'x',   # Multiplication
        '÷': '/',   # Division
        '±': '+/-', # Plus-minus

        # Currency symbols
        '£': 'GBP', # Pound sterling
        '€': 'EUR', # Euro
        '¥': 'YEN', # Yen
        '¢': 'c',   # Cent

        # Trademark/copyright
        '™': '(TM)',
        '©': '(C)',
        '®': '(R)',

        # Degree and other symbols
        '°': 'deg',  # Degree symbol
        'α': 'alpha',
        'β': 'beta',
        'γ': 'gamma',
        'δ': 'delta',
        'θ': 'theta',
        'λ': 'lambda',
        'μ': 'mu',
        'π': 'pi',
        'σ': 'sigma',
        'τ': 'tau',
        'φ': 'phi',
        'ω': 'omega',

        # Common fractions
        '½': '1/2',
        '⅓': '1/3',
        '⅔': '2/3',
        '¼': '1/4',
        '¾': '3/4',
        '⅕': '1/5',
        '⅖': '2/5',
        '⅗': '3/5',
        '⅘': '4/5',
        '⅙': '1/6',
        '⅚': '5/6',
        '⅛': '1/8',
        '⅜': '3/8',
        '⅝': '5/8',
        '⅞': '7/8',
    }

    # Apply Unicode replacements
    for unicode_char, ascii_replacement in unicode_replacements.items():
        text = text.replace(unicode_char, ascii_replacement)

    # Remove zero-width spaces and other invisible characters
    text = re.sub(r'[\u200b-\u200f\ufeff]', '', text)

    # Force ASCII encoding - this removes any remaining non-ASCII
    text = sanitize_string(text)

    return text

def filter_code_blocks(text):
    """
    Ensure all code blocks are properly formatted and ASCII-safe
    """
    if not text:
        return ""

    # Find and clean code blocks
    code_block_pattern = r'```([a-z]*)\n(.*?)```'

    def clean_code_block(match):
        language = match.group(1) or ''
        code = match.group(2) or ''

        # Clean the code content
        clean_code = clean_to_ascii(code)

        # Ensure proper formatting
        return f"```{language}\n{clean_code}```"

    # Replace all code blocks with cleaned versions
    text = re.sub(code_block_pattern, clean_code_block, text, flags=re.DOTALL)

    return text

def filter_json_blocks(text):
    """
    Ensure JSON blocks are properly formatted and ASCII-safe
    """
    if not text:
        return ""

    import json

    # Find JSON-like structures and validate them
    json_pattern = r'\{[^{}]*\}'

    def validate_json(match):
        json_text = match.group(0)
        try:
            # Try to parse as JSON
            parsed = json.loads(json_text)
            # Re-serialize to ensure proper formatting
            return json.dumps(parsed, separators=(',', ':'), ensure_ascii=True)
        except:
            # If not valid JSON, just clean the text
            return clean_to_ascii(json_text)

    # Apply JSON validation and cleaning
    text = re.sub(json_pattern, validate_json, text)

    return text

def filter_stdin():
    """
    Read from stdin, filter to ASCII, and output
    """
    try:
        # Read all input
        input_text = sys.stdin.read()

        # Apply all filters
        filtered_text = clean_to_ascii(input_text)
        filtered_text = filter_code_blocks(filtered_text)
        filtered_text = filter_json_blocks(filtered_text)

        # Output cleaned text
        ascii_safe_print(filtered_text)

        return True

    except Exception as e:
        ascii_safe_print(f"ASCII Filter Error: {sanitize_string(str(e))}")
        return False

def filter_file(input_file, output_file=None):
    """
    Filter a file to ASCII-safe content
    """
    try:
        # Read input file
        with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
            input_text = f.read()

        # Apply filters
        filtered_text = clean_to_ascii(input_text)
        filtered_text = filter_code_blocks(filtered_text)
        filtered_text = filter_json_blocks(filtered_text)

        # Write output
        output_path = output_file or input_file
        with open(output_path, 'w', encoding='ascii', errors='replace') as f:
            f.write(filtered_text)

        ascii_safe_print(f"Filtered: {input_file} -> {output_path}")
        return True

    except Exception as e:
        ascii_safe_print(f"File Filter Error: {sanitize_string(str(e))}")
        return False

def main():
    """
    Main ASCII filter entry point
    """
    enforce_ascii()

    if len(sys.argv) == 1:
        # No arguments - filter stdin
        ascii_safe_print("EQ12 ASCII Filter - Processing stdin...")
        success = filter_stdin()

    elif len(sys.argv) == 2:
        # One argument - filter file in place
        input_file = sys.argv[1]
        ascii_safe_print(f"EQ12 ASCII Filter - Processing file: {input_file}")
        success = filter_file(input_file)

    elif len(sys.argv) == 3:
        # Two arguments - filter input file to output file
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        ascii_safe_print(f"EQ12 ASCII Filter - Processing: {input_file} -> {output_file}")
        success = filter_file(input_file, output_file)

    else:
        ascii_safe_print("Usage:")
        ascii_safe_print("  python ascii_filter.py < input.txt > output.txt  # Filter stdin")
        ascii_safe_print("  python ascii_filter.py file.txt                   # Filter file in-place")
        ascii_safe_print("  python ascii_filter.py input.txt output.txt      # Filter to new file")
        ascii_safe_print("")
        ascii_safe_print("Examples:")
        ascii_safe_print('  echo "Smart quotes test" | python ascii_filter.py')
        ascii_safe_print('  python ascii_filter.py corrupted_script.py')
        ascii_safe_print('  copilot-output | python ascii_filter.py')
        return 1

    return 0 if success else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        ascii_safe_print("ASCII Filter interrupted by user")
        sys.exit(130)
    except Exception as e:
        ascii_safe_print(f"Unexpected ASCII Filter error: {sanitize_string(str(e))}")
        sys.exit(1)
