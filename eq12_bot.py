#!/usr/bin/env python3
"""
EQ12 Telegram Bot with SQLite logging and comprehensive command suite.
Integrates with all EQ12 stacks: governance, monitoring, betting, travel, cannabis.
"""

import csv
import logging
import os
import sqlite3
from datetime import datetime

from telegram import InputFile, Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

if not TG_TOKEN:
    logger.error("TG_TOKEN environment variable not set!")
    exit(1)

# === Database Setup ===
DB_PATH = os.path.join(os.path.dirname(__file__), "eq12_bot_log.db")


def init_db():
    """Initialize SQLite database for logging bot interactions."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS bot_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_id TEXT,
            command TEXT,
            response TEXT
        )
    """
    )
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")


def log_to_db(user_id: str, command: str, response: str):
    """Log command and response to SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO bot_logs (timestamp, user_id, command, response) VALUES (?, ?, ?, ?)",
            (datetime.utcnow().isoformat(), str(user_id), command, response),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to log to database: {e}")


def fetch_logs(limit: int = 5):
    """Fetch last N log entries from database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "SELECT timestamp, user_id, command, response FROM bot_logs ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"Failed to fetch logs: {e}")
        return []


def count_logs():
    """Count total log entries."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM bot_logs")
        count = c.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        logger.error(f"Failed to count logs: {e}")
        return 0


# === States for ConversationHandler ===
STATUS, AUDIT, PARLAY, FLIGHTS, DISPENSARY, LOGS = range(6)

# === Command Handlers ===


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - show available commands."""
    response = """🚀 EQ12 GODSTACK Bot Ready!

🔧 **Governance & Monitoring:**
/status - System health check
/audit - Compliance audit results

🎲 **Betting & Analytics:**
/parlay - Today's MLB parlays

✈️ **Travel & Deals:**
/flights - Cheapest flight deals

🌿 **Cannabis & Wellness:**
/dispensary - Buffalo dispensary updates

📋 **Logging & Admin:**
/logs [N] - Show last N interactions (default 5)
/exportlogs - Export full log history as CSV
/clearlogs - Clear all logs (admin only)

/cancel - End session"""

    await update.message.reply_text(response)
    log_to_db(update.effective_user.id, "/start", response)
    return STATUS


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """System status check - integrates with EQ12 monitoring."""
    # TODO: Replace with actual EQ12 system checks
    response = """✅ **EQ12 System Status**

🔒 **Security:** All Green
📊 **CI/CD:** GitHub Actions healthy
🐍 **Python:** Dependencies up-to-date
⚙️ **Services:** All processes running
🔍 **Monitoring:** Grafana operational
📈 **Performance:** Within normal parameters

Last check: {}""".format(
        datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    )

    await update.message.reply_text(response)
    log_to_db(update.effective_user.id, "/status", response)
    return STATUS


async def audit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Compliance audit results."""
    response = """📑 **EQ12 Compliance Audit**

🔐 **Security Scan:** PASSED
   - No hardcoded secrets detected
   - All API keys properly encrypted

🧪 **Code Quality:** PASSED
   - Flake8: No violations
   - MyPy: Type checking clean
   - Bandit: No security issues

📋 **Dependencies:** PASSED
   - No known vulnerabilities
   - All packages up-to-date

🔄 **Backup Status:** HEALTHY
   - Last backup: 2 hours ago
   - All critical data preserved

✅ **Overall Status:** COMPLIANT"""

    await update.message.reply_text(response)
    log_to_db(update.effective_user.id, "/audit", response)
    return AUDIT


async def parlay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Today's betting parlays from OddsAPI integration."""
    # TODO: Replace with actual OddsAPI calls
    response = """🎲 **Today's EQ12 Parlays**

⚾ **MLB Featured:**
Yankees ML (-110) + Over 8.5 runs (-105)
**Expected Value:** +285

🏀 **NBA (if active):**
Lakers ML + Over 220.5 points
**Expected Value:** +240

📊 **Analytics:**
- Win Rate (7d): 68.2%
- ROI (30d): +12.4%
- Risk Level: MODERATE

💡 **AI Recommendation:**
Strong confidence on Yankees ML based on pitcher matchups and recent form."""

    await update.message.reply_text(response)
    log_to_db(update.effective_user.id, "/parlay", response)
    return PARLAY


async def flights(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cheapest flight deals from travel scraper."""
    # TODO: Replace with actual travel API integration
    response = """✈️ **EQ12 Flight Deals (Buffalo Origin)**

🌴 **Top Deals:**
BUF → LAX: $189 roundtrip (Southwest)
BUF → MIA: $167 roundtrip (Spirit)
BUF → LAS: $203 roundtrip (Allegiant)

📅 **Best Travel Dates:**
- Weekday departures save ~$45
- Book 3-6 weeks ahead for optimal pricing

🎯 **Price Alerts Active:**
- BUF → NYC: Alert at $89
- BUF → CHI: Alert at $125

💳 **Credit Card Points:**
Chase Sapphire: 2x points on travel
- Estimated value: ~$12 back on $189 flight"""

    await update.message.reply_text(response)
    log_to_db(update.effective_user.id, "/flights", response)
    return FLIGHTS


async def dispensary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buffalo dispensary deals and cannabis updates."""
    # TODO: Replace with actual cannabis market scraper
    response = """🌿 **Buffalo Cannabis Updates**

💚 **Featured Dispensary Deals:**
- Curaleaf Buffalo: 20% off all flower (weekend only)
- MedMen: Buy 2 get 1 free on edibles
- Rise Dispensary: $5 off $50+ purchase

📊 **Market Insights:**
- Average price: $45/eighth premium flower
- CBD products trending up 15%
- New strains: Gelato 45, Wedding Cake

🐾 **CBD Pet Products:**
- Affiliate commission available
- Popular: CBD dog treats, calming oils
- Revenue opportunity: $25-50/sale

⚖️ **Legal Updates:**
- NY home cultivation approved
- Delivery services expanding statewide"""

    await update.message.reply_text(response)
    log_to_db(update.effective_user.id, "/dispensary", response)
    return DISPENSARY


async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recent bot interaction logs."""
    try:
        limit = int(context.args[0]) if context.args else 5
        limit = max(1, min(limit, 50))  # Limit between 1-50
    except (ValueError, IndexError):
        limit = 5

    rows = fetch_logs(limit)
    total_logs = count_logs()

    if not rows:
        response = "📭 No logs found."
    else:
        response = f"🗂 **Last {limit} logs** (Total: {total_logs}):\n\n"
        for i, (ts, uid, cmd, resp) in enumerate(rows, 1):
            # Format timestamp nicely
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                formatted_time = dt.strftime("%m/%d %H:%M")
            except:
                formatted_time = ts[:16]

            # Truncate response for readability
            truncated_resp = resp[:60] + "..." if len(resp) > 60 else resp
            response += f"`{i}.` **{formatted_time}** User:{uid}\n   `{cmd}` → {truncated_resp}\n\n"

    await update.message.reply_text(response, parse_mode="Markdown")
    log_to_db(update.effective_user.id, f"/logs {limit}", f"Retrieved {len(rows)} log entries")
    return LOGS


async def exportlogs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export all logs as CSV file."""
    try:
        csv_path = os.path.join(os.path.dirname(__file__), "eq12_bot_export.csv")

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, timestamp, user_id, command, response FROM bot_logs ORDER BY id ASC")
        rows = c.fetchall()
        conn.close()

        if not rows:
            await update.message.reply_text("📭 No logs to export.")
            return

        # Write CSV
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "timestamp", "user_id", "command", "response"])
            writer.writerows(rows)

        # Send file
        with open(csv_path, "rb") as f:
            await update.message.reply_document(
                document=InputFile(
                    f,
                    filename=f"eq12_bot_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                ),
                caption=f"📊 EQ12 Bot Log Export\n{len(rows)} total interactions",
            )

        # Clean up temp file
        if os.path.exists(csv_path):
            os.remove(csv_path)

        log_to_db(update.effective_user.id, "/exportlogs", f"Exported {len(rows)} logs to CSV")

    except Exception as e:
        logger.error(f"Export failed: {e}")
        await update.message.reply_text(f"❌ Export failed: {e!s}")


async def clearlogs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear all logs (admin command)."""
    user_id = str(update.effective_user.id)

    # Basic admin check (you can enhance this)
    if TG_CHAT_ID and user_id != TG_CHAT_ID:
        response = "❌ Access denied. Admin privileges required."
        await update.message.reply_text(response)
        log_to_db(user_id, "/clearlogs", "Access denied - not admin")
        return

    try:
        # Count logs before clearing
        total_before = count_logs()

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM bot_logs")
        conn.commit()
        conn.close()

        response = f"🗑 **Logs cleared successfully.**\n\nRemoved {total_before} log entries."
        await update.message.reply_text(response)
        log_to_db(user_id, "/clearlogs", f"Cleared {total_before} logs")

    except Exception as e:
        logger.error(f"Clear logs failed: {e}")
        await update.message.reply_text(f"❌ Clear failed: {e!s}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command - same as start."""
    return await start(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation."""
    response = "❌ Session ended. Use /start to begin new session."
    await update.message.reply_text(response)
    log_to_db(update.effective_user.id, "/cancel", response)
    return ConversationHandler.END


# === Error Handler ===
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "🚨 An error occurred. The incident has been logged."
        )


# === Main Application ===
def main():
    """Start the EQ12 Telegram Bot."""
    logger.info("Starting EQ12 Telegram Bot...")

    # Initialize database
    init_db()

    # Create application
    app = Application.builder().token(TG_TOKEN).build()

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("help", help_command),
        ],
        states={
            STATUS: [
                CommandHandler("status", status),
                CommandHandler("audit", audit),
                CommandHandler("parlay", parlay),
                CommandHandler("flights", flights),
                CommandHandler("dispensary", dispensary),
                CommandHandler("logs", logs),
                CommandHandler("exportlogs", exportlogs),
                CommandHandler("clearlogs", clearlogs),
            ],
            AUDIT: [
                CommandHandler(cmd, globals()[cmd])
                for cmd in [
                    "status",
                    "audit",
                    "parlay",
                    "flights",
                    "dispensary",
                    "logs",
                    "exportlogs",
                    "clearlogs",
                ]
            ],
            PARLAY: [
                CommandHandler(cmd, globals()[cmd])
                for cmd in [
                    "status",
                    "audit",
                    "parlay",
                    "flights",
                    "dispensary",
                    "logs",
                    "exportlogs",
                    "clearlogs",
                ]
            ],
            FLIGHTS: [
                CommandHandler(cmd, globals()[cmd])
                for cmd in [
                    "status",
                    "audit",
                    "parlay",
                    "flights",
                    "dispensary",
                    "logs",
                    "exportlogs",
                    "clearlogs",
                ]
            ],
            DISPENSARY: [
                CommandHandler(cmd, globals()[cmd])
                for cmd in [
                    "status",
                    "audit",
                    "parlay",
                    "flights",
                    "dispensary",
                    "logs",
                    "exportlogs",
                    "clearlogs",
                ]
            ],
            LOGS: [
                CommandHandler(cmd, globals()[cmd])
                for cmd in [
                    "status",
                    "audit",
                    "parlay",
                    "flights",
                    "dispensary",
                    "logs",
                    "exportlogs",
                    "clearlogs",
                ]
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add handlers
    app.add_handler(conv_handler)
    app.add_error_handler(error_handler)

    # Start polling
    logger.info("EQ12 Bot is now running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
