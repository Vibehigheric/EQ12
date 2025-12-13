# EQ12 Telegram Bot Setup Guide

## Windows Setup (Task Scheduler)

### Install the Task:
```powershell
# Run as Administrator
schtasks /create /tn "EQ12_TelegramBot" /xml C:\EQ12\tasks\EQ12_TelegramBot.xml /f
```

### Manage the Task:
```powershell
# Start manually
schtasks /run /tn "EQ12_TelegramBot"

# Stop the task
schtasks /end /tn "EQ12_TelegramBot"

# Check status
schtasks /query /tn "EQ12_TelegramBot" /fo LIST

# Delete task (if needed)
schtasks /delete /tn "EQ12_TelegramBot" /f
```

### Environment Variables (Windows):
Set these in your system environment or `.env` file:
```
TG_TOKEN=your-telegram-bot-token
TG_CHAT_ID=your-telegram-chat-id
```

## Linux Setup (systemd)

### Install the Service:
```bash
# Copy service file
sudo cp C:\EQ12\systemd\eq12-telegram-bot.service /etc/systemd/system/

# Edit environment variables
sudo nano /etc/systemd/system/eq12-telegram-bot.service

# Reload systemd and enable
sudo systemctl daemon-reload
sudo systemctl enable eq12-telegram-bot.service
sudo systemctl start eq12-telegram-bot.service
```

### Manage the Service:
```bash
# Check status
systemctl status eq12-telegram-bot.service

# View logs
journalctl -u eq12-telegram-bot.service -f

# Restart service
sudo systemctl restart eq12-telegram-bot.service

# Stop service
sudo systemctl stop eq12-telegram-bot.service

# Disable auto-start
sudo systemctl disable eq12-telegram-bot.service
```

### Environment Variables (Linux):
Edit the service file to include your tokens:
```bash
sudo systemctl edit eq12-telegram-bot.service
```

Add:
```ini
[Service]
Environment="TG_TOKEN=your-telegram-bot-token"
Environment="TG_CHAT_ID=your-telegram-chat-id"
```

## Getting Telegram Bot Token

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot`
3. Follow prompts to create your bot
4. Copy the API token provided
5. To get chat ID, message your bot and visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`

## Testing the Bot

After setup, test with:
```bash
python C:\EQ12\eq12_bot.py
```

Then message your bot:
- `/start` - Initialize bot
- `/status` - Check EQ12 system status
- `/logs 5` - Show last 5 interactions
- `/exportlogs` - Export full log history

## Dependencies

Install required Python packages:
```bash
pip install python-telegram-bot sqlite3
```

## Security Notes

- Never hardcode tokens in scripts
- Use environment variables or `.env` files
- Restrict `/clearlogs` command to admin users only
- Consider enabling Telegram bot privacy mode
- Regularly rotate bot tokens for security

## Troubleshooting

### Bot not responding:
- Check network connectivity
- Verify TG_TOKEN is correct
- Check bot logs: `journalctl -u eq12-telegram-bot.service`

### Permission errors:
- Ensure user has write access to EQ12 directory
- Check file permissions on log database

### Task Scheduler issues (Windows):
- Run Task Scheduler as Administrator
- Check task history in Task Scheduler GUI
- Verify Python is in system PATH
