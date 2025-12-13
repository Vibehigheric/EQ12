#!/usr/bin/env python3
"""
EQ12 Cookbook Query Tool

Quick command-line access to cookbook sections and patterns.
Usage: python eq12_cookbook_query.py [section] [pattern]

Examples:
  python eq12_cookbook_query.py python fastapi
  python eq12_cookbook_query.py security wireguard
  python eq12_cookbook_query.py testing pytest
  python eq12_cookbook_query.py --list-sections
"""

import re
import sys
from pathlib import Path
from typing import Any


class EQ12CookbookQuery:
    def __init__(self, cookbook_path: str | None = None):
        self.eq12_home = Path("C:/EQ12" if sys.platform == "win32" else "/opt/eq12")
        self.cookbook_path = Path(cookbook_path or self.eq12_home / "EQ12_COPILOT_COOKBOOK.md")
        self.sections = self._parse_sections()

    def _parse_sections(self) -> dict[str, dict]:
        """Parse cookbook into searchable sections"""
        if not self.cookbook_path.exists():
            print(f"❌ Cookbook not found: {self.cookbook_path}")
            return {}

        with open(self.cookbook_path, encoding="utf-8") as f:
            content = f.read()

        sections = {}
        current_section = None
        current_content = []

        lines = content.split("\n")
        for line in lines:
            # Main sections (## N️⃣ Title)
            if re.match(r"^## \d+️⃣", line):
                if current_section:
                    sections[current_section] = {
                        "content": "\n".join(current_content),
                        "subsections": self._extract_subsections("\n".join(current_content)),
                    }

                current_section = self._extract_section_name(line)
                current_content = [line]
            elif current_section:
                current_content.append(line)

        # Add last section
        if current_section:
            sections[current_section] = {
                "content": "\n".join(current_content),
                "subsections": self._extract_subsections("\n".join(current_content)),
            }

        return sections

    def _extract_section_name(self, line: str) -> str:
        """Extract clean section name from header"""
        # Remove emoji and numbers, clean up
        name = re.sub(r"^## \d+️⃣\s*", "", line)
        name = re.sub(r"\s+Patterns?$", "", name)
        return name.lower().replace(" & ", "_").replace(" ", "_").replace("/", "_")

    def _extract_subsections(self, content: str) -> dict[str, str]:
        """Extract subsections and code blocks from content"""
        subsections = {}
        lines = content.split("\n")
        current_sub = None
        current_content = []

        for line in lines:
            if line.startswith("### "):
                if current_sub:
                    subsections[current_sub] = "\n".join(current_content)

                current_sub = line.replace("### ", "").replace("**", "").lower().replace(" ", "_")
                current_content = [line]
            elif current_sub:
                current_content.append(line)

        if current_sub:
            subsections[current_sub] = "\n".join(current_content)

        return subsections

    def list_sections(self) -> None:
        """List all available sections"""
        print("📚 EQ12 Cookbook Sections:\n")

        for i, section in enumerate(self.sections.keys(), 1):
            print(f"{i:2d}. {section.replace('_', ' ').title()}")

            # Show subsections
            subsections = list(self.sections[section]["subsections"].keys())
            if subsections:
                for sub in subsections[:3]:  # Show first 3
                    print(f"     • {sub.replace('_', ' ')}")
                if len(subsections) > 3:
                    print(f"     • ... and {len(subsections) - 3} more")
            print()

    def search_section(self, section_name: str, pattern: str | None = None) -> None:
        """Search for specific section and optional pattern"""
        # Fuzzy match section name
        matched_section = self._fuzzy_match_section(section_name)

        if not matched_section:
            print(f"❌ Section '{section_name}' not found.")
            print("Available sections:")
            self.list_sections()
            return

        section_data = self.sections[matched_section]

        if pattern:
            # Search within subsections
            matching_subs = self._search_subsections(section_data["subsections"], pattern)

            if matching_subs:
                print(
                    f"🎯 Found {len(matching_subs)} matches in '{matched_section.replace('_', ' ').title()}':\n"
                )
                for sub_name, sub_content in matching_subs.items():
                    print(f"{'=' * 60}")
                    print(f"📝 {sub_name.replace('_', ' ').title()}")
                    print("=" * 60)
                    print(sub_content[:2000])  # Limit output
                    if len(sub_content) > 2000:
                        print("\n... (truncated)")
                    print()
            else:
                print(f"❌ Pattern '{pattern}' not found in section '{matched_section}'")
        else:
            # Show entire section
            print(f"📚 {matched_section.replace('_', ' ').title()}")
            print("=" * 60)
            print(section_data["content"][:3000])  # Limit output
            if len(section_data["content"]) > 3000:
                print("\n... (truncated - use specific pattern to see more)")

    def _fuzzy_match_section(self, query: str) -> str | None:
        """Find best matching section name"""
        query = query.lower().replace(" ", "_")

        # Exact match first
        if query in self.sections:
            return query

        # Partial matches
        matches = [s for s in self.sections if query in s or s in query]

        if matches:
            return matches[0]  # Return first match

        # Keyword matching
        query_words = query.split("_")
        for section in self.sections:
            section_words = section.split("_")
            if any(word in section_words for word in query_words):
                return section

        return None

    def _search_subsections(self, subsections: dict[str, str], pattern: str) -> dict[str, str]:
        """Search for pattern within subsections"""
        pattern = pattern.lower()
        matches = {}

        for sub_name, sub_content in subsections.items():
            if pattern in sub_name.lower() or pattern in sub_content.lower():
                matches[sub_name] = sub_content

        return matches

    def keyword_search(self, query: str, section_filter: str | None = None) -> list[dict[str, Any]]:
        """Advanced keyword search with context and relevance scoring"""
        query_terms = [term.lower().strip() for term in query.split()]
        matches = []

        sections_to_search = (
            [section_filter]
            if section_filter and section_filter in self.sections
            else self.sections.keys()
        )

        for section_name in sections_to_search:
            section_data = self.sections[section_name]
            content_lines = section_data["content"].split("\n")

            for i, line in enumerate(content_lines):
                line_lower = line.lower()
                score = 0
                matched_terms = []

                # Score based on term matches
                for term in query_terms:
                    if term in line_lower:
                        score += 10
                        matched_terms.append(term)
                        # Extra points for exact word matches
                        if f" {term} " in f" {line_lower} ":
                            score += 5

                if score > 0:
                    # Extract context
                    start = max(0, i - 3)
                    end = min(len(content_lines), i + 4)
                    context = "\n".join(content_lines[start:end])

                    match_type = (
                        "code"
                        if line.strip().startswith(
                            (
                                "```",
                                "def ",
                                "class ",
                                "function",
                                "$",
                                "#",
                                "//",
                                "<!--",
                            )
                        )
                        else "text"
                    )

                    matches.append(
                        {
                            "section": section_name,
                            "line_number": i + 1,
                            "line": line.strip(),
                            "context": context,
                            "score": score,
                            "matched_terms": matched_terms,
                            "type": match_type,
                        }
                    )

        # Sort by relevance score
        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches

    def quick_search(self, query: str) -> None:
        """Quick search with enhanced formatting and results"""
        matches = self.keyword_search(query)

        if not matches:
            print(f"❌ No matches found for '{query}'")
            return

        print(f"🔍 Found {len(matches)} matches for '{query}':\n")

        # Group by section for better readability
        sections_with_matches = {}
        for match in matches[:10]:  # Limit to top 10 results
            section = match["section"]
            if section not in sections_with_matches:
                sections_with_matches[section] = []
            sections_with_matches[section].append(match)

        for section, section_matches in sections_with_matches.items():
            print(f"📍 {section.replace('_', ' ').title()}")
            for match in section_matches[:3]:  # Max 3 per section
                match_indicator = "💻" if match["type"] == "code" else "📝"
                print(
                    f"   {match_indicator} {match['line'][:100]}{'...' if len(match['line']) > 100 else ''}"
                )
            print()

    def search_code_snippets(self, query: str) -> None:
        """Search specifically for code patterns"""
        matches = self.keyword_search(query)
        code_matches = [m for m in matches if m["type"] == "code"]

        if not code_matches:
            print(f"❌ No code snippets found for '{query}'")
            return

        print(f"💻 Found {len(code_matches)} code snippets for '{query}':\n")
        for i, match in enumerate(code_matches[:8], 1):
            print(f"{i}. 📍 {match['section'].replace('_', ' ').title()}")
            print(f"   {match['line']}")
            if i < len(code_matches):
                print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cookbook = EQ12CookbookQuery()

    arg1 = sys.argv[1]

    if arg1 in ("--list-sections", "-l", "list"):
        cookbook.list_sections()
    elif arg1 in ("--search", "-s", "search"):
        if len(sys.argv) < 3:
            print("Usage: python eq12_cookbook_query.py --search <query>")
            return
        cookbook.quick_search(" ".join(sys.argv[2:]))
    elif arg1 in ("--code", "-c", "code"):
        if len(sys.argv) < 3:
            print("Usage: python eq12_cookbook_query.py --code <query>")
            return
        cookbook.search_code_snippets(" ".join(sys.argv[2:]))
    elif arg1 in ("--help", "-h", "help"):
        print(__doc__)
        print("\nAvailable modes:")
        print("  --list-sections, -l    List all cookbook sections")
        print("  --search, -s <query>   Search all content for keywords")
        print("  --code, -c <query>     Search specifically for code snippets")
        print("  <section> [pattern]    Search specific section (e.g. 'python fastapi')")
        print("\nExamples:")
        print("  python eq12_cookbook_query.py python fastapi")
        print("  python eq12_cookbook_query.py --search wireguard")
        print("  python eq12_cookbook_query.py --code pytest")
    else:
        section = arg1
        pattern = sys.argv[2] if len(sys.argv) > 2 else None
        cookbook.search_section(section, pattern or "")


if __name__ == "__main__":
    main()
