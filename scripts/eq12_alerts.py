#!/usr/bin/env python3
"""
 EQ12 CRYPTO ALERTS SYSTEM
Automated alert system for Coral TPU cryptocurrency signals
Telegram, Discord, and email notifications
"""

import os
import json
import logging
import asyncio
import requests
from datetime import datetime
from typing import Dict, List, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class CryptoAlertsSystem:
    """
     Automated cryptocurrency alerts powered by EQ12 Coral signals
    Multi-channel notification system
    """
    
    def __init__(self, config_path: str = None):
        self.setup_logging()
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Alert tracking
        self.alert_history = []
        self.rate_limits = {}
        
        self.logger.info(" EQ12 Crypto Alerts System initialized")
    
    def setup_logging(self):
        """Setup logging system"""
        
        log_dir = "C:\\EQ12\\logs\\crypto\\alerts"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"crypto_alerts_{timestamp}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load alerts configuration"""
        
        default_config = {
            "telegram": {
                "enabled": True,
                "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
                "chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
                "rate_limit_minutes": 5
            },
            "discord": {
                "enabled": False,
                "webhook_url": os.getenv("DISCORD_WEBHOOK_URL", ""),
                "rate_limit_minutes": 3
            },
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "email": os.getenv("ALERT_EMAIL", ""),
                "password": os.getenv("ALERT_EMAIL_PASSWORD", ""),
                "recipients": []
            },
            "thresholds": {
                "high_confidence": 0.85,
                "medium_confidence": 0.70,
                "ev_threshold": 0.60,
                "price_change_threshold": 5.0
            },
            "filters": {
                "min_confidence": 0.60,
                "symbols_whitelist": [],
                "symbols_blacklist": [],
                "max_alerts_per_hour": 20
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
        
        return default_config
    
    async def send_telegram_alert(self, message: str, urgent: bool = False) -> bool:
        """Send alert via Telegram"""
        
        if not self.config["telegram"]["enabled"]:
            return False
        
        bot_token = self.config["telegram"]["bot_token"]  
        chat_id = self.config["telegram"]["chat_id"]
        
        if not bot_token or not chat_id:
            self.logger.warning("Telegram credentials not configured")
            return False
        
        # Check rate limiting
        if not urgent and not self._check_rate_limit("telegram"):
            self.logger.debug("Telegram rate limit exceeded")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                self.logger.info(" Telegram alert sent")
                self._update_rate_limit("telegram")
                return True
            else:
                self.logger.error(f" Telegram API error: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f" Telegram send failed: {e}")
            return False
    
    async def send_discord_alert(self, message: str, urgent: bool = False) -> bool:
        """Send alert via Discord webhook"""
        
        if not self.config["discord"]["enabled"]:
            return False
        
        webhook_url = self.config["discord"]["webhook_url"]
        
        if not webhook_url:
            self.logger.warning("Discord webhook not configured")
            return False
        
        # Check rate limiting
        if not urgent and not self._check_rate_limit("discord"):
            self.logger.debug("Discord rate limit exceeded")
            return False
        
        try:
            payload = {
                "content": message,
                "username": "EQ12 Coral Crypto AI"
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            if response.status_code == 204:
                self.logger.info(" Discord alert sent")
                self._update_rate_limit("discord")
                return True
            else:
                self.logger.error(f" Discord webhook error: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f" Discord send failed: {e}")
            return False
    
    async def send_email_alert(self, subject: str, message: str, urgent: bool = False) -> bool:
        """Send alert via email"""
        
        if not self.config["email"]["enabled"]:
            return False
        
        email_config = self.config["email"]
        recipients = email_config.get("recipients", [])
        
        if not recipients:
            self.logger.warning("No email recipients configured")
            return False
        
        # Check rate limiting
        if not urgent and not self._check_rate_limit("email"):
            self.logger.debug("Email rate limit exceeded")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = email_config["email"]
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'html'))
            
            # Send email
            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            server.login(email_config["email"], email_config["password"])
            
            text = msg.as_string()
            server.sendmail(email_config["email"], recipients, text)
            server.quit()
            
            self.logger.info(" Email alert sent")
            self._update_rate_limit("email")
            return True
            
        except Exception as e:
            self.logger.error(f" Email send failed: {e}")
            return False
    
    def _check_rate_limit(self, channel: str) -> bool:
        """Check if rate limit allows sending"""
        
        rate_limit_minutes = self.config[channel].get("rate_limit_minutes", 5)
        
        if channel not in self.rate_limits:
            return True
        
        last_sent = self.rate_limits[channel]
        time_diff = (datetime.now() - last_sent).total_seconds() / 60
        
        return time_diff >= rate_limit_minutes
    
    def _update_rate_limit(self, channel: str):
        """Update rate limit tracking"""
        
        self.rate_limits[channel] = datetime.now()
    
    def format_signal_alert(self, signal_data: Dict[str, Any]) -> str:
        """Format trading signal for alert message"""
        
        symbol = signal_data.get("symbol", "UNKNOWN")
        signal_type = signal_data.get("signal_type", "HOLD")
        confidence = signal_data.get("confidence", 0.0)
        ev_score = signal_data.get("ev_score", 0.0)
        price = signal_data.get("price", 0.0)
        
        emoji_map = {'BUY': '', 'SELL': '', 'HOLD': ''}
        emoji = emoji_map.get(signal_type, '')
        
        # Determine urgency
        urgency_emoji = ""
        if confidence >= 0.90:
            urgency_emoji = " URGENT "
        elif confidence >= 0.80:
            urgency_emoji = " HIGH "
        
        message = f"""
{urgency_emoji} <b>EQ12 CORAL CRYPTO SIGNAL</b>

{emoji} <b>{signal_type}</b> - {symbol}
 Price: ${price:,.2f}
 Confidence: {confidence:.1%}
 EV Score: {ev_score:.1%}

 <i>Powered by Google Coral Edge TPU</i>
 {datetime.now().strftime('%H:%M:%S')}

---
<i>EQ12 Automated Trading Intelligence</i>
        """.strip()
        
        return message
    
    def format_price_alert(self, symbol: str, price: float, change_percent: float) -> str:
        """Format price movement alert"""
        
        direction = "" if change_percent > 0 else ""
        
        message = f"""
 <b>PRICE ALERT</b> {direction}

<b>{symbol}</b>
 Current Price: ${price:,.2f}
 Change: {change_percent:+.2f}%

 {datetime.now().strftime('%H:%M:%S')}

---
<i>EQ12 Price Monitoring</i>
        """.strip()
        
        return message
    
    def should_send_alert(self, signal_data: Dict[str, Any]) -> bool:
        """Determine if alert should be sent based on filters"""
        
        filters = self.config.get("filters", {})
        
        # Check minimum confidence
        min_confidence = filters.get("min_confidence", 0.60)
        if signal_data.get("confidence", 0) < min_confidence:
            return False
        
        # Check symbol whitelist
        whitelist = filters.get("symbols_whitelist", [])
        if whitelist and signal_data.get("symbol") not in whitelist:
            return False
        
        # Check symbol blacklist
        blacklist = filters.get("symbols_blacklist", [])
        if signal_data.get("symbol") in blacklist:
            return False
        
        # Check hourly alert limit
        max_alerts_per_hour = filters.get("max_alerts_per_hour", 20)
        recent_alerts = [
            alert for alert in self.alert_history
            if (datetime.now() - alert["timestamp"]).total_seconds() < 3600
        ]
        
        if len(recent_alerts) >= max_alerts_per_hour:
            self.logger.warning("Hourly alert limit reached")
            return False
        
        return True
    
    async def process_crypto_signal(self, signal_data: Dict[str, Any]):
        """Process and send alerts for crypto trading signal"""
        
        # Check if alert should be sent
        if not self.should_send_alert(signal_data):
            return
        
        # Format alert message
        message = self.format_signal_alert(signal_data)
        
        # Determine urgency
        confidence = signal_data.get("confidence", 0.0)
        urgent = confidence >= self.config["thresholds"]["high_confidence"]
        
        # Send alerts
        alert_results = []
        
        # Telegram
        if self.config["telegram"]["enabled"]:
            result = await self.send_telegram_alert(message, urgent)
            alert_results.append(("telegram", result))
        
        # Discord
        if self.config["discord"]["enabled"]:
            result = await self.send_discord_alert(message, urgent)
            alert_results.append(("discord", result))
        
        # Email (for high confidence signals only)
        if self.config["email"]["enabled"] and urgent:
            subject = f" EQ12 Crypto Alert: {signal_data.get('signal_type')} {signal_data.get('symbol')}"
            result = await self.send_email_alert(subject, message, urgent)
            alert_results.append(("email", result))
        
        # Log alert
        self._log_sent_alert(signal_data, alert_results)
    
    async def process_price_alert(self, symbol: str, price: float, change_percent: float):
        """Process and send price movement alerts"""
        
        threshold = self.config["thresholds"]["price_change_threshold"]
        
        if abs(change_percent) < threshold:
            return
        
        # Format message
        message = self.format_price_alert(symbol, price, change_percent)
        
        # Send to primary channels only
        if self.config["telegram"]["enabled"]:
            await self.send_telegram_alert(message, urgent=False)
        
        if self.config["discord"]["enabled"]:
            await self.send_discord_alert(message, urgent=False)
    
    def _log_sent_alert(self, signal_data: Dict[str, Any], results: List[tuple]):
        """Log sent alert details"""
        
        alert_record = {
            "timestamp": datetime.now(),
            "symbol": signal_data.get("symbol"),
            "signal_type": signal_data.get("signal_type"),
            "confidence": signal_data.get("confidence"),
            "channels": results,
            "successful_sends": sum(1 for _, success in results if success)
        }
        
        self.alert_history.append(alert_record)
        
        # Keep only recent alerts
        if len(self.alert_history) > 10000:
            self.alert_history = self.alert_history[-10000:]
        
        self.logger.info(f"Alert sent: {signal_data.get('symbol')} - "
                        f"{alert_record['successful_sends']}/{len(results)} channels")
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert system statistics"""
        
        recent_alerts = [
            alert for alert in self.alert_history
            if (datetime.now() - alert["timestamp"]).total_seconds() < 86400  # Last 24h
        ]
        
        return {
            "total_alerts_sent": len(self.alert_history),
            "alerts_last_24h": len(recent_alerts),
            "channels_configured": sum(1 for channel in ["telegram", "discord", "email"] 
                                     if self.config[channel]["enabled"]),
            "rate_limits_active": len(self.rate_limits),
            "last_alert": self.alert_history[-1]["timestamp"] if self.alert_history else None
        }


async def main():
    """Test the alerts system"""
    
    print(" EQ12 Crypto Alerts System Test")
    
    alerts = CryptoAlertsSystem()
    
    # Test signal
    test_signal = {
        "symbol": "BTCUSDT",
        "signal_type": "BUY",
        "confidence": 0.87,
        "ev_score": 0.73,
        "price": 42500.50
    }
    
    print("\n Sending test alert...")
    await alerts.process_crypto_signal(test_signal)
    
    # Display stats
    stats = alerts.get_alert_stats()
    print(f"\n Stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())