#!/usr/bin/env python3
"""
EQ12 Cookbook Search - Cross-Platform Keyword Search

Simple grep-like search across the entire EQ12 Master Cookbook.
Optimized for Windows console compatibility.

Usage:
    python eq12_cookbook_search.py <keyword>

Examples:
    python eq12_cookbook_search.py pytest
    python eq12_cookbook_search.py fastapi
    python eq12_cookbook_search.py wireguard
    python eq12_cookbook_search.py "monte carlo"
"""

import os
import re
import sys

# Support both new and legacy cookbook names
COOKBOOK_PATHS = [
    os.path.join(os.path.dirname(__file__), "EQ12_COPILOT_COOKBOOK.md"),
    os.path.join(os.path.dirname(__file__), "EQ12_Master_Cookbook.md"),
]


class EQ12CookbookSearch:
    def __init__(self):
        self.cookbook_file = None

        # Find the cookbook file
        for path in COOKBOOK_PATHS:
            if os.path.exists(path):
                self.cookbook_file = path
                break

        if not self.cookbook_file:
            print("Error: Cookbook file not found!")
            print("Looking for:")
            for path in COOKBOOK_PATHS:
                print(f"  - {path}")
            sys.exit(1)

    def search_cookbook(self, keyword, max_results=15):
        """Search cookbook with enhanced formatting"""
        if not self.cookbook_file:
            print("Error: No cookbook file available")
            return

        try:
            with open(self.cookbook_file, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading cookbook: {e}")
            return

        keyword_lower = keyword.lower()
        matches = []
        current_section = "Unknown"

        for line_num, line in enumerate(lines, 1):
            line_clean = line.strip()

            # Track current section
            if line_clean.startswith("## ") and ("️⃣" in line_clean or "Patterns" in line_clean):
                section_match = re.search(r"## (?:\d+️⃣\s*)?([^#\n]+)", line_clean)
                if section_match:
                    current_section = section_match.group(1).strip()
                    current_section = current_section.replace("Patterns", "").strip()

            # Search for keyword
            if keyword_lower in line.lower():
                # Clean up Unicode for console display
                display_line = line_clean
                display_line = re.sub(r"[^\x00-\x7F]", "", display_line)  # Remove non-ASCII

                if display_line.strip():  # Only non-empty lines
                    match_type = (
                        "CODE"
                        if any(
                            pattern in display_line
                            for pattern in [
                                "def ",
                                "function",
                                "class ",
                                "```",
                                "$",
                                "powershell",
                                "bash",
                            ]
                        )
                        else "TEXT"
                    )

                    matches.append(
                        {
                            "line_num": line_num,
                            "section": current_section,
                            "line": display_line[:100],  # Truncate
                            "type": match_type,
                        }
                    )

                    if len(matches) >= max_results:
                        break

        self.display_results(matches, keyword)

    def display_results(self, matches, keyword):
        """Display formatted search results"""
        if not matches:
            print(f"No matches found for '{keyword}'")
            print()
            print("Try searching for:")
            print("  python, fastapi, pytest, wireguard, parlay")
            print("  powershell, bash, devops, security, data")
            return

        print(f"=== Found {len(matches)} matches for '{keyword}' ===")
        print()

        current_section = None
        for i, match in enumerate(matches, 1):
            section = match["section"]

            # Print section header when changed
            if section != current_section:
                if current_section:
                    print()
                print(f"--- {section} ---")
                current_section = section

            # Print match
            type_indicator = f"[{match['type']}]"
            print(f"{i:2d}. Line {match['line_num']:4d} {type_indicator:6s} {match['line']}")

        print()
        print(f"Search complete - {len(matches)} results from EQ12 Cookbook")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    keyword = " ".join(sys.argv[1:])
    search = EQ12CookbookSearch()
    search.search_cookbook(keyword)


if __name__ == "__main__":
    main()
