import ast


def check_syntax(filename):
    try:
        with open(filename, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        ast.parse(content)
        print(f"✅ {filename}: No syntax errors")
        return True
    except SyntaxError as e:
        print(f"❌ {filename}: Line {e.lineno}: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ {filename}: Error reading file: {e}")
        return False


files = [
    "cfb_dk_boost_optimizer.py",
    "eq12_copilot_triggers_fixed.py",
    "eq12_telegram_master_bot.py",
    "eq12_vbnet_copilot_assistant.py",
    "EdgeGodParlays/ai_betting_bot_stealth_final_flask_pro.py",
    "generated_projects/EQ12SystemMonitor/eq12systemmonitor.py",
]

for f in files:
    check_syntax(f)
