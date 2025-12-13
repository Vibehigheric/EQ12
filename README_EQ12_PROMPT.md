**EQ12 Copilot Master Prompt**

- **File:** `EQ12_master_copilot_prompt.txt`  contains the exact EQ12 God-Mode prompt block.

- **One-line PowerShell (copy to clipboard):**

```powershell
Get-Content C:\EQ12\EQ12_master_copilot_prompt.txt -Raw | Set-Clipboard
```

- **How to use:**
  - Open `Copilot Chat` or `Copilot in VS Code` and paste (Ctrl+V) the clipboard contents into the chat input.
  - When Copilot asks for confirmation, you can type: `EQ12 Copilot Mode: ONLINE` to match the prompt's expected acknowledgement.

- **Notes:**
  - This folder location is the canonical copy. Keep it under source control if you want versioning.
  - If you prefer to view or edit the prompt before pasting, open `C:\EQ12\EQ12_master_copilot_prompt.txt` in VS Code.

- **Optional quick check (PowerShell):**

```powershell
# Verify files exist and show first 3 lines of the prompt
if (Test-Path C:\EQ12\EQ12_master_copilot_prompt.txt) { Get-Content C:\EQ12\EQ12_master_copilot_prompt.txt -TotalCount 3 } else { Write-Host "Prompt file missing" }
``` 

- **Permission hint:**
  - No elevated privileges are needed to copy/paste the prompt. If you script VS Code repairs later, you may need to run PowerShell as Administrator (`-RunAsAdministrator`).
