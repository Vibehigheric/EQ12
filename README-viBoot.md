README - viBoot integration for EQ12

Purpose
-------
Provide a safe, read-only workflow to stage a VM from the latest Macrium Reflect full backup image (via viBoot), run idempotent tests inside that VM, collect logs, then tear down the VM.

Files created
-------------
- `C:\EQ12\scripts\eq12_viboot_stage.ps1` - main staging script (PowerShell, CmdletBinding)
- `C:\EQ12\configs\viboot_config.example.json` - example configuration

Safety notes
------------
- This integration does NOT modify backup images. All operations on images are read-only.
- If an image is missing or a VM fails to boot, the script exits with JSON: `{ "ok": false, "error": "message" }`.
- Tests executed inside the VM must be idempotent and must not write to production/live data directories.

Pre-requisites
-------------
- Macrium Reflect with viBoot installed and licensed on the host.
- Hyper-V or VirtualBox available and enabled.
- Administrative privileges to manage VMs and run PowerShell scripts.

Usage
-----
1. Review and copy `C:\EQ12\configs\viboot_config.example.json` to `C:\EQ12\configs\viboot_config.json` and adjust RAM/CPU and test commands.
2. Run from an elevated PowerShell prompt:

   powershell -ExecutionPolicy Bypass -File "C:\EQ12\scripts\eq12_viboot_stage.ps1" -ConfigPath "C:\EQ12\configs\viboot_config.json"

What the script does
---------------------
1. Finds the latest full backup image under the configured backup directory.
2. Attempts to use viBoot to mount and start a VM from that image using Hyper-V or VirtualBox (preference order).
3. Waits for the VM to boot and become accessible via PowerShell Direct (Hyper-V) or WinRM.
4. Runs configured test commands inside the VM (dry-run / checks allowed).
5. Collects test output and logs into `vm_logs_path` (on host). If `retain_vm_logs` is true, logs are kept; otherwise they are removed after collection.
6. Shuts down and removes the staged VM.

Troubleshooting
---------------
- If viBoot or Macrium CLI is not installed or not available, the script fails with an explanatory JSON error.
- For long-running boots, increase the `BootTimeoutSec` value in the configuration.

Support
-------
If you want I can add an option to keep the VM running for interactive debugging instead of automatic teardown (requires explicit consent).
