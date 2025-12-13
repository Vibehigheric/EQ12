# � EQ12 Master Copilot Cookbook (Complete Edition)

## 🎯 Purpose
This is the **master recipe library** for the EQ12 automation system. All Copilot completions and GPT-5 interactions must **match these patterns, security practices, and coding standards**.

## 🚀 GPT-5 Enhanced Features Integration
- **Verbosity Control**: Use `low` for minimal code, `medium` for balanced detail, `high` for comprehensive implementations
- **Minimal Reasoning**: Set `reasoning.effort: "minimal"` for fast classification and simple extraction tasks
- **Context-Free Grammar**: Enforce strict output formats using Lark or Regex grammars
- **Freeform Function Calling**: Generate raw code payloads directly to execution environments

---

## 1️⃣ Python Bots & Automation

### **FastAPI Service Template**
```python
#!/usr/bin/env python3
"""
EQ12 [SERVICE_NAME] - [BRIEF_DESCRIPTION]
Integrates with: [LIST_INTEGRATIONS]
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# EQ12 Configuration
EQ12_HOME = Path(os.getenv("EQ12_HOME", r"C:\EQ12"))
LOGS_DIR = EQ12_HOME / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | [SERVICE_NAME] | %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / '[service_name].log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("[SERVICE_NAME]")

# FastAPI app
app = FastAPI(title="EQ12 [SERVICE_NAME]", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "[SERVICE_NAME]"
    }

@app.get("/api/[endpoint]")
async def main_endpoint():
    """Main service endpoint"""
    try:
        # Implementation here
        result = {"message": "success", "data": {}}
        logger.info(f"[endpoint] request processed successfully")
        return result
    except Exception as e:
        logger.error(f"[endpoint] error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("Starting EQ12 [SERVICE_NAME]...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
```

### **Telegram Bot Handler Template**
```python
#!/usr/bin/env python3
"""
EQ12 Telegram Bot - [BOT_NAME]
Commands: [LIST_COMMANDS]
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# EQ12 Configuration
EQ12_HOME = Path(os.getenv("EQ12_HOME", r"C:\EQ12"))
LOGS_DIR = EQ12_HOME / "logs"
CREDENTIALS_FILE = EQ12_HOME / "keys" / "credentials.json"

# Load credentials
def load_credentials():
    """Load encrypted credentials"""
    if CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE, 'r') as f:
            creds = json.load(f)
            return creds.get("TELEGRAM_BOT_TOKEN"), creds.get("TELEGRAM_CHAT_ID")
    return None, None

TOKEN, CHAT_ID = load_credentials()
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in credentials")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | TelegramBot | %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'telegram_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TelegramBot")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    keyboard = [[InlineKeyboardButton("🎯 Main Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🤖 EQ12 [BOT_NAME] Active!\n\n"
        "Available commands:\n"
        "/[command1] - [description]\n"
        "/[command2] - [description]",
        reply_markup=reply_markup
    )

async def main_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main command"""
    try:
        # Implementation here
        result = "✅ Command executed successfully"
        await update.message.reply_text(result)
        logger.info(f"Command executed by {update.effective_user.username}")
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        await update.message.reply_text(error_msg)
        logger.error(f"Command error: {e}")

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries"""
    query = update.callback_query
    await query.answer()

    if query.data == "main_menu":
        # Handle main menu
        pass

def main():
    """Main bot function"""
    logger.info("Starting EQ12 Telegram Bot...")

    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("[command]", main_command))
    application.add_handler(CallbackQueryHandler(callback_handler))

    # Start bot
    application.run_polling()

if __name__ == "__main__":
    main()
```

### **OCR Watcher Template**
```python
#!/usr/bin/env python3
"""
EQ12 OCR Watcher - [WATCHER_NAME]
Monitors: [MONITOR_PATH]
Processes: [PROCESS_DESCRIPTION]
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pytesseract
from PIL import Image

# EQ12 Configuration
EQ12_HOME = Path(os.getenv("EQ12_HOME", r"C:\EQ12"))
WATCH_DIR = EQ12_HOME / "snips"
LOGS_DIR = EQ12_HOME / "logs"
PROCESSED_DIR = WATCH_DIR / "processed"

# Create directories
WATCH_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | OCRWatcher | %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'ocr_watcher.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("OCRWatcher")

class ScreenshotHandler(FileSystemEventHandler):
    """Handle screenshot file events"""

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp']:
            logger.info(f"New screenshot detected: {file_path.name}")
            self.process_screenshot(file_path)

    def process_screenshot(self, file_path: Path):
        """Process screenshot with OCR"""
        try:
            # Wait for file to be fully written
            time.sleep(1)

            # Open and process image
            image = Image.open(file_path)

            # Extract text using OCR
            extracted_text = pytesseract.image_to_string(image)

            if extracted_text.strip():
                logger.info(f"Text extracted: {len(extracted_text)} characters")

                # Process extracted text
                self.handle_extracted_text(extracted_text, file_path)
            else:
                logger.warning(f"No text found in {file_path.name}")

            # Move to processed directory
            processed_path = PROCESSED_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_path.name}"
            file_path.rename(processed_path)
            logger.info(f"Screenshot moved to: {processed_path.name}")

        except Exception as e:
            logger.error(f"Error processing screenshot {file_path.name}: {e}")

    def handle_extracted_text(self, text: str, file_path: Path):
        """Handle extracted text"""
        # Implementation specific to use case
        logger.info(f"Processing text from {file_path.name}")

        # Save text to file
        text_file = LOGS_DIR / f"extracted_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(f"Source: {file_path.name}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Text:\n{text}")

def main():
    """Main watcher function"""
    logger.info(f"Starting OCR Watcher - monitoring: {WATCH_DIR}")

    event_handler = ScreenshotHandler()
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_DIR), recursive=False)

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping OCR Watcher...")
        observer.stop()

    observer.join()

if __name__ == "__main__":
    main()
```

---

## 🔧 PowerShell Patterns

### **Admin Toolkit Template**
```powershell
#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    EQ12 [ADMIN_TOOL_NAME] - [DESCRIPTION]
.DESCRIPTION
    Administrative toolkit for [SPECIFIC_PURPOSE]
    Requires Administrator privileges
.PARAMETER Action
    Action to perform: [LIST_ACTIONS]
.EXAMPLE
    .\eq12_[tool].ps1 -Action "Configure" -Verbose
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("[ACTION1]", "[ACTION2]", "[ACTION3]")]
    [string]$Action,

    [string]$ConfigPath = "C:\EQ12\configs\[config_name].json"
)

# EQ12 Configuration
$EQ12_HOME = $env:EQ12_HOME ?? "C:\EQ12"
$LOGS_DIR = Join-Path $EQ12_HOME "logs"
$KEYS_DIR = Join-Path $EQ12_HOME "keys"

# Ensure directories exist
if (-not (Test-Path $LOGS_DIR)) { New-Item -Path $LOGS_DIR -ItemType Directory -Force | Out-Null }

# Setup logging
$LogFile = Join-Path $LOGS_DIR "[tool_name]_$(Get-Date -Format 'yyyyMMdd').log"
function Write-EQ12Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "$Timestamp | $Level | [TOOL_NAME] | $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry -Encoding UTF8
}

function Test-AdminPrivileges {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Invoke-[ActionName] {
    Write-EQ12Log "Starting [ActionName]..."

    try {
        # Implementation here

        Write-EQ12Log "[ActionName] completed successfully" "SUCCESS"
        return $true
    }
    catch {
        Write-EQ12Log "Error in [ActionName]: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Main execution
try {
    Write-EQ12Log "EQ12 [TOOL_NAME] starting - Action: $Action"

    if (-not (Test-AdminPrivileges)) {
        throw "Administrator privileges required"
    }

    switch ($Action) {
        "[ACTION1]" { $result = Invoke-[ActionName] }
        "[ACTION2]" { $result = Invoke-[ActionName] }
        default { throw "Unknown action: $Action" }
    }

    if ($result) {
        Write-EQ12Log "Operation completed successfully" "SUCCESS"
        exit 0
    } else {
        Write-EQ12Log "Operation failed" "ERROR"
        exit 1
    }
}
catch {
    Write-EQ12Log "Fatal error: $($_.Exception.Message)" "FATAL"
    exit 1
}
```

### **User Toolkit Template**
```powershell
<#
.SYNOPSIS
    EQ12 [USER_TOOL_NAME] - [DESCRIPTION]
.DESCRIPTION
    Daily operations toolkit for [SPECIFIC_PURPOSE]
    Safe for standard user execution
.PARAMETER Operation
    Operation to perform: [LIST_OPERATIONS]
.EXAMPLE
    .\eq12_user_[tool].ps1 -Operation "Status"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("[OP1]", "[OP2]", "[OP3]")]
    [string]$Operation
)

# EQ12 Configuration
$EQ12_HOME = $env:EQ12_HOME ?? "C:\EQ12"
$LOGS_DIR = Join-Path $EQ12_HOME "logs"

# Setup logging
$LogFile = Join-Path $LOGS_DIR "user_[tool]_$(Get-Date -Format 'yyyyMMdd').log"
function Write-UserLog {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "$Timestamp | $Level | USER_[TOOL] | $Message"
    Write-Host $LogEntry -ForegroundColor $(if($Level -eq "ERROR"){"Red"}elseif($Level -eq "SUCCESS"){"Green"}else{"White"})
    if (Test-Path $LOGS_DIR) {
        Add-Content -Path $LogFile -Value $LogEntry -Encoding UTF8
    }
}

function Get-[ServiceName]Status {
    Write-UserLog "Checking [ServiceName] status..."

    try {
        # Implementation here
        $status = "Running" # or actual status check

        Write-UserLog "[ServiceName] Status: $status" "SUCCESS"
        return $status
    }
    catch {
        Write-UserLog "Error checking status: $($_.Exception.Message)" "ERROR"
        return "Unknown"
    }
}

# Main execution
try {
    Write-UserLog "EQ12 User [TOOL] - Operation: $Operation"

    switch ($Operation) {
        "Status" {
            $status = Get-[ServiceName]Status
            Write-Host "`n🎯 [ServiceName] Status: $status" -ForegroundColor Cyan
        }
        "[OP2]" {
            # Implementation
        }
        default {
            Write-UserLog "Unknown operation: $Operation" "ERROR"
            exit 1
        }
    }

    Write-UserLog "Operation completed successfully" "SUCCESS"
}
catch {
    Write-UserLog "Error: $($_.Exception.Message)" "ERROR"
    exit 1
}
```

---

## 🐧 Bash/Linux Patterns

### **Systemd Service Template**
```bash
#!/bin/bash
# EQ12 [SERVICE_NAME] - [DESCRIPTION]

# Configuration
EQ12_HOME=${EQ12_HOME:-"/opt/eq12"}
LOGS_DIR="$EQ12_HOME/logs"
SERVICE_NAME="[service_name]"
PYTHON_SCRIPT="$EQ12_HOME/[script_name].py"

# Ensure directories exist
mkdir -p "$LOGS_DIR"

# Logging function
log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$timestamp | $level | $SERVICE_NAME | $message" | tee -a "$LOGS_DIR/${SERVICE_NAME}.log"
}

# Check if service is running
is_running() {
    systemctl is-active --quiet "$SERVICE_NAME"
    return $?
}

# Start service
start_service() {
    log_message "INFO" "Starting $SERVICE_NAME..."

    if is_running; then
        log_message "WARNING" "$SERVICE_NAME is already running"
        return 0
    fi

    # Activate virtual environment if exists
    if [[ -f "$EQ12_HOME/venv/bin/activate" ]]; then
        source "$EQ12_HOME/venv/bin/activate"
    fi

    # Start Python script
    python3 "$PYTHON_SCRIPT" &
    local pid=$!

    echo "$pid" > "$EQ12_HOME/run/${SERVICE_NAME}.pid"
    log_message "SUCCESS" "$SERVICE_NAME started with PID: $pid"
}

# Stop service
stop_service() {
    log_message "INFO" "Stopping $SERVICE_NAME..."

    local pid_file="$EQ12_HOME/run/${SERVICE_NAME}.pid"
    if [[ -f "$pid_file" ]]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            rm -f "$pid_file"
            log_message "SUCCESS" "$SERVICE_NAME stopped"
        else
            log_message "WARNING" "$SERVICE_NAME was not running"
            rm -f "$pid_file"
        fi
    else
        log_message "WARNING" "PID file not found"
    fi
}

# Check status
check_status() {
    if is_running; then
        log_message "INFO" "$SERVICE_NAME is running"
        return 0
    else
        log_message "INFO" "$SERVICE_NAME is not running"
        return 1
    fi
}

# Main execution
case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        stop_service
        sleep 2
        start_service
        ;;
    status)
        check_status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0
```

---

## 🏗️ C# Patterns

### **ASP.NET API Controller Template**
```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System;
using System.Threading.Tasks;
using EQ12.Core.Models;
using EQ12.Core.Services;

namespace EQ12.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class [ControllerName]Controller : ControllerBase
    {
        private readonly ILogger<[ControllerName]Controller> _logger;
        private readonly I[ServiceName]Service _[serviceName]Service;

        public [ControllerName]Controller(
            ILogger<[ControllerName]Controller> logger,
            I[ServiceName]Service [serviceName]Service)
        {
            _logger = logger;
            _[serviceName]Service = [serviceName]Service;
        }

        [HttpGet("health")]
        public ActionResult<HealthResponse> GetHealth()
        {
            _logger.LogInformation("[ControllerName] health check requested");

            return Ok(new HealthResponse
            {
                Status = "Healthy",
                Timestamp = DateTime.UtcNow,
                Service = "[ControllerName]"
            });
        }

        [HttpGet]
        public async Task<ActionResult<[ResponseType]>> Get[MethodName]()
        {
            try
            {
                _logger.LogInformation("[MethodName] request received");

                var result = await _[serviceName]Service.[MethodName]Async();

                _logger.LogInformation("[MethodName] completed successfully");
                return Ok(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in [MethodName]");
                return StatusCode(500, new { Error = "Internal server error" });
            }
        }

        [HttpPost]
        public async Task<ActionResult<[ResponseType]>> Post[MethodName]([RequestType] request)
        {
            try
            {
                if (!ModelState.IsValid)
                {
                    return BadRequest(ModelState);
                }

                _logger.LogInformation("Post[MethodName] request received");

                var result = await _[serviceName]Service.Create[Entity]Async(request);

                _logger.LogInformation("Post[MethodName] completed successfully");
                return CreatedAtAction(nameof(Get[MethodName]), new { id = result.Id }, result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in Post[MethodName]");
                return StatusCode(500, new { Error = "Internal server error" });
            }
        }
    }
}
```

### **Background Worker Service Template**
```csharp
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.DependencyInjection;
using System;
using System.Threading;
using System.Threading.Tasks;

namespace EQ12.Workers
{
    public class [WorkerName]Worker : BackgroundService
    {
        private readonly ILogger<[WorkerName]Worker> _logger;
        private readonly IServiceScopeFactory _scopeFactory;
        private readonly TimeSpan _interval = TimeSpan.FromMinutes(5); // Default interval

        public [WorkerName]Worker(
            ILogger<[WorkerName]Worker> logger,
            IServiceScopeFactory scopeFactory)
        {
            _logger = logger;
            _scopeFactory = scopeFactory;
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            _logger.LogInformation("[WorkerName] Worker starting");

            while (!stoppingToken.IsCancellationRequested)
            {
                try
                {
                    using var scope = _scopeFactory.CreateScope();

                    // Get scoped services
                    var [serviceName]Service = scope.ServiceProvider.GetRequiredService<I[ServiceName]Service>();

                    _logger.LogInformation("[WorkerName] Worker executing task");

                    // Execute work
                    await [serviceName]Service.[MethodName]Async(stoppingToken);

                    _logger.LogInformation("[WorkerName] Worker task completed");
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error in [WorkerName] Worker execution");
                }

                try
                {
                    await Task.Delay(_interval, stoppingToken);
                }
                catch (OperationCanceledException)
                {
                    // Expected when cancellation is requested
                    break;
                }
            }

            _logger.LogInformation("[WorkerName] Worker stopping");
        }
    }
}
```

---

## 🔄 GitHub Actions Patterns

### **Security CI Pipeline Template**
```yaml
name: EQ12 Security CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  EQ12_HOME: /home/runner/work/eq12

jobs:
  security-scan:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install bandit safety semgrep
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

    - name: Run Bandit security scan
      run: |
        bandit -r . -f json -o security-report.json || true
        bandit -r . --severity-level medium

    - name: Run Safety check for vulnerabilities
      run: |
        safety check --json --output safety-report.json || true
        safety check

    - name: Run Semgrep security analysis
      run: |
        semgrep --config=auto --json --output=semgrep-report.json . || true

    - name: Check for exposed secrets
      run: |
        if find . -name "*.env*" -o -name "credentials.json" -o -name "*secrets*" | grep -v ".gitignore"; then
          echo "❌ Exposed secrets detected!"
          exit 1
        fi
        echo "✅ No exposed secrets found"

    - name: Upload security reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: security-reports
        path: |
          security-report.json
          safety-report.json
          semgrep-report.json

  lint-and-test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flake8 black pytest
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

    - name: Format check with black
      run: black --check --diff .

    - name: Test with pytest
      run: |
        pytest tests/ -v --tb=short
```

---

## 📁 File Structure Patterns

### **EQ12 Project Structure Template**
```
C:\EQ12\                                 # Main EQ12 directory
├── configs\                             # Configuration files
│   ├── [service_name]_config.json
│   └── wireguard\
│       ├── wg-betting.conf
│       ├── wg-travel.conf
│       └── wg-finance.conf
├── keys\                                # Encrypted credentials (gitignored)
│   ├── credentials.json                 # Main credentials file
│   └── backup\                          # Credential backups
├── logs\                                # All log files (gitignored)
│   ├── [service_name].log
│   └── archive\                         # Archived logs
├── scripts\                             # Main executable scripts
│   ├── [service_name].py               # Python services
│   ├── eq12_admin.ps1                  # Admin PowerShell toolkit
│   ├── eq12_user.ps1                   # User PowerShell toolkit
│   └── eq12_admin.sh                   # Linux admin toolkit
├── modules\                             # Reusable Python modules
│   ├── __init__.py
│   ├── eq12_core.py                    # Core EQ12 functionality
│   └── integrations\                    # Third-party integrations
├── tests\                               # Test files
│   ├── test_[service_name].py
│   └── integration\                     # Integration tests
├── .vscode\                             # VS Code configuration
│   ├── settings.json                    # Copilot configuration
│   ├── launch.json                      # Debug configurations
│   └── tasks.json                       # Build tasks
├── .github\                             # GitHub Actions
│   └── workflows\
│       └── security-ci.yml              # Security pipeline
├── .gitignore                           # Security-hardened exclusions
├── requirements.txt                     # Python dependencies
└── README.md                            # Project documentation
```

---

## 🛡️ Security Patterns

### **Credential Management Pattern**
```python
import os
import json
from pathlib import Path
from cryptography.fernet import Fernet

class EQ12CredentialManager:
    """Secure credential management for EQ12"""

    def __init__(self, credentials_path: str = None):
        self.eq12_home = Path(os.getenv("EQ12_HOME", r"C:\EQ12"))
        self.keys_dir = self.eq12_home / "keys"
        self.keys_dir.mkdir(parents=True, exist_ok=True)

        self.credentials_file = self.keys_dir / "credentials.enc"
        self.key_file = self.keys_dir / ".key"

    def _get_key(self) -> bytes:
        """Get or generate encryption key"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key

    def load_credentials(self) -> dict:
        """Load and decrypt credentials"""
        if not self.credentials_file.exists():
            return {}

        key = self._get_key()
        fernet = Fernet(key)

        with open(self.credentials_file, 'rb') as f:
            encrypted_data = f.read()

        decrypted_data = fernet.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())

    def save_credentials(self, credentials: dict):
        """Encrypt and save credentials"""
        key = self._get_key()
        fernet = Fernet(key)

        json_data = json.dumps(credentials, indent=2).encode()
        encrypted_data = fernet.encrypt(json_data)

        with open(self.credentials_file, 'wb') as f:
            f.write(encrypted_data)

    def get_credential(self, key_name: str) -> str:
        """Get specific credential"""
        credentials = self.load_credentials()
        return credentials.get(key_name) or os.getenv(key_name)

# Usage example:
# creds = EQ12CredentialManager()
# token = creds.get_credential("TELEGRAM_BOT_TOKEN")
```

---

## 2️⃣ PowerShell (Windows) Patterns

### **User Toolkit Template**
```powershell
function Run-Parlay {
    Write-Host "[*] Running Parlay Generator..." -ForegroundColor Cyan
    python C:\EQ12\eq12_telegram_master_bot.py --command parlay
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Parlay generated successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Parlay generation failed" -ForegroundColor Red
    }
}

function Show-EQ12Status {
    Write-Host "🎯 EQ12 System Status:" -ForegroundColor Yellow
    Get-Process python* | Where-Object {$_.ProcessName -like "*eq12*"} | Format-Table
}
```

### **Admin Toolkit Template**
```powershell
#Requires -RunAsAdministrator

function Install-EQ12Task {
    param([string]$TaskName = "EQ12 Parlay Morning")

    schtasks /create /tn $TaskName `
      /xml "C:\EQ12\tasks\eq12_parlay_morning.xml" /f

    Write-Host "✅ Task $TaskName registered" -ForegroundColor Green
}

function Set-EQ12Firewall {
    New-NetFirewallRule -DisplayName "EQ12 API" `
      -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
    Write-Host "✅ Firewall rule added for port 8000" -ForegroundColor Green
}
```

### **WireGuard VPN Switcher**
```powershell
function Switch-WireGuard {
    param(
        [ValidateSet("betting", "travel", "finance", "rotate")]
        [string]$Profile = "betting"
    )

    $ConfigPath = "C:\EQ12\configs\wireguard\wg-$Profile.conf"

    if ($Profile -eq "rotate") {
        $Profiles = @("betting", "travel", "finance")
        $Profile = $Profiles | Get-Random
        $ConfigPath = "C:\EQ12\configs\wireguard\wg-$Profile.conf"
    }

    wg-quick down $ConfigPath 2>$null
    wg-quick up $ConfigPath
    Write-Host "🌐 VPN switched to: $Profile" -ForegroundColor Cyan
}
```

---

## 3️⃣ Bash/Linux Patterns

### **User Scripts**
```bash
#!/bin/bash
# EQ12 User Operations

eq12_parlay() {
    echo "[*] Running Parlay Generator..."
    python3 ~/EQ12/eq12_telegram_master_bot.py --command parlay
    echo "✅ Parlay completed"
}

eq12_status() {
    echo "🎯 EQ12 System Status:"
    ps aux | grep python3 | grep eq12 | grep -v grep
}

eq12_logs() {
    tail -f ~/EQ12/logs/telegram_bot.log
}
```

### **Admin Scripts**
```bash
#!/bin/bash
# EQ12 Admin Operations (requires sudo)

eq12_update_system() {
    sudo apt update && sudo apt upgrade -y
    echo "✅ System updated"
}

eq12_firewall() {
    sudo ufw allow 8000/tcp
    sudo ufw enable
    echo "✅ Firewall configured"
}

eq12_vpn_switch() {
    local profile=${1:-betting}
    sudo wg-quick down ~/EQ12/configs/wireguard/wg-$profile.conf 2>/dev/null
    sudo wg-quick up ~/EQ12/configs/wireguard/wg-$profile.conf
    echo "🌐 VPN switched to: $profile"
}
```

### **Systemd Service Template**
```ini
[Unit]
Description=EQ12 %i Service
After=network.target

[Service]
Type=simple
User=eq12
WorkingDirectory=/home/eq12/EQ12
ExecStart=/usr/bin/python3 /home/eq12/EQ12/eq12_%i.py
Restart=always
RestartSec=10
Environment=EQ12_HOME=/home/eq12/EQ12

[Install]
WantedBy=multi-user.target
```

---

## 4️⃣ C# / Visual Studio Patterns

### **ASP.NET Core API Controller**
```csharp
[ApiController]
[Route("api/[controller]")]
public class ParlayController : ControllerBase
{
    private readonly ILogger<ParlayController> _logger;

    public ParlayController(ILogger<ParlayController> logger)
    {
        _logger = logger;
    }

    [HttpPost]
    public async Task<IActionResult> UpdateParlay([FromBody] ParlayTicket ticket)
    {
        try
        {
            var json = JsonSerializer.Serialize(ticket, new JsonSerializerOptions { WriteIndented = true });
            await System.IO.File.WriteAllTextAsync("C:\\EQ12\\data\\parlay.json", json);

            _logger.LogInformation("Parlay updated: {ParlayId}", ticket.Id);
            return Ok(new { ok = true, msg = "Parlay updated", id = ticket.Id });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update parlay");
            return StatusCode(500, new { error = "Failed to update parlay" });
        }
    }
}
```

### **Background Worker Service**
```csharp
public class EQ12WorkerService : BackgroundService
{
    private readonly ILogger<EQ12WorkerService> _logger;
    private readonly TimeSpan _interval = TimeSpan.FromMinutes(5);

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("EQ12 Worker Service started");

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                // Poll for Telegram updates, process commands
                await ProcessEQ12Commands();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in EQ12 worker cycle");
            }

            await Task.Delay(_interval, stoppingToken);
        }
    }
}
```

### **WPF Dashboard Snippet**
```xml
<Grid Background="Black">
    <StackPanel HorizontalAlignment="Center" VerticalAlignment="Center">
        <TextBlock Text="{Binding ParlayPayout}" FontSize="48"
                   Foreground="Lime" HorizontalAlignment="Center"/>
        <TextBlock Text="Today's Parlay Estimate" FontSize="16"
                   Foreground="White" HorizontalAlignment="Center"/>
    </StackPanel>
</Grid>
```

---

## 5️⃣ DevOps & CI/CD Patterns

### **Security-Hardened .gitignore**
```gitignore
# EQ12 Security Exclusions
keys/
credentials.*
*.env*
logs/
snips/
data/
*.key
*.pem

# Python
__pycache__/
*.pyc
*.pyo
venv/
.pytest_cache/

# System
Thumbs.db
.DS_Store
Desktop.ini
```

### **GitHub Actions Security Pipeline**
```yaml
name: EQ12 Security CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Security Scan
      run: |
        # Check for exposed secrets
        if find . -name "*.env*" -o -name "credentials.*" | grep -v .gitignore; then
          echo "❌ Exposed secrets detected!"
          exit 1
        fi

        # Run bandit security scanner
        pip install bandit
        bandit -r . --severity-level medium

    - name: Test Suite
      run: |
        pip install pytest
        pytest tests/ -v
```

### **Pre-Commit Security Hook**
```bash
#!/bin/bash
# .git/hooks/pre-commit

if git diff --cached --name-only | grep -E '(keys/|credentials\.|\.env)'; then
  echo "🚨 BLOCKED: Sensitive files detected in commit"
  echo "Files:"
  git diff --cached --name-only | grep -E '(keys/|credentials\.|\.env)'
  exit 1
fi

echo "✅ Security check passed"
```

---

## 6️⃣ GPT-5 & AI Integration Patterns

### **GPT-5 Developer Controls Implementation**
```python
from openai import OpenAI

class EQ12GPTController:
    def __init__(self):
        self.client = OpenAI()

    def generate_parlay_minimal(self, sport: str):
        """Fast parlay generation with minimal reasoning"""
        response = self.client.responses.create(
            model="gpt-5-mini",
            input=f"Generate 5-leg {sport} parlay. Return JSON only.",
            reasoning={"effort": "minimal"},
            text={"verbosity": "low"}
        )
        return response

    def generate_detailed_analysis(self, data: dict):
        """Comprehensive analysis with high verbosity"""
        response = self.client.responses.create(
            model="gpt-5",
            input="Analyze this betting data and provide strategy recommendations",
            text={"verbosity": "high"},
            reasoning={"effort": "high"}
        )
        return response
```

### **Context-Free Grammar for SQL Generation**
```python
sql_grammar = """
    start: "SELECT" SP select_list SP "FROM" SP table SP "WHERE" SP filters SP "LIMIT" SP NUMBER ";"
    select_list: column ("," SP column)*
    column: IDENTIFIER
    table: IDENTIFIER
    filters: filter (SP "AND" SP filter)*
    filter: IDENTIFIER SP operator SP value
    operator: ">" | "=" | "<"
    value: NUMBER | STRING

    IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
    NUMBER: /[0-9]+/
    STRING: /'[^']*'/
    SP: " "
"""

# Usage in tool definition
tools = [{
    "type": "custom",
    "name": "sql_generator",
    "description": "Generate SQL queries for EQ12 database",
    "format": {
        "type": "grammar",
        "syntax": "lark",
        "definition": sql_grammar
    }
}]
```

### **Specialist GPT Integration**
```python
class EQ12GPTOrchestrator:
    def __init__(self):
        self.specialist_gpts = {
            "sports": "EdgeGodParlays GPT",
            "travel": "TravelDeals GPT",
            "finance": "FinanceGuru GPT",
            "content": "ContentCreator GPT"
        }

    def route_request(self, category: str, request: str):
        """Route requests to appropriate specialist GPT"""
        gpt_name = self.specialist_gpts.get(category)
        if gpt_name:
            return f"Routing to {gpt_name}: {request}"
        return "Using general GPT-5 orchestrator"
```

---

## 7️⃣ Security & Networking Patterns

### **WireGuard Profile Template**
```ini
[Interface]
PrivateKey = REPLACE_WITH_PRIVATE_KEY
Address = 10.0.0.2/32
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = REPLACE_WITH_SERVER_PUBLIC_KEY
Endpoint = vpn.example.com:51820
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
```

### **ngrok Configuration**
```yaml
version: "2"
authtoken: REPLACE_WITH_NGROK_TOKEN

tunnels:
  eq12-api:
    proto: http
    addr: 8000
    bind_tls: true

  eq12-dashboard:
    proto: http
    addr: 3000
    subdomain: eq12-dash
```

### **Network Security Functions**
```python
import ipaddress
import requests

def validate_api_source(request_ip: str) -> bool:
    """Validate API requests from trusted sources"""
    trusted_ranges = [
        ipaddress.ip_network("127.0.0.0/8"),    # localhost
        ipaddress.ip_network("10.0.0.0/8"),     # VPN range
        ipaddress.ip_network("192.168.0.0/16")  # local network
    ]

    try:
        ip = ipaddress.ip_address(request_ip)
        return any(ip in network for network in trusted_ranges)
    except ValueError:
        return False

def rotate_ngrok_tunnel():
    """Rotate ngrok tunnel for security"""
    import subprocess
    subprocess.run(["ngrok", "kill"])
    subprocess.run(["ngrok", "start", "eq12-api"], background=True)
```

---

## 8️⃣ Data Engineering & Analysis Patterns

### **ETL with Pandas**
```python
import pandas as pd
import json
from datetime import datetime

def process_parlay_history():
    """Process parlay data for analysis"""
    # Load parlay data
    with open("C:/EQ12/data/parlay.json", "r") as f:
        data = json.load(f)

    # Normalize to DataFrame
    df = pd.json_normalize(data["legs"])
    df["timestamp"] = datetime.now()

    # Calculate metrics
    df["expected_value"] = df["odds"] * df["probability"] - 1
    df["kelly_fraction"] = (df["probability"] * df["odds"] - 1) / (df["odds"] - 1)

    # Save analysis
    df.to_csv("C:/EQ12/logs/parlay_analysis.csv", index=False)
    return df

def monte_carlo_parlay_simulation(probabilities: list, payout: float, trials: int = 100000):
    """Simulate parlay outcomes using Monte Carlo"""
    import random

    wins = 0
    total_invested = trials  # Assume $1 per trial

    for _ in range(trials):
        if all(random.random() < p for p in probabilities):
            wins += 1

    total_return = wins * payout
    roi = (total_return - total_invested) / total_invested * 100

    return {
        "win_rate": wins / trials,
        "expected_return": total_return,
        "roi_percentage": roi,
        "breakeven_probability": 1 / payout
    }
```

### **Visualization with Matplotlib**
```python
import matplotlib.pyplot as plt
import seaborn as sns

def create_roi_dashboard():
    """Generate ROI visualization for Apple TV"""
    plt.style.use('dark_background')
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 9))

    # Parlay performance over time
    ax1.plot(df["date"], df["roi"], color='lime', linewidth=2)
    ax1.set_title("Parlay ROI Over Time", color='white', fontsize=16)
    ax1.set_facecolor('black')

    # Win rate by sport
    sport_wins = df.groupby("sport")["win"].mean()
    ax2.bar(sport_wins.index, sport_wins.values, color=['gold', 'silver', 'orange'])
    ax2.set_title("Win Rate by Sport", color='white', fontsize=16)

    plt.tight_layout()
    plt.savefig("C:/EQ12/data/dashboard.png", facecolor='black', dpi=150)
    plt.close()
```

---

## 9️⃣ Media & Content Generation Patterns

### **Sora Video Prompt Templates**
```python
def generate_parlay_hype_reel(parlay_data: dict):
    """Generate Sora prompt for parlay hype video"""
    prompt = f"""
    Create a 15-second sports betting hype reel:
    - Open with stadium lights turning on at night
    - Show {parlay_data['sport']} action highlights
    - Overlay glowing text: "{parlay_data['description']}"
    - Display payout estimate: "${parlay_data['payout']:.2f}"
    - End with EQ12 logo pulsing with gold effect
    - Style: Cinematic, high energy, dark theme with neon accents
    """
    return prompt

def generate_travel_deal_video(deal_data: dict):
    """Generate Sora prompt for travel deal content"""
    prompt = f"""
    Create a 10-second travel deal showcase:
    - Aerial view of {deal_data['destination']}
    - Smooth transition to price overlay: "${deal_data['price']}"
    - QR code appears in corner
    - Text animation: "Book Now - Limited Time"
    - Upbeat, wanderlust style with bright colors
    """
    return prompt
```

### **ffmpeg Automation**
```bash
#!/bin/bash
# EQ12 Video Processing Pipeline

add_parlay_overlay() {
    local input_video=$1
    local parlay_text=$2
    local output_video=$3

    ffmpeg -i "$input_video" \
      -vf "drawtext=text='$parlay_text':x=50:y=50:fontsize=48:fontcolor=gold:box=1:boxcolor=black@0.8" \
      -c:a copy "$output_video"
}

create_qr_overlay() {
    local url=$1
    local output_image=$2

    # Generate QR code
    python3 -c "
import qrcode
qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data('$url')
qr.make(fit=True)
img = qr.make_image(fill_color='white', back_color='transparent')
img.save('$output_image')
"
}
```

### **Social Media Automation**
```python
import requests
from datetime import datetime

class EQ12ContentPipeline:
    def __init__(self):
        self.platforms = {
            "telegram": self.post_telegram,
            "discord": self.post_discord,
            "instagram": self.post_instagram
        }

    def auto_post_parlay(self, parlay_data: dict):
        """Automatically post parlay across platforms"""
        content = self.format_parlay_content(parlay_data)

        for platform, post_func in self.platforms.items():
            try:
                post_func(content)
                print(f"✅ Posted to {platform}")
            except Exception as e:
                print(f"❌ Failed to post to {platform}: {e}")

    def format_parlay_content(self, data: dict):
        """Format parlay for social media"""
        return f"""
🎯 TODAY'S PARLAY PICK

🏆 {data['sport']} {len(data['legs'])}-Leg Special
💰 Potential Payout: ${data['payout']:.2f}
📊 Combined Odds: {data['total_odds']}

{self.format_legs(data['legs'])}

🚀 Powered by EQ12 Analytics
        """.strip()
```

---

## 🔟 Marketplace & Affiliate Patterns

### **AliDropship Integration**
```python
import requests
from typing import List, Dict

class EQ12CommerceEngine:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.alidropship.com"

    def search_trending_products(self, category: str = "pet supplies") -> List[Dict]:
        """Search for trending products to dropship"""
        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = requests.get(
            f"{self.base_url}/products/trending",
            headers=headers,
            params={"category": category, "limit": 50}
        )

        products = response.json()

        # Filter for profitable products (3x markup minimum)
        profitable = []
        for product in products:
            cost = float(product['cost'])
            market_price = cost * 3  # 3x markup

            if market_price < 50:  # Sweet spot for impulse buys
                product['suggested_price'] = market_price
                product['profit_margin'] = market_price - cost
                profitable.append(product)

        return profitable

    def generate_seo_listing(self, product: Dict) -> Dict:
        """Generate SEO-optimized product listing"""
        # Use GPT-5 for SEO rewriting
        prompt = f"""
        Rewrite this product title for maximum SEO impact:
        Original: {product['title']}
        Category: {product['category']}

        Make it compelling, include power words, optimize for search.
        """

        # Implementation would call GPT-5 here
        return {
            "title": "Premium CBD Calming Drops for Anxious Dogs | Fast Relief | 300mg",
            "description": self.generate_product_description(product),
            "tags": ["pet wellness", "cbd", "calming", "anxiety relief"]
        }
```

### **Cross-Platform Listing Automation**
```python
def push_to_multiple_platforms(product: Dict):
    """List product across eBay, Amazon, Etsy"""
    platforms = {
        "ebay": EBayAPI(),
        "amazon": AmazonSPAPI(),
        "etsy": EtsyAPI()
    }

    for platform_name, api in platforms.items():
        try:
            listing = adapt_product_for_platform(product, platform_name)
            result = api.create_listing(listing)
            print(f"✅ Listed on {platform_name}: {result['listing_id']}")
        except Exception as e:
            print(f"❌ Failed to list on {platform_name}: {e}")

def calculate_affiliate_commissions(sales_data: List[Dict]) -> Dict:
    """Calculate affiliate earnings"""
    total_commission = 0
    platform_breakdown = {}

    for sale in sales_data:
        commission = sale['amount'] * sale['commission_rate']
        total_commission += commission

        platform = sale['platform']
        if platform not in platform_breakdown:
            platform_breakdown[platform] = 0
        platform_breakdown[platform] += commission

    return {
        "total_commission": total_commission,
        "platform_breakdown": platform_breakdown,
        "average_order_value": sum(s['amount'] for s in sales_data) / len(sales_data)
    }
```

---

## 1️⃣1️⃣ Testing & Quality Assurance Patterns

### **pytest Test Suite**
```python
import pytest
from unittest.mock import Mock, patch
from eq12_telegram_master_bot import TelegramBot

class TestEQ12TelegramBot:
    @pytest.fixture
    def bot(self):
        return TelegramBot(token="test_token")

    def test_parlay_generation(self, bot):
        """Test parlay generation functionality"""
        result = bot.generate_parlay("MLB", 5)

        assert result is not None
        assert len(result['legs']) == 5
        assert 'total_odds' in result
        assert result['total_odds'] > 1

    @patch('requests.post')
    def test_telegram_message_send(self, mock_post, bot):
        """Test Telegram message sending"""
        mock_post.return_value.status_code = 200

        result = bot.send_message("test message", "123456789")

        assert result is True
        mock_post.assert_called_once()

    def test_odds_api_integration(self, bot):
        """Test OddsAPI integration"""
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                "data": [{"home_team": "Yankees", "away_team": "Red Sox"}]
            }

            games = bot.fetch_games("MLB")
            assert len(games) > 0
```

### **Mock API Server for Testing**
```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Mock server for testing
mock_app = FastAPI()

@mock_app.get("/odds/{sport}")
def mock_odds(sport: str):
    return {
        "sport": sport,
        "games": [
            {
                "home_team": "Team A",
                "away_team": "Team B",
                "odds": {"home": -150, "away": +130}
            }
        ]
    }

@mock_app.post("/api/parlay")
def mock_parlay_update(data: dict):
    return {"status": "success", "id": "mock_123"}

# Test client
client = TestClient(mock_app)

def test_mock_integration():
    response = client.get("/odds/MLB")
    assert response.status_code == 200
    assert response.json()["sport"] == "MLB"
```

### **Load Testing with Locust**
```python
from locust import HttpUser, task, between

class EQ12LoadTest(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_parlay(self):
        """Test parlay endpoint (most common operation)"""
        self.client.get("/api/parlay")

    @task(2)
    def post_parlay(self):
        """Test parlay updates"""
        parlay_data = {
            "legs": [{"team": "Yankees", "bet_type": "ML", "odds": -150}],
            "stake": 100
        }
        self.client.post("/api/parlay", json=parlay_data)

    @task(1)
    def health_check(self):
        """Test system health"""
        self.client.get("/health")

    def on_start(self):
        """Setup for each user"""
        self.client.headers.update({"X-API-Key": "test-key"})
```

### **Automated Health Monitoring**
```python
import requests
import time
from datetime import datetime

class EQ12HealthMonitor:
    def __init__(self):
        self.endpoints = [
            "http://localhost:8000/health",
            "http://localhost:3000/tv/health",
            "http://localhost:5000/api/health"
        ]

    def check_system_health(self) -> Dict:
        """Comprehensive system health check"""
        results = {}

        for endpoint in self.endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                results[endpoint] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                results[endpoint] = {
                    "status": "down",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }

        return results

    def alert_if_unhealthy(self, health_data: Dict):
        """Send alerts for unhealthy services"""
        for endpoint, data in health_data.items():
            if data['status'] != 'healthy':
                self.send_alert(f"🚨 {endpoint} is {data['status']}")
```

---

## ✅ Golden Rules & Best Practices

### **Security First**
1. **Never hardcode secrets** - Use `keys/credentials.json` or environment variables
2. **Validate all inputs** - Sanitize user data and API responses
3. **Log security events** - Track authentication, authorization, and access attempts
4. **Encrypt sensitive data** - Use EQ12CredentialManager for all credentials
5. **Network security** - Validate IP ranges, use VPN profiles, rotate tunnels

### **Code Quality Standards**
1. **Follow naming conventions**: `eq12_[service]_[type].[ext]`
2. **Modular architecture** - Functions over monoliths, clear separation of concerns
3. **Comprehensive logging** - Structured logs with timestamps and context
4. **Error handling** - Graceful degradation, meaningful error messages
5. **Type hints** - Use Python type hints, C# strong typing

### **Platform Compatibility**
1. **Admin vs User separation** - Respect privilege boundaries on Windows/Linux
2. **Cross-platform paths** - Use Path objects, environment variables
3. **Service management** - PowerShell services on Windows, systemd on Linux
4. **Network configuration** - Platform-specific firewall and VPN management

### **Testing & Deployment**
1. **Test before production** - Unit tests, integration tests, load tests
2. **Automated CI/CD** - Security scanning, linting, automated deployments
3. **Health monitoring** - Endpoint checks, performance metrics, alerting
4. **Rollback procedures** - Quick recovery mechanisms for failed deployments

### **GPT-5 Integration Guidelines**
1. **Use verbosity control** - `low` for speed, `high` for comprehensive output
2. **Leverage minimal reasoning** - Fast responses for simple classification tasks
3. **Grammar constraints** - Use CFG for strict output formatting requirements
4. **Specialist routing** - Route domain-specific tasks to appropriate GPTs

---

## 🚀 Quick Reference Commands

### **Development Workflow**
```bash
# Start EQ12 development environment
python eq12_production_launcher.py --dev

# Run security scan
python eq12_security_scanner.py --scan-all

# Generate parlay via CLI
python eq12_telegram_master_bot.py --generate-parlay MLB 5

# Health check all services
python -c "from eq12_health_monitor import check_all; check_all()"
```

### **Deployment Commands**
```powershell
# Windows deployment
.\eq12_admin.ps1 -Action Deploy -Environment Production

# Linux deployment
sudo ./eq12_admin.sh deploy production
```

### **Monitoring & Debugging**
```bash
# View logs
tail -f C:/EQ12/logs/*.log

# Check system status
eq12_status

# Restart services
eq12_restart_all
```

---

**🎯 This master cookbook now provides comprehensive, battle-tested patterns for all EQ12 development scenarios across 11 specialized domains!**

**📝 Keep this file in your repo root - Copilot and GPT-5 will reference it as the authoritative guide for EQ12 automation development.**
