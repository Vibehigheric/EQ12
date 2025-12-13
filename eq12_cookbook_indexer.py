#!/usr/bin/env python3
"""
EQ12 Cookbook Indexer - Quick Section Access

Simple command-line tool for accessing specific cookbook sections by name.
Designed for rapid access to cookbook sections without complex search.

Usage:
    python eq12_cookbook_indexer.py <section_name>

Examples:
    python eq12_cookbook_indexer.py python
    python eq12_cookbook_indexer.py powershell
    python eq12_cookbook_indexer.py testing
    python eq12_cookbook_indexer.py security
    python eq12_cookbook_indexer.py list  # Show all sections

Section Names:
    - python        → Python Bots & Automation
    - powershell    → PowerShell (Windows)
    - bash          → Bash/Linux
    - c#            → C#/Visual Studio
    - devops        → DevOps/CI-CD
    - prompts       → GPT-5/AI Integration
    - security      → Security/Networking
    - data          → Data Engineering/Analysis
    - media         → Media/Content Generation
    - marketplace   → Marketplace/Affiliate
    - testing       → Testing & QA
"""

import re
import sys
from pathlib import Path


class EQ12CookbookIndexer:
    """Simplified cookbook section access"""

    def __init__(self, cookbook_path: str | None = None):
        self.eq12_home = Path("C:/EQ12" if sys.platform == "win32" else "/opt/eq12")
        self.cookbook_path = Path(cookbook_path or self.eq12_home / "EQ12_COPILOT_COOKBOOK.md")

        # Section name mappings for user-friendly access
        self.section_aliases = {
            "python": ["python", "bot", "bots", "automation"],
            "powershell": ["powershell", "windows", "ps1", "pwsh"],
            "bash": ["bash", "linux", "shell", "sh"],
            "c#": ["c#", "csharp", "dotnet", ".net", "visual_studio"],
            "devops": ["devops", "ci", "cd", "github", "actions"],
            "prompts": ["prompts", "gpt", "ai", "gpt-5", "openai"],
            "security": ["security", "networking", "vpn", "firewall"],
            "data": ["data", "analysis", "pandas", "sql", "database"],
            "media": ["media", "content", "ffmpeg", "video", "audio"],
            "marketplace": ["marketplace", "affiliate", "commerce", "e-commerce"],
            "testing": ["testing", "qa", "pytest", "test", "quality"],
        }

        self.sections = self._load_sections()

    def _load_sections(self) -> dict[str, str]:
        """Load cookbook sections into memory"""
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
                    sections[current_section] = "\n".join(current_content)

                current_section = self._extract_section_key(line)
                current_content = [line]
            elif current_section:
                current_content.append(line)

        # Add last section
        if current_section:
            sections[current_section] = "\n".join(current_content)

        return sections

    def _extract_section_key(self, line: str) -> str:
        """Extract section key from header"""
        # Remove emoji and numbers, clean up
        name = re.sub(r"^## \d+️⃣\s*", "", line)
        name = re.sub(r"\s+Patterns?$", "", name)

        # Map to standard key
        name_lower = name.lower()
        if "python" in name_lower or "bot" in name_lower:
            return "python"
        if "powershell" in name_lower or "windows" in name_lower:
            return "powershell"
        if "bash" in name_lower or "linux" in name_lower:
            return "bash"
        if "c#" in name_lower or "visual studio" in name_lower:
            return "c#"
        if "devops" in name_lower or "ci" in name_lower:
            return "devops"
        if "gpt" in name_lower or "ai" in name_lower:
            return "prompts"
        if "security" in name_lower or "networking" in name_lower:
            return "security"
        if "data" in name_lower or "analysis" in name_lower:
            return "data"
        if "media" in name_lower or "content" in name_lower:
            return "media"
        if "marketplace" in name_lower or "affiliate" in name_lower:
            return "marketplace"
        if "testing" in name_lower or "qa" in name_lower:
            return "testing"
        return name.lower().replace(" ", "_").replace("/", "_")

    def resolve_section(self, query: str) -> str:
        """Resolve user input to section key"""
        query = query.lower().strip()

        # Direct match
        if query in self.sections:
            return query

        # Check aliases
        for section, aliases in self.section_aliases.items():
            if query in aliases:
                return section

        # Partial match
        for section in self.sections:
            if query in section or section in query:
                return section

        return None

    def get_section(self, section_name: str) -> None:
        """Get and display specific cookbook section"""
        section_key = self.resolve_section(section_name)

        if not section_key or section_key not in self.sections:
            print(f"Section '{section_name}' not found.")
            print("\\nAvailable sections:")
            self.list_sections()
            return

        content = self.sections[section_key]

        title = f"EQ12 Cookbook: {section_key.replace('_', ' ').title()}"
        print(title)
        print("=" * 60)
        print(content)
        print("=" * 60)
        print(f"End of {section_key.replace('_', ' ').title()} section")

    def list_sections(self) -> None:
        """List all available sections"""
        print("EQ12 Cookbook Sections:")
        print()

        for i, (section, aliases) in enumerate(self.section_aliases.items(), 1):
            if section in self.sections:
                print(f"{i:2d}. {section.ljust(12)} -> {section.replace('_', ' ').title()}")
                print(f"     Aliases: {', '.join(aliases[:3])}")
                print()

        print("Usage: python eq12_cookbook_indexer.py <section_name>")
        print("Example: python eq12_cookbook_indexer.py python")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    indexer = EQ12CookbookIndexer()
    section_name = sys.argv[1]

    if section_name.lower() in ("list", "ls", "--list", "-l"):
        indexer.list_sections()
    else:
        indexer.get_section(section_name)


if __name__ == "__main__":
    main()
