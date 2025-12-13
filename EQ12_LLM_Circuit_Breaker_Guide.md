# EQ12 LLM Circuit Breaker Usage Guide

## Overview
The EQ12 LLM circuit breaker system prevents quota exhaustion by implementing a cross-process offline mode that stops all OpenAI API calls when quota issues are detected.

## Key Components

### 1. LLMOffline Circuit Breaker (`eq12_llm_offline.py`)
- Cross-process sentinel file: `C:\EQ12\logs\.llm_offline.json`
- Automatic 24-hour cooldown on quota exhaustion
- Manual control methods available

### 2. Updated Error Boundary (`eq12_error_boundary.py`)
- Integrates with LLMOffline for immediate offline switching
- Disables OpenAI auto-retries (`max_retries=0`)
- Prevents remote fallback calls when offline

## Usage Commands

### Check Current Status
```powershell
python -c "from eq12_llm_offline import LLMOffline; print('Offline:', LLMOffline.is_offline()); print('Status:', LLMOffline.status())"
```

### Force Offline Mode (Emergency)
```powershell
# Set environment variable
$env:EQ12_USE_LLM = "0"

# Trip circuit breaker for 24 hours
python -c "from eq12_llm_offline import LLMOffline; LLMOffline.trip(reason='manual_override')"

# Stop all Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
```

### Re-enable LLM Calls (After Quota Restoration)
```powershell
# Reset environment variable
$env:EQ12_USE_LLM = "1"

# Reset circuit breaker
python -c "from eq12_llm_offline import LLMOffline; LLMOffline.reset()"

# Stop all Python processes to reload clean
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
```

### Test Offline Mode
```powershell
$env:EQ12_USE_LLM = "0"
python -c "
from eq12_error_boundary import GPT5ErrorBoundary
import asyncio

async def test():
    boundary = GPT5ErrorBoundary()
    result = await boundary.safe_call('Test prompt')
    print(f'Result: {result}')

asyncio.run(test())
"
```

## Environment Variables

- `EQ12_USE_LLM`: Set to "0" to disable LLM calls, "1" to enable
- `OPENAI_API_KEY`: Your OpenAI API key (when enabled)

## Automatic Behavior

### When 429 `insufficient_quota` Occurs:
1. Circuit breaker trips immediately
2. Cross-process sentinel created for 24 hours
3. All subsequent LLM calls return offline responses
4. No more API requests sent

### Offline Response Format:
```
"🛡️ Offline mode: local heuristics/results will be used."
```

## Files Modified

### Core Circuit Breaker:
- `eq12_llm_offline.py` - New cross-process circuit breaker
- `eq12_error_boundary.py` - Updated with LLMOffline integration

### OpenAI Clients Patched (max_retries=0):
- `eq12_error_boundary.py`
- `scripts/eq12_url_scanner.py`
- `scripts/eq12_enhanced_ai.py`
- `eq12_advanced_optimizer.py`
- `eq12_openai_optimizer.py`

## Monitoring

### Check Health Status:
```powershell
python -c "
from eq12_llm_offline import LLMOffline
status = LLMOffline.status()
if status['offline']:
    print(f'🔴 OFFLINE until {status[\"until\"]} - Reason: {status[\"reason\"]}')
else:
    print('🟢 ONLINE - LLM calls enabled')
"
```

### View Sentinel File:
```powershell
if (Test-Path "C:\EQ12\logs\.llm_offline.json") {
    Get-Content "C:\EQ12\logs\.llm_offline.json" | ConvertFrom-Json | Format-List
}
```

## Integration with Existing Code

All existing EQ12 components automatically respect the circuit breaker through the updated `GPT5ErrorBoundary`. No code changes required for individual scripts.

## Troubleshooting

### If Still Getting 429 Errors:
1. Verify environment variable: `echo $env:EQ12_USE_LLM`
2. Check circuit breaker status
3. Stop all Python processes: `Get-Process python | Stop-Process -Force`
4. Manually trip circuit: `python -c "from eq12_llm_offline import LLMOffline; LLMOffline.trip()"`

### Re-enable After Quota Funding:
1. Set `$env:EQ12_USE_LLM = "1"`
2. Reset circuit: `python -c "from eq12_llm_offline import LLMOffline; LLMOffline.reset()"`
3. Restart processes

This system ensures **zero OpenAI API calls** when offline mode is active, preventing further quota depletion.
