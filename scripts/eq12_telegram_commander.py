#!/usr/bin/env python3
"""
 EQ12 TELEGRAM INTEGRATION MODULE 
Advanced notification and alert system for parlay simulation engine

Features:
- Real-time simulation alerts with advanced metrics
- Top parlay summaries with formatted tables
- Risk category notifications
- Error alerts and system status
- Interactive command handling with parlay optimization integration
- Real-time monitoring and automated alerts
- Advanced betting intelligence notifications
"""

import os
import json
import logging
import asyncio
import time
import sqlite3
import subprocess
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass

# Telegram imports with fallback
try:
    from telegram import Bot, Update, BotCommand
    from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
    from telegram.constants import ParseMode
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    # Mock classes for development without telegram
    class Bot: pass
    class Update: pass
    class Application: pass
    class CommandHandler: pass
    class ContextTypes:
        DEFAULT_TYPE = None
    class MessageHandler: pass
    class filters: pass
    class ParseMode:
        MARKDOWN_V2 = "MarkdownV2"

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TelegramMessage:
    """Data class for telegram message logging"""
    timestamp: str
    chat_id: int
    username: str
    message_type: str
    content: str
    command: Optional[str] = None
    response: Optional[str] = None
    execution_time: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None

class EQ12TelegramCommander:
    """Main Telegram bot controller for EQ12 notifications"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.workspace = os.getenv("EQ12_WORKSPACE", "C:\\EQ12")
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")
        if not self.chat_id:
            raise ValueError("TELEGRAM_CHAT_ID environment variable not set")
        
        self.bot = Bot(token=self.bot_token)
        self.application = Application.builder().token(self.bot_token).build()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("latest", self.latest_results_command))
        self.application.add_handler(CommandHandler("top5", self.top5_parlays_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
    
    async def send_simulation_alert(self, results: Dict[str, Any]) -> bool:
        """Send comprehensive simulation completion alert with advanced metrics"""
        try:
            message = self._format_advanced_simulation_summary(results)
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            
            # Send top parlays as separate formatted message
            if results.get('optimal_parlays'):
                top_parlays_message = self._format_top_parlays_advanced(results['optimal_parlays'][:3])
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=top_parlays_message,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
            
            logger.info("Advanced simulation alert sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send simulation alert: {e}")
            return False
    
    async def send_error_alert(self, error_message: str, component: str = "Unknown") -> bool:
        """Send error notification"""
        try:
            message = f"""
 *EQ12 SYSTEM ERROR ALERT* 

*Component:* {component}
*Time:* {datetime.now().strftime('%Y\\-m\\-d %H:%M:%S')}

*Error:*
```
{error_message}
```

Please check the logs for more details\\.
"""
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            logger.info("Error alert sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send error alert: {e}")
            return False
    message_type: str
    content: str
    command: Optional[str] = None
    response: Optional[str] = None
    execution_time: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None


class EQ12TelegramCommander:
    """Complete EQ12 Telegram command and control system"""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / "data" / "telegram_activity.db"
        self.config_path = self.workspace_path / "configs" / "telegram_config.json"
        self.alerts_path = self.workspace_path / "logs" / "telegram_alerts"
        
        # Create directories
        for path in [
            self.workspace_path / "data",
            self.workspace_path / "logs" / "telegram",
            self.alerts_path
        ]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self.load_config()
        
        # Initialize database
        self.init_database()
        
        # Telegram setup
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_ids = self.load_chat_ids()
        self.authorized_users = set(self.chat_ids.get("admins", []))
        
        if not self.bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN not found in environment")
            return
        
        if not TELEGRAM_AVAILABLE:
            logger.error("Telegram library not available")
            return
        
        # Initialize bot
        self.application = None
        self.bot = None
        self.setup_bot()
        
        # Command handlers with enhanced features
        self.commands = {
            "start": self.cmd_start,
            "status": self.cmd_status,
            "health": self.cmd_health,
            "wealth": self.cmd_wealth,
            "groq": self.cmd_groq,
            "openai": self.cmd_openai,
            "parlay": self.cmd_parlay,
            "quickbet": self.cmd_quickbet,  # New quick betting analysis
            "portfolio": self.cmd_portfolio,
            "reboot": self.cmd_reboot,
            "logs": self.cmd_logs,
            "analytics": self.cmd_analytics,
            "alerts": self.cmd_alerts,
            "monitor": self.cmd_monitor,  # New monitoring command
            "help": self.cmd_help,
            "admin": self.cmd_admin,
            "api": self.cmd_api_status,  # New API status command
            "simulate": self.cmd_simulate_trade  # New trade simulation
        }
        
        logger.info("EQ12 Telegram Commander initialized")

    def load_config(self) -> Dict:
        """Load Telegram configuration"""
        default_config = {
            "alert_types": {
                "system": {"enabled": True, "priority": "high"},
                "wealth": {"enabled": True, "priority": "high"},
                "betting": {"enabled": True, "priority": "medium"},
                "ai": {"enabled": True, "priority": "low"},
                "security": {"enabled": True, "priority": "critical"}
            },
            "rate_limits": {
                "commands_per_minute": 10,
                "alerts_per_hour": 50
            },
            "auto_responses": True,
            "command_logging": True
        }
        
        try:
            if self.config_path.exists():
                with open(self.config_path) as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                # Create default config
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return default_config

    def load_chat_ids(self) -> Dict:
        """Load chat IDs from environment and config"""
        chat_ids = {
            "admins": [],
            "channels": [],
            "groups": []
        }
        
        # Primary chat ID from environment
        primary_id = os.getenv("TELEGRAM_CHAT_ID")
        if primary_id:
            try:
                chat_ids["admins"].append(int(primary_id))
            except ValueError:
                logger.error(f"Invalid TELEGRAM_CHAT_ID: {primary_id}")
        
        # Additional IDs from config file
        ids_file = self.workspace_path / "configs" / "telegram_chat_ids.json"
        if ids_file.exists():
            try:
                with open(ids_file) as f:
                    additional_ids = json.load(f)
                for key in ["admins", "channels", "groups"]:
                    if key in additional_ids:
                        chat_ids[key].extend(additional_ids[key])
            except Exception as e:
                logger.error(f"Failed to load additional chat IDs: {e}")
        
        return chat_ids

    def init_database(self):
        """Initialize SQLite database for activity logging"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS telegram_activity (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        chat_id INTEGER NOT NULL,
                        username TEXT,
                        message_type TEXT NOT NULL,
                        content TEXT,
                        command TEXT,
                        response TEXT,
                        execution_time REAL,
                        success BOOLEAN NOT NULL,
                        error_message TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS telegram_alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        alert_type TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        title TEXT NOT NULL,
                        message TEXT NOT NULL,
                        chat_ids TEXT,
                        sent BOOLEAN DEFAULT FALSE,
                        delivery_attempts INTEGER DEFAULT 0
                    )
                """)
                
                conn.commit()
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    def setup_bot(self):
        """Setup Telegram bot and application"""
        if not self.bot_token or not TELEGRAM_AVAILABLE:
            return
        
        try:
            self.application = Application.builder().token(self.bot_token).build()
            self.bot = self.application.bot
            
            # Add command handlers
            for command, handler in self.commands.items():
                self.application.add_handler(CommandHandler(command, handler))
            
            # Add message handler for non-commands
            self.application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
            )
            
            logger.info("Telegram bot setup complete")
        except Exception as e:
            logger.error(f"Bot setup failed: {e}")

    async def setup_bot_commands(self):
        """Setup bot command menu"""
        commands = [
            BotCommand("start", "Start EQ12 Commander"),
            BotCommand("status", "System status overview"),
            BotCommand("health", "Health check all modules"),
            BotCommand("wealth", "Wealth intelligence report"),
            BotCommand("groq", "Groq engine status"),
            BotCommand("openai", "OpenAI key status"),
            BotCommand("parlay", "Generate betting analysis"),
            BotCommand("portfolio", "Portfolio performance"),
            BotCommand("analytics", "Analytics dashboard"),
            BotCommand("alerts", "Alert management"),
            BotCommand("logs", "View recent logs"),
            BotCommand("help", "Command help")
        ]
        
        try:
            await self.bot.set_my_commands(commands)
            logger.info("Bot commands menu set")
        except Exception as e:
            logger.error(f"Failed to set commands: {e}")

    def log_activity(self, message: TelegramMessage):
        """Log Telegram activity to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO telegram_activity 
                    (timestamp, chat_id, username, message_type, content, 
                     command, response, execution_time, success, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    message.timestamp, message.chat_id, message.username,
                    message.message_type, message.content, message.command,
                    message.response, message.execution_time, message.success,
                    message.error_message
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")

    def is_authorized(self, chat_id: int) -> bool:
        """Check if user is authorized"""
        return chat_id in self.authorized_users

    async def send_message(self, chat_id: int, text: str, parse_mode: str = "Markdown") -> bool:
        """Send message to specific chat"""
        try:
            await self.bot.send_message(
                chat_id=chat_id, 
                text=text, 
                parse_mode=parse_mode
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            return False

    async def broadcast_message(self, text: str, target_type: str = "admins") -> int:
        """Broadcast message to multiple chats"""
        sent_count = 0
        target_ids = self.chat_ids.get(target_type, [])
        
        for chat_id in target_ids:
            if await self.send_message(chat_id, text):
                sent_count += 1
            await asyncio.sleep(0.1)  # Rate limiting
        
        return sent_count

    # Command Handlers
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        chat_id = update.effective_chat.id
        username = update.effective_user.username or "Unknown"
        
        if not self.is_authorized(chat_id):
            await update.message.reply_text(" Unauthorized access to EQ12 Commander")
            return
        
        welcome_msg = """
 **EQ12 Commander Online**

Welcome to the EQ12 Intelligence Command Center!

**Quick Commands:**
 `/status` - System overview
 `/health` - Health check
 `/wealth` - Wealth report
 `/parlay` - Betting analysis
 `/help` - All commands

Type any command to get started!
        """
        
        await update.message.reply_text(welcome_msg, parse_mode="Markdown")
        
        # Log activity
        self.log_activity(TelegramMessage(
            timestamp=datetime.now(timezone.utc).isoformat(),
            chat_id=chat_id,
            username=username,
            message_type="command",
            content="/start",
            command="start",
            response="Welcome message sent"
        ))

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """System status command"""
        if not self.is_authorized(update.effective_chat.id):
            await update.message.reply_text(" Unauthorized")
            return
        
        start_time = time.time()
        
        try:
            # Check running services
            status_report = await self.get_system_status()
            
            execution_time = time.time() - start_time
            
            await update.message.reply_text(status_report, parse_mode="Markdown")
            
            # Log activity
            self.log_activity(TelegramMessage(
                timestamp=datetime.now(timezone.utc).isoformat(),
                chat_id=update.effective_chat.id,
                username=update.effective_user.username or "Unknown",
                message_type="command",
                content="/status",
                command="status",
                response="Status report generated",
                execution_time=execution_time
            ))
            
        except Exception as e:
            await update.message.reply_text(f" Status check failed: {e}")
            logger.error(f"Status command failed: {e}")

    async def cmd_health(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Health check command"""
        if not self.is_authorized(update.effective_chat.id):
            await update.message.reply_text(" Unauthorized")
            return
        
        await update.message.reply_text(" Running health checks...")
        
        try:
            health_report = await self.run_health_checks()
            await update.message.reply_text(health_report, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f" Health check failed: {e}")

    async def cmd_wealth(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Wealth intelligence report"""
        if not self.is_authorized(update.effective_chat.id):
            await update.message.reply_text(" Unauthorized")
            return
        
        await update.message.reply_text(" Generating wealth report...")
        
        try:
            report = await self.get_wealth_report()
            await update.message.reply_text(report, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f" Wealth report failed: {e}")

    async def cmd_groq(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Groq engine status and test"""
        if not self.is_authorized(update.effective_chat.id):
            await update.message.reply_text(" Unauthorized")
            return
        
        await update.message.reply_text(" Testing Groq engine...")
        
        try:
            result = await self.test_groq_engine()
            await update.message.reply_text(result, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f" Groq test failed: {e}")

    async def cmd_parlay(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate advanced parlay analysis with real-time data"""
        if not self.is_authorized(update.effective_chat.id):
            await update.message.reply_text(" Unauthorized")
            return
        
        await update.message.reply_text(" Running EQ12 parlay optimization engine...")
        
        try:
            # Parse command arguments for advanced options
            args = context.args
            target_legs = 8
            ev_floor = 0.01
            min_eq_index = 30.0
            
            # Parse arguments if provided
            if args:
                try:
                    if len(args) >= 1:
                        target_legs = int(args[0])
                    if len(args) >= 2:
                        ev_floor = float(args[1])
                    if len(args) >= 3:
                        min_eq_index = float(args[2])
                except (ValueError, IndexError):
                    await update.message.reply_text(" Invalid arguments. Use: /parlay [legs] [ev_floor] [min_eq_index]")
                    return
            
            # Run the parlay simulation engine
            analysis = await self.generate_advanced_parlay_analysis(target_legs, ev_floor, min_eq_index)
            
            # Split message if too long
            if len(analysis) > 4096:
                # Send in chunks
                for i in range(0, len(analysis), 4096):
                    chunk = analysis[i:i+4096]
                    await update.message.reply_text(chunk, parse_mode="Markdown")
                    await asyncio.sleep(0.5)  # Rate limiting
            else:
                await update.message.reply_text(analysis, parse_mode="Markdown")
                
        except Exception as e:
            error_msg = f" Parlay analysis failed: {str(e)[:200]}..."
            await update.message.reply_text(error_msg)
            logger.error(f"Parlay command failed: {e}")

    async def cmd_alerts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Alert management command with advanced options"""
        if not self.is_authorized(update.effective_chat.id):
            await update.message.reply_text(" Unauthorized")
            return
        
        args = context.args if hasattr(context, 'args') else []
        
        if not args:
            # Show current alert status
            alert_status = await self.get_alert_status()
            await update.message.reply_text(alert_status, parse_mode="Markdown")
            return
        
        action = args[0].lower()
        
        if action == "enable":
            await self.enable_real_time_alerts()
            await update.message.reply_text(" Real-time alerts **ENABLED**", parse_mode="Markdown")
            
        elif action == "disable":
            await self.disable_real_time_alerts()
            await update.message.reply_text(" Real-time alerts **DISABLED**", parse_mode="Markdown")
            
        elif action == "test":
            await self.send_test_alert()
            await update.message.reply_text(" Test alert sent", parse_mode="Markdown")
            
        elif action == "history":
            history = await self.get_alert_history()
            await update.message.reply_text(history, parse_mode="Markdown")
            
        else:
            help_msg = """
 **Alert Management**

**Commands:**
 `/alerts` - Show current status
 `/alerts enable` - Enable real-time alerts
 `/alerts disable` - Disable alerts
 `/alerts test` - Send test alert
 `/alerts history` - Recent alert history

**Alert Types:**
  High-value parlay opportunities
  Profit threshold alerts
  System warnings
  Emergency notifications
            """
            await update.message.reply_text(help_msg, parse_mode="Markdown")

    async def get_alert_status(self) -> str:
        """Get current alert system status"""
        try:
            config = self.config.get('alert_types', {})
            enabled_count = sum(1 for alert in config.values() if alert.get('enabled', False))
            total_count = len(config)
            
            status_msg = f""" **Alert System Status**

**Configuration:**
 Enabled Alerts: {enabled_count}/{total_count}
 Auto-responses: {' ON' if self.config.get('auto_responses') else ' OFF'}
 Command Logging: {' ON' if self.config.get('command_logging') else ' OFF'}

**Alert Types:**
"""
            
            for alert_type, settings in config.items():
                status_icon = "" if settings.get('enabled') else ""
                priority = settings.get('priority', 'medium').upper()
                status_msg += f" {status_icon} {alert_type.title()}: {priority}\n"
            
            # Recent activity
            recent_alerts = await self.get_recent_alert_count()
            status_msg += f"\n**Recent Activity (24h):**\n Alerts Sent: {recent_alerts}\n"
            
            return status_msg
            
        except Exception as e:
            return f" Failed to get alert status: {e}"

    async def enable_real_time_alerts(self):
        """Enable real-time alert monitoring"""
        try:
            # Update config
            for alert_type in self.config.get('alert_types', {}):
                self.config['alert_types'][alert_type]['enabled'] = True
            
            # Save config
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            # Start monitoring if not already running
            await self.start_alert_monitoring()
            
        except Exception as e:
            logger.error(f"Failed to enable alerts: {e}")

    async def disable_real_time_alerts(self):
        """Disable real-time alert monitoring"""
        try:
            # Update config
            for alert_type in self.config.get('alert_types', {}):
                self.config['alert_types'][alert_type]['enabled'] = False
            
            # Save config
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to disable alerts: {e}")

    async def start_alert_monitoring(self):
        """Start real-time alert monitoring background task"""
        try:
            if not hasattr(self, '_monitoring_task') or self._monitoring_task.done():
                self._monitoring_task = asyncio.create_task(self._monitor_alerts_loop())
                logger.info("Alert monitoring started")
        except Exception as e:
            logger.error(f"Failed to start alert monitoring: {e}")

    async def _monitor_alerts_loop(self):
        """Background monitoring loop for real-time alerts"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Check for high-value parlay opportunities
                await self.check_parlay_opportunities()
                
                # Check system health
                await self.check_system_health_alerts()
                
                # Check for profit alerts
                await self.check_profit_alerts()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Alert monitoring error: {e}")
                await asyncio.sleep(30)  # Wait before retrying

    async def check_parlay_opportunities(self):
        """Check for high-value parlay opportunities and send alerts"""
        try:
            if not self.config.get('alert_types', {}).get('betting', {}).get('enabled'):
                return
            
            # Run quick parlay analysis
            analysis_result = await self.generate_advanced_parlay_analysis(6, 0.05, 40.0)
            
            # Check if we found high-value opportunities
            if "EV:" in analysis_result and " EV:" in analysis_result:
                lines = analysis_result.split('\n')
                ev_lines = [line for line in lines if " EV:" in line]
                
                for line in ev_lines:
                    try:
                        # Extract EV value
                        ev_part = line.split(" EV:")[1].split("|")[0].strip()
                        ev_value = float(ev_part)
                        
                        if ev_value > 5.0:  # High EV threshold
                            alert_msg = f""" **HIGH-VALUE PARLAY ALERT** 

{line}

 **Action Required:** Review this opportunity immediately!

Use `/parlay` for full analysis.
"""
                            await self.broadcast_message(alert_msg, "admins")
                            
                            # Log alert
                            await self.log_alert("betting", "high", "High-Value Parlay", alert_msg)
                            break  # Only send one alert per check
                            
                    except (ValueError, IndexError):
                        continue
                        
        except Exception as e:
            logger.error(f"Parlay opportunity check failed: {e}")

    async def log_alert(self, alert_type: str, priority: str, title: str, message: str):
        """Log alert to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO telegram_alerts 
                    (timestamp, alert_type, priority, title, message, chat_ids, sent, delivery_attempts)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now(timezone.utc).isoformat(),
                    alert_type, priority, title, message,
                    json.dumps(self.chat_ids.get("admins", [])),
                    True, 1
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")

    async def get_recent_alert_count(self) -> int:
        """Get count of alerts sent in last 24 hours"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM telegram_alerts 
                    WHERE timestamp > datetime('now', '-24 hours')
                """)
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Failed to get alert count: {e}")
            return 0

    async def get_alert_history(self) -> str:
        """Get recent alert history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT timestamp, alert_type, priority, title 
                    FROM telegram_alerts 
                    ORDER BY timestamp DESC 
                    LIMIT 10
                """)
                alerts = cursor.fetchall()
            
            if not alerts:
                return " No recent alerts"
            
            history_msg = " **Recent Alert History**\n\n"
            
            for timestamp, alert_type, priority, title in alerts:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%m-%d %H:%M')
                priority_icon = {"critical": "", "high": "", "medium": "", "low": ""}.get(priority, "")
                
                history_msg += f" {priority_icon} {formatted_time} - {title} ({alert_type})\n"
            
            return history_msg
            
        except Exception as e:
            logger.error(f"Failed to get alert history: {e}")
            return f" Failed to get history: {e}"

    async def send_test_alert(self):
        """Send a test alert"""
        test_msg = f""" **TEST ALERT** 

This is a test of the EQ12 alert system.

**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:**  All systems operational

If you received this, alerts are working correctly!
"""
        await self.broadcast_message(test_msg, "admins")
        await self.log_alert("system", "low", "Test Alert", test_msg)
        """Help command"""
        help_text = """
 **EQ12 Commander Help**

**System Commands:**
 `/status` - System overview and health
 `/health` - Run comprehensive health checks
 `/reboot` - Restart EQ12 services
 `/logs` - View recent system logs

**Intelligence Commands:**
 `/wealth` - Wealth intelligence report
 `/groq` - Groq engine status and test
 `/openai` - OpenAI key management
 `/analytics` - Performance analytics

**Trading Commands:**
 `/parlay` - Generate betting analysis
 `/portfolio` - Portfolio performance

**Administration:**
 `/alerts` - Alert management
 `/admin` - Admin panel
 `/help` - This help message

**Quick Tips:**
 All commands are logged for security
 System auto-responds to critical alerts
 Use `/status` for quick health overview
        """
        
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle non-command messages"""
        if not self.is_authorized(update.effective_chat.id):
            return
        
        message_text = update.message.text.lower()
        
        # Simple AI-like responses
        if "status" in message_text or "health" in message_text:
            await update.message.reply_text("Use `/status` for system overview or `/health` for detailed checks.")
        elif "help" in message_text:
            await update.message.reply_text("Use `/help` to see all available commands.")
        elif "wealth" in message_text or "money" in message_text:
            await update.message.reply_text("Use `/wealth` for wealth intelligence report.")
        else:
            await update.message.reply_text("Use `/help` to see available commands.")

    async def generate_advanced_parlay_analysis(self, target_legs: int = 8, ev_floor: float = 0.01, min_eq_index: float = 30.0) -> str:
        """Generate advanced parlay analysis using the complete simulation engine"""
        try:
            import subprocess
            import json
            from pathlib import Path
            
            # Run the parlay simulation engine
            engine_script = Path(self.workspace_path) / "scripts" / "eq12_complete_parlay_simulation_engine.py"
            if not engine_script.exists():
                return " Parlay simulation engine not found"
            
            # Execute with parameters
            cmd = [
                "python", str(engine_script),
                "--target_legs", str(target_legs),
                "--ev_floor", str(ev_floor),
                "--min_eq_index", str(min_eq_index)
            ]
            
            # Run the process
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
                cwd=str(self.workspace_path)
            )
            
            if result.returncode != 0:
                return f" Parlay engine failed: {result.stderr[:200]}..."
            
            # Find the latest results file
            logs_dir = Path(self.workspace_path) / "logs"
            result_files = list(logs_dir.glob("eq12_parlay_simulation_*.json"))
            
            if not result_files:
                return " No parlay results found"
            
            # Get the most recent file
            latest_file = max(result_files, key=lambda x: x.stat().st_mtime)
            
            # Load and format results
            with open(latest_file) as f:
                data = json.load(f)
            
            return self.format_parlay_results_for_telegram(data)
            
        except subprocess.TimeoutExpired:
            return " Parlay analysis timed out (>2 minutes)"
        except Exception as e:
            logger.error(f"Parlay analysis failed: {e}")
            return f" Analysis failed: {str(e)[:200]}..."

    def format_parlay_results_for_telegram(self, data: dict) -> str:
        """Format parlay results for Telegram display"""
        try:
            summary = data.get('summary', {})
            parlays = data.get('optimal_parlays', [])
            
            # Header
            msg = f""" **EQ12 Parlay Analysis Results**

 **Summary:**
 Games Analyzed: {summary.get('total_games', 0)}
 Legs Generated: {summary.get('total_legs', 0)}
 Optimal Parlays: {len(parlays)}
 Coral Accelerator: {' ENABLED' if summary.get('coral_enabled') else ' DISABLED'}

"""
            
            # Top 3 parlays
            if parlays:
                msg += " **Top Recommendations:**\n\n"
                
                for i, parlay in enumerate(parlays[:3], 1):
                    legs = parlay.get('legs', [])
                    ev = parlay.get('expected_value', 0)
                    odds = parlay.get('total_odds', 0)
                    eq_index = parlay.get('eq12_index', 0)
                    
                    msg += f"**{i}. {parlay.get('id', 'Unknown')}**\n"
                    msg += f" EV: {ev:.2f} |  Odds: {odds:.0f} |  EQ12: {eq_index:.1f}\n"
                    msg += f" Legs: {len(legs)} | Leagues: {', '.join(set(leg.get('league', 'N/A') for leg in legs[:3]))}\n"
                    
                    # Show top legs
                    if legs:
                        msg += "**Top Legs:**\n"
                        for j, leg in enumerate(legs[:2], 1):
                            team = leg.get('team', 'Unknown')
                            bet_type = leg.get('bet_type', 'ML')
                            edge = leg.get('edge', 0)
                            msg += f"  {j}. {team} ({bet_type}) - Edge: {edge:.2f}%\n"
                    
                    msg += "\n"
            else:
                msg += " No optimal parlays found with current criteria\n"
            
            # Add usage tip
            msg += f"\n **Tip:** Use `/parlay [legs] [ev_floor] [eq_index]` for custom analysis"
            
            return msg
            
        except Exception as e:
            logger.error(f"Failed to format parlay results: {e}")
            return f" Failed to format results: {str(e)[:100]}..."

    # System Integration Methods
    async def get_system_status(self) -> str:
        """Get comprehensive system status"""
        try:
            # Check if key processes are running
            services = {
                "Hub Autostart": self.check_process("eq12_hub_autostart.py"),
                "Wealth Core": self.check_process("eq12_wealth_core.py"),
                "Groq Engine": self.check_process("eq12_groq_engine.py"),
                "OpenAI Monitor": self.check_process("eq12_openai_key_engine.py"),
                "Web Interface": self.check_process("eq12_web_interface_clean.py")
            }
            
            # System metrics
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:\\')
            
            status_msg = f"""
 **EQ12 System Status**

**Services:**
"""
            
            for service, running in services.items():
                status_icon = "" if running else ""
                status_msg += f" {status_icon} {service}\n"
            
            status_msg += f"""

**System Metrics:**
 CPU: {cpu_percent:.1f}%
 Memory: {memory.percent:.1f}% ({memory.available // 1024**3:.1f}GB free)
 Disk: {disk.percent:.1f}% ({disk.free // 1024**3:.1f}GB free)

**Last Updated:** {datetime.now().strftime('%H:%M:%S')}
            """
            
            return status_msg
            
        except Exception as e:
            return f" Failed to get system status: {e}"

    def check_process(self, script_name: str) -> bool:
        """Check if a Python process is running"""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'python.exe':
                        cmdline = ' '.join(proc.info['cmdline'] or [])
                        if script_name in cmdline:
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception:
            return False

    async def run_health_checks(self) -> str:
        """Run comprehensive health checks"""
        health_results = []
        
        # Check API keys
        api_keys = {
            "GROQ_API_KEY": bool(os.getenv("GROQ_API_KEY")),
            "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
            "TELEGRAM_BOT_TOKEN": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
            "TELEGRAM_CHAT_ID": bool(os.getenv("TELEGRAM_CHAT_ID"))
        }
        
        # Check file system
        critical_paths = [
            self.workspace_path / "scripts",
            self.workspace_path / "data",
            self.workspace_path / "logs",
            self.workspace_path / "configs"
        ]
        
        health_msg = " **Health Check Results**\n\n**API Keys:**\n"
        
        for key, present in api_keys.items():
            icon = "" if present else ""
            health_msg += f" {icon} {key}\n"
        
        health_msg += "\n**File System:**\n"
        
        for path in critical_paths:
            exists = path.exists()
            icon = "" if exists else ""
            health_msg += f" {icon} {path.name}/\n"
        
        # Test basic functionality
        health_msg += "\n**Functionality Tests:**\n"
        
        try:
            # Test Groq engine
            result = subprocess.run([
                "python", str(self.workspace_path / "scripts" / "eq12_groq_engine.py"),
                "--test", "Health check test"
            ], capture_output=True, text=True, timeout=30)
            
            groq_ok = result.returncode == 0
            icon = "" if groq_ok else ""
            health_msg += f" {icon} Groq Engine Test\n"
            
        except Exception as e:
            health_msg += f"  Groq Engine Test (Error: {str(e)[:50]})\n"
        
        health_msg += f"\n**Check completed:** {datetime.now().strftime('%H:%M:%S')}"
        
        return health_msg

    async def get_wealth_report(self) -> str:
        """Get wealth intelligence report"""
        try:
            # Run wealth core status
            result = subprocess.run([
                "python", str(self.workspace_path / "scripts" / "eq12_wealth_core.py"),
                "--status", "--brief"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Parse output for key metrics
                output = result.stdout
                return f"""
 **Wealth Intelligence Report**

{output[:1000]}

*Generated: {datetime.now().strftime('%H:%M:%S')}*
                """
            else:
                return " Wealth core not responding"
                
        except Exception as e:
            return f" Wealth report failed: {e}"

    async def test_groq_engine(self) -> str:
        """Test Groq engine functionality"""
        try:
            result = subprocess.run([
                "python", str(self.workspace_path / "scripts" / "eq12_groq_engine.py"),
                "--test", "Telegram commander test"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return " **Groq Engine Status: OPERATIONAL**\n\nLatency test passed successfully!"
            else:
                return f" **Groq Engine Status: ERROR**\n\n{result.stderr[:500]}"
                
        except Exception as e:
            return f" Groq test failed: {e}"

    async def generate_betting_analysis(self) -> str:
        """Generate betting analysis using EQ12 systems"""
        try:
            result = subprocess.run([
                "python", str(self.workspace_path / "scripts" / "eq12_groq_engine.py"),
                "--test", "Generate betting analysis for today's games with value picks"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Parse JSON response
                import json
                try:
                    response_data = json.loads(result.stdout)
                    content = response_data.get("content", "No analysis generated")
                    
                    # Truncate if too long
                    if len(content) > 2000:
                        content = content[:2000] + "..."
                    
                    return f" **EQ12 Betting Analysis**\n\n{content}"
                except json.JSONDecodeError:
                    return f" **EQ12 Betting Analysis**\n\n{result.stdout[:2000]}"
            else:
                return " Betting analysis failed"
                
        except Exception as e:
            return f" Analysis error: {e}"

    # Alert System
    async def send_alert(self, alert_type: str, title: str, message: str, priority: str = "medium"):
        """Send alert to configured recipients"""
        try:
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO telegram_alerts 
                    (timestamp, alert_type, priority, title, message, chat_ids)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now(timezone.utc).isoformat(),
                    alert_type, priority, title, message,
                    json.dumps(self.chat_ids["admins"])
                ))
                conn.commit()
            
            # Format alert message
            priority_icons = {
                "critical": "",
                "high": "",
                "medium": "",
                "low": ""
            }
            
            icon = priority_icons.get(priority, "")
            formatted_message = f"{icon} **{title}**\n\n{message}\n\n*{alert_type.upper()} | {datetime.now().strftime('%H:%M:%S')}*"
            
            # Send to admins
            sent_count = await self.broadcast_message(formatted_message, "admins")
            
            # Update database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE telegram_alerts 
                    SET sent = TRUE, delivery_attempts = ?
                    WHERE timestamp = ? AND title = ?
                """, (sent_count, datetime.now(timezone.utc).isoformat(), title))
                conn.commit()
            
            logger.info(f"Alert sent to {sent_count} recipients: {title}")
            
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")

    async def start_monitoring(self):
        """Start the monitoring and alert system"""
        logger.info("Starting Telegram monitoring system...")
        
        while True:
            try:
                # Check for system alerts
                await self.check_system_alerts()
                
                # Process pending alerts
                await self.process_pending_alerts()
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def check_system_alerts(self):
        """Check for system conditions that require alerts"""
        try:
            import psutil
            
            # CPU usage alert
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                await self.send_alert(
                    "system", "High CPU Usage", 
                    f"CPU usage at {cpu_percent:.1f}%", "high"
                )
            
            # Memory usage alert
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                await self.send_alert(
                    "system", "High Memory Usage",
                    f"Memory usage at {memory.percent:.1f}%", "high"
                )
            
            # Disk space alert
            disk = psutil.disk_usage('C:\\')
            if disk.percent > 90:
                await self.send_alert(
                    "system", "Low Disk Space",
                    f"Disk usage at {disk.percent:.1f}%", "high"
                )
            
        except Exception as e:
            logger.error(f"System check failed: {e}")

    async def process_pending_alerts(self):
        """Process any pending alerts that failed to send"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, title, message, priority, chat_ids, delivery_attempts
                    FROM telegram_alerts 
                    WHERE sent = FALSE AND delivery_attempts < 3
                    ORDER BY timestamp DESC LIMIT 10
                """)
                
                pending_alerts = cursor.fetchall()
                
                for alert in pending_alerts:
                    alert_id, title, message, priority, chat_ids_json, attempts = alert
                    
                    try:
                        chat_ids = json.loads(chat_ids_json)
                        
                        # Try to send again
                        sent_count = 0
                        for chat_id in chat_ids:
                            if await self.send_message(chat_id, message):
                                sent_count += 1
                        
                        # Update database
                        if sent_count > 0:
                            conn.execute("""
                                UPDATE telegram_alerts 
                                SET sent = TRUE, delivery_attempts = ?
                                WHERE id = ?
                            """, (attempts + 1, alert_id))
                        else:
                            conn.execute("""
                                UPDATE telegram_alerts 
                                SET delivery_attempts = ?
                                WHERE id = ?
                            """, (attempts + 1, alert_id))
                        
                        conn.commit()
                        
                    except Exception as e:
                        logger.error(f"Failed to process alert {alert_id}: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to process pending alerts: {e}")

    async def run_bot(self):
        """Run the Telegram bot"""
        if not self.application:
            logger.error("Bot application not initialized")
            return
        
        try:
            # Setup commands
            await self.setup_bot_commands()
            
            # Start polling
            logger.info("Starting Telegram bot polling...")
            await self.application.run_polling()
            
        except Exception as e:
            logger.error(f"Bot run failed: {e}")


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Telegram Commander")
    parser.add_argument("--workspace", default="C:\\EQ12", help="Workspace path")
    parser.add_argument("--monitor-only", action="store_true", help="Run monitoring only")
    parser.add_argument("--test-alert", help="Send test alert")
    
    args = parser.parse_args()
    
    commander = EQ12TelegramCommander(args.workspace)
    
    if args.test_alert:
        await commander.send_alert(
            "test", "Test Alert", args.test_alert, "medium"
        )
        return 0
    
    if args.monitor_only:
        await commander.start_monitoring()
        return 0
    
    # Run both bot and monitoring
    tasks = []
    
    if commander.application:
        tasks.append(commander.run_bot())
    
    tasks.append(commander.start_monitoring())
    
    if tasks:
        await asyncio.gather(*tasks)
    else:
        logger.error("No tasks to run - check configuration")
        return 1
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Telegram Commander stopped by user")
        exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)