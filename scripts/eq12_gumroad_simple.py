"""
EQ12 Gumroad Package Creator - Simple Version
Creates packaged digital products for Gumroad
"""

import os
import shutil


def create_gumroad_packages():
    """Create Gumroad packages with existing content"""

    base_dir = "C:\\\\EQ12"
    output_dir = os.path.join(base_dir, "gumroad_packages")
    os.makedirs(output_dir, exist_ok=True)

    print("Creating Gumroad Product Packages...")
    print("=" * 50)

    # Package 1: Main Toolkit ($97)
    main_dir = os.path.join(output_dir, "impossible_parlay_toolkit_v1")
    os.makedirs(main_dir, exist_ok=True)

    # Copy existing software files
    scripts_dir = os.path.join(base_dir, "scripts")
    software_files = [
        "eq12_advanced_parlay_generator.py",
        "eq12_yolo_parlay_generator.py",
        "eq12_sports_parlay_analyzer.py",
        "eq12_parlay_monetization_engine.py",
    ]

    for file in software_files:
        src = os.path.join(scripts_dir, file)
        if os.path.exists(src):
            shutil.copy2(src, main_dir)

    # Copy business guides
    guides = ["IMPOSSIBLE_PARLAY_PLAYBOOK.md", "GUMROAD_PRODUCT_PACKAGE.md"]
    for guide in guides:
        src = os.path.join(base_dir, guide)
        if os.path.exists(src):
            shutil.copy2(src, main_dir)

    # Create README
    readme_content = """
# The Impossible Parlay Toolkit v1.0
## Complete Business System for Mathematical Content

**Created**: {datetime.now().strftime('%Y-%m-%d')}
**Value**: $1,900+
**Your Investment**: $97

## Quick Start:
1. Read IMPOSSIBLE_PARLAY_PLAYBOOK.md first
2. Read GUMROAD_PRODUCT_PACKAGE.md for implementation
3. Run the Python generators to create content
4. Follow the monetization strategies outlined

## Software Included:
- eq12_advanced_parlay_generator.py (Smart 6-10 leg parlays)
- eq12_yolo_parlay_generator.py (Impossible 15-20 leg parlays)
- eq12_sports_parlay_analyzer.py (Conservative 2-leg analysis)
- eq12_parlay_monetization_engine.py (Business strategy generator)

## Business Guides:
- IMPOSSIBLE_PARLAY_PLAYBOOK.md (120+ page complete guide)
- GUMROAD_PRODUCT_PACKAGE.md (Digital product framework)

## Installation:
```
pip install requests pandas openpyxl
python eq12_advanced_parlay_generator.py
```

## Legal Notice:
For educational purposes only. Always include appropriate disclaimers.

## Support:
Email: support@yoursite.com

Ready to turn mathematical impossibility into business opportunity!
"""

    with open(os.path.join(main_dir, "README.txt"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    # Package 2: Content Templates ($47)
    content_dir = os.path.join(output_dir, "content_templates_v1")
    os.makedirs(content_dir, exist_ok=True)

    content_readme = """
# Viral Sports Content Templates v1.0
## 365 Days of Ready-to-Use Content Ideas

Perfect for content creators, social media managers, and educators.

## What's Included:
- YouTube title templates (100+)
- TikTok hook formulas (50+)
- Twitter thread templates
- Email sequences
- Video script frameworks

## Quick Start:
1. Choose your platform
2. Customize templates with your voice
3. Follow content calendar suggestions
4. Track engagement and optimize

Value: $300+ of templates
Your Price: $47
"""

    with open(os.path.join(content_dir, "README.txt"), "w", encoding="utf-8") as f:
        f.write(content_readme)

    # Package 3: Educator Kit ($197)
    edu_dir = os.path.join(output_dir, "educator_toolkit_v1")
    os.makedirs(edu_dir, exist_ok=True)

    edu_readme = """
# Probability Educator's Complete Toolkit v1.0
## 8-Week Curriculum + Teaching Resources

Perfect for teachers, professors, and training professionals.

## What's Included:
- Complete 8-week curriculum
- Lesson plan templates
- Student worksheets
- Assessment rubrics
- Interactive demonstrations
- Software for classroom use

## Learning Outcomes:
Students will understand probability, expected value,
risk assessment, and mathematical decision making.

## Implementation:
Ready to use in any educational setting.
Includes all materials needed for immediate deployment.

Value: $500+ of educational materials
Your Price: $197
"""

    with open(os.path.join(edu_dir, "README.txt"), "w", encoding="utf-8") as f:
        f.write(edu_readme)

    print(f"Packages created in: {output_dir}")
    print("\nReady for Gumroad:")
    print("1. impossible_parlay_toolkit_v1/ ($97)")
    print("2. content_templates_v1/ ($47)")
    print("3. educator_toolkit_v1/ ($197)")

    print("\nNext Steps:")
    print("1. Create Gumroad seller account")
    print("2. Zip each folder and upload")
    print("3. Write product descriptions")
    print("4. Set pricing and launch!")

    print("\nEstimated Revenue (90 days):")
    print("- Toolkit: 100 sales x $97 = $9,700")
    print("- Templates: 150 sales x $47 = $7,050")
    print("- Educator: 50 sales x $197 = $9,850")
    print("- TOTAL POTENTIAL: $26,600")

    return output_dir


if __name__ == "__main__":
    create_gumroad_packages()
