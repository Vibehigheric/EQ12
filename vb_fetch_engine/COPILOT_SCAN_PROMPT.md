# COPILOT SYSTEM SCAN AND HARDWARE UPGRADE ANALYSIS

**Paste this directly into GitHub Copilot Chat (VS Code Copilot sidebar) or .continue**

```
You are now operating as a System Diagnostic and Hardware Optimization Expert.

Scan my entire workspace and development environment. Focus on:
- Machine specs
- Python 3.12 execution behavior
- Pylance crashes (EPIPE, channel closed)
- PowerShell file corruption issues
- Encoding drift (UTF8 vs ANSI)
- Dev Container prompts and Docker state
- VS Code configuration integrity
- Directory structure: C:\EQ12, C:\EQ12\scripts, usb_builds, logs
- __pycache__ patterns
- Any misconfigured GitHub or .devcontainer files
- My heavy multi-process workload

Perform the following tasks:

1. Analyze the likely hardware bottlenecks under my current workflow.
2. Recommend SPECIFIC hardware upgrades based on actual constraints.
3. Evaluate whether I should upgrade:
   - RAM
   - NVMe drive
   - CPU generation
   - USB expansion
   - External accelerators (Coral, USB TPU, GPUs)
   - Raspberry Pi offloading
   - Network bandwidth
4. Identify what would MOST impact:
   - Python execution speed
   - VS Code responsiveness
   - Pylance stability
   - Terminal speed
   - Container build times
   - Overall EQ12 automation load

5. Based on all detected patterns, produce:
   - A Hardware Upgrade Priority List (1 through 10)
   - A Software Stability Improvement List
   - A specific set of VS Code settings to stabilize Pylance
   - A recommended hardware budget (low, mid, high tiers)
   - A developer-grade action plan for stabilizing corrupted scripts

6. Output the final report in the following sections:

   SECTION A: System Scan Summary  
   SECTION B: Detected Bottlenecks  
   SECTION C: Hardware Upgrade Recommendations  
   SECTION D: Software and Settings Fixes  
   SECTION E: Final Action Plan (Highest Impact First)

Use only ASCII. No emoji. No Unicode beyond plain text.
Be extremely detailed and technical.
Assume I am running heavy automation (EQ12 stack).
```

## WHAT THIS COPILOT PROMPT DOES

When you paste this into Copilot Chat, it will:

1. **Scan your workspace** for system health indicators
2. **Detect Pylance crash patterns** (EPIPE errors, channel closed)
3. **Analyze PowerShell corruption** (parse errors, encoding issues)
4. **Identify hardware bottlenecks** (RAM, CPU, NVMe, USB)
5. **Recommend specific upgrades** with priority ranking
6. **Generate VS Code stability fixes** for Pylance
7. **Output ASCII-safe report** (no emoji, no corruption)

## EXPECTED OUTPUT SECTIONS

### SECTION A: System Scan Summary
- Workspace size and file count
- Python 3.12 configuration
- Pylance version and state
- PowerShell script inventory
- Current hardware profile

### SECTION B: Detected Bottlenecks
- Memory pressure (RAM usage patterns)
- Disk I/O constraints (NVMe vs HDD)
- CPU throttling under heavy load
- USB bandwidth limitations
- VS Code extension conflicts

### SECTION C: Hardware Upgrade Recommendations
Prioritized list with specific models:
1. RAM upgrade (e.g., 32GB → 64GB DDR4-3200)
2. NVMe upgrade (e.g., Samsung 990 Pro 2TB)
3. USB 3.2 Gen 2 expansion card
4. Google Coral Edge TPU
5. Raspberry Pi 5 cluster (offload tasks)
6. GPU upgrade for ML workloads
7. 10GbE network card
8. CPU upgrade (specific model recommended)
9. Motherboard with more PCIe lanes
10. Improved cooling system

### SECTION D: Software and Settings Fixes
- VS Code settings.json optimizations
- Pylance memory limits
- Python path configuration
- PowerShell execution policy
- UTF-8 encoding enforcement
- Extension disable recommendations

### SECTION E: Final Action Plan
Step-by-step prioritized action list:
1. Immediate fixes (software, free)
2. Low-cost upgrades ($0-$100)
3. Mid-tier upgrades ($100-$500)
4. High-impact upgrades ($500+)
5. Long-term infrastructure improvements

## ALTERNATIVE: MANUAL HARDWARE SCAN

If Copilot doesn't provide enough detail, use the VB.NET tools in this repo:

```cmd
# Log analysis
Eq12LogInspector.exe C:\EQ12\logs

# USB drive inventory
UsbInspector.exe

# ASCII corruption scan
Eq12AsciiValidator.exe C:\EQ12

# System banner
Eq12BannerGenerator.exe diagnostic
```

## HARDWARE UPGRADE TIERS

### LOW TIER ($0-$200)
- 16GB → 32GB RAM
- USB 3.0 hub with power
- SSD cache drive (256GB)
- Better thermal paste

### MID TIER ($200-$800)
- 32GB → 64GB RAM
- 1TB NVMe (Samsung 980 Pro)
- Google Coral TPU ($60)
- Raspberry Pi 5 8GB ($80)
- PCIe USB 3.2 card

### HIGH TIER ($800-$2000)
- 64GB → 128GB RAM
- 2TB NVMe (Samsung 990 Pro)
- AMD Ryzen 9 7950X CPU upgrade
- NVIDIA RTX 4060 Ti
- 10GbE network card
- Multiple Coral TPUs
- Raspberry Pi cluster (5 units)

## COPILOT FOLLOW-UP PROMPTS

After getting the initial report, ask Copilot:

**For hardware specifics:**
```
Based on my current Intel i7-10700K and DDR4 motherboard, recommend exact RAM and NVMe models compatible with my system. Include Amazon/Newegg links.
```

**For Pylance stability:**
```
Generate a complete VS Code settings.json file optimized for Pylance stability with Python 3.12 and heavy automation workloads.
```

**For PowerShell corruption fixes:**
```
Create a PowerShell script that validates all .ps1 files for parse errors, missing braces, and encoding issues. Include auto-fix capability.
```

**For USB empire optimization:**
```
Design a USB drive allocation strategy for 5 drives (D: through H:) supporting development, backup, Ventoy boot, and distribution packages.
```

## ASCII-SAFE GUARANTEE

This prompt is:
- ✅ Pure ASCII (no emoji, no Unicode)
- ✅ Copy-paste safe
- ✅ Windows terminal compatible
- ✅ No encoding corruption risk
- ✅ PowerShell friendly
- ✅ Copilot optimized

## INTEGRATION WITH EQ12 STACK

Once you get Copilot's recommendations, integrate them with:
- **LoopGuard system** - monitor hardware-induced timeouts
- **Fetch Engine** - optimize API call performance
- **Parlay Validator** - reduce validation overhead
- **Log Inspector** - track hardware-related errors
- **ASCII Validator** - prevent encoding corruption

---

**This is your hardware upgrade roadmap generator.**

Paste into Copilot, review recommendations, implement prioritized list.
