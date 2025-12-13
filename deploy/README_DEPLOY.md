# 🚀 EQ12 Cluster Deployment Guide (Lenovo M70q)

**Target Hardware**: Lenovo ThinkCentre M70q
**OS**: Windows 10/11 Pro (Recommended) or Linux (Ubuntu 22.04)
**Role**: Dedicated AI & Automation Server

---

## 📦 Phase 1: Preparation (On Current Machine)

1.  **Run the Packaging Script**:
    Open PowerShell and run:
    ```powershell
    .\deploy\package_for_transfer.ps1
    ```
    This will create a `EQ12_DEPLOY_PACKAGE` folder in the root directory.

2.  **Transfer**:
    Copy the entire `EQ12_DEPLOY_PACKAGE` folder to a USB drive or use a network share to move it to the Lenovo M70q.

---

## 🛠️ Phase 2: Installation (On Lenovo M70q)

1.  **Prerequisites**:
    *   Install **Python 3.10+** (Ensure "Add Python to PATH" is checked).
    *   Install **Git** (Optional, but recommended).
    *   Install **VS Code** (Recommended for management).

2.  **Setup**:
    *   Copy the `EQ12_DEPLOY_PACKAGE` folder to `C:\EQ12`.
    *   Open PowerShell as Administrator.
    *   Navigate to the folder: `cd C:\EQ12`
    *   Run the setup script:
        ```powershell
        .\setup_lenovo.ps1
        ```

3.  **Configuration**:
    *   The setup script will create a `.env` file.
    *   Open `.env` and verify your API Keys (OpenRouter, Odds API).

---

## 🤖 Phase 3: Activation

1.  **Test the Brain**:
    ```powershell
    python src/gpt_analyzer.py
    ```

2.  **Test the Self-Learning Loop**:
    ```powershell
    python src/post_mortem.py logs/gpt_picks_20251205.json
    ```

3.  **Start the Scheduler (Optional)**:
    *   Use Task Scheduler to run `src/gpt_analyzer.py` every morning at 8:00 AM.
    *   Use Task Scheduler to run `src/post_mortem.py` every night at 11:00 PM.

---

## 📂 Directory Structure (Post-Deployment)

*   `C:\EQ12\`
    *   `src/` - Core Engines (Betting, Meta-Prompter, Code-Genesis)
    *   `config/` - Prompts & Memory
    *   `logs/` - Data storage
    *   `n8n/` - Workflow files
    *   `venv/` - Python Virtual Environment
