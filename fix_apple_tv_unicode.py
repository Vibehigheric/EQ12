#!/usr/bin/env python3
"""
EQ12 Apple TV Unicode Fix Script

Replaces all emoji characters in logging with safe ASCII alternatives
to prevent UnicodeEncodeError on Windows console.
"""

from pathlib import Path


def fix_unicode_in_file(filepath):
    """Replace emoji characters with text equivalents in a file"""

    # Emoji mappings to ASCII-safe alternatives
    emoji_replacements = {
        "🚀": "[LAUNCH]",
        "✅": "[SUCCESS]",
        "❌": "[ERROR]",
        "⚠️": "[WARNING]",
        "🔍": "[SEARCH]",
        "🎯": "[TARGET]",
        "🔄": "[REFRESH]",
        "🏥": "[HEALTH]",
        "📊": "[CHART]",
        "📈": "[METRICS]",
        "📺": "[TV]",
        "🎬": "[STREAM]",
        "📱": "[TELEGRAM]",
        "🏠": "[HOME]",
        "⏱️": "[TIME]",
        "🌐": "[WEB]",
        "🔌": "[SOCKET]",
        "🎉": "[READY]",
        "🔗": "[LINK]",
        "📄": "[FILE]",
        "⚡": "[POWER]",
        "🖥️": "[DISPLAY]",
        "📅": "[SCHEDULE]",
        "🛠️": "[TOOL]",
    }

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Replace each emoji
        modified = False
        for emoji, replacement in emoji_replacements.items():
            if emoji in content:
                content = content.replace(emoji, replacement)
                modified = True
                print(f"  Replaced '{emoji}' with '{replacement}' in {filepath.name}")

        # Write back if modified
        if modified:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  ✓ Fixed {filepath}")

        return modified

    except Exception as e:
        print(f"  ✗ Error processing {filepath}: {e}")
        return False


def main():
    """Fix all Apple TV system files"""

    appletv_dir = Path(r"C:\EQ12\appletv_system")

    if not appletv_dir.exists():
        print(f"❌ Apple TV directory not found: {appletv_dir}")
        return

    print("🔧 Fixing Unicode issues in Apple TV system files...")

    # Files to fix
    files_to_fix = [
        "eq12_appletv_manager.py",
        "eq12_streaming_engine.py",
        "eq12_telegram_appletv_bot.py",
        "eq12_appletv_master_launcher.py",
    ]

    fixed_count = 0

    for filename in files_to_fix:
        filepath = appletv_dir / filename
        if filepath.exists():
            print(f"\nProcessing {filename}...")
            if fix_unicode_in_file(filepath):
                fixed_count += 1
        else:
            print(f"⚠️ File not found: {filename}")

    print(f"\n✅ Unicode fix complete! Fixed {fixed_count} files.")
    print("\nNext steps:")
    print("1. Install correct dependencies: pip install -r appletv_system/requirements_fixed.txt")
    print("2. Test with: cd appletv_system && python eq12_appletv_master_launcher.py")


if __name__ == "__main__":
    main()
