#!/usr/bin/env python3
"""
EQ12 Expert Kelly Integration Setup Script
Complete initialization of Kelly Criterion as central bankroll management system
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_expert_kelly_system():
    """Complete setup of Expert Kelly Integration System"""

    print("🚀 EQ12 EXPERT KELLY INTEGRATION SYSTEM SETUP")
    print("=" * 60)

    # 1. Create directory structure
    print("\n📁 Creating directory structure...")
    create_directory_structure()

    # 2. Initialize Azure ML configuration
    print("\n☁️ Setting up Azure ML workspace configuration...")
    setup_azure_ml_configuration()

    # 3. Create Kelly bankroll data files
    print("\n🧮 Initializing Kelly bankroll management...")
    initialize_kelly_data_files()

    # 4. Setup environment configuration
    print("\n⚙️ Creating environment configuration...")
    create_environment_configs()

    # 5. Create launch scripts
    print("\n🚀 Creating launch scripts...")
    create_launch_scripts()

    # 6. Setup CLI tools
    print("\n🔧 Setting up CLI tools...")
    setup_cli_tools()

    # 7. Create documentation
    print("\n📖 Generating documentation...")
    create_expert_kelly_documentation()

    # 8. Validate setup
    print("\n✅ Validating setup...")
    validate_setup()

    print("\n🎉 Expert Kelly Integration System setup complete!")
    print_usage_instructions()


def create_directory_structure():
    """Create complete directory structure"""

    directories = [
        "data",
        "data/bankrolls",
        "data/azure-ml",
        "data/correlations",
        "configs",
        "configs/environments",
        "configs/azure-ml",
        ".azureml",
        ".azureml/environments",
        ".azureml/compute",
        ".azureml/pipelines",
        ".azureml/deployments",
        "logs/kelly",
        "logs/azure-ml",
        "scripts/kelly",
        "scripts/azure-ml",
        "cli/kelly",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")


def setup_azure_ml_configuration():
    """Setup Azure ML workspace configurations"""

    # Create Azure ML manager to generate configs
    try:
        from src.core.azure_ml_manager import AzureMLWorkspaceManager

        manager = AzureMLWorkspaceManager()
        manager.generate_azureml_folder_structure()

        logger.info("Azure ML workspace configuration created")

    except ImportError:
        logger.warning("Azure ML manager not available - creating minimal config")
        create_minimal_azure_config()


def create_minimal_azure_config():
    """Create minimal Azure ML configuration"""

    environments = ["dev", "staging", "production"]

    for env in environments:
        config = {
            "subscription_id": "${AZURE_SUBSCRIPTION_ID}",
            "resource_group": f"eq12-sports-betting-{env}-rg",
            "workspace_name": f"eq12sportsbetting{env}",
            "location": "eastus2",
        }

        config_file = Path(f".azureml/config-{env}.json")
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)


def initialize_kelly_data_files():
    """Initialize Kelly bankroll data files for each environment"""

    environments = ["dev", "staging", "production"]

    for env in environments:
        bankroll_file = Path(f"data/bankrolls/kelly_bankroll_{env}.csv")

        if not bankroll_file.exists():
            # Create CSV headers
            headers = [
                "timestamp",
                "bet_id",
                "sport",
                "event",
                "market",
                "decimal_odds",
                "true_probability",
                "edge",
                "kelly_fraction",
                "full_kelly_pct",
                "adjusted_kelly_pct",
                "stake",
                "balance_before",
                "balance_after",
                "total_at_risk",
                "result",
                "payout",
                "roi",
                "bankroll_growth_rate",
                "notes",
            ]

            with open(bankroll_file, "w") as f:
                f.write(",".join(headers) + "\n")

                # Initial balance entry
                initial_entry = [
                    datetime.utcnow().isoformat(),
                    "INIT",
                    "N/A",
                    "INITIALIZATION",
                    "N/A",
                    "0.0",
                    "0.0",
                    "0.0",
                    "0.0",
                    "0.0",
                    "0.0",
                    "0.0",
                    "1000.0",
                    "1000.0",
                    "0.0",
                    "init",
                    "0.0",
                    "0.0",
                    "0.0",
                    f"Kelly Bankroll Manager Initialized - {env.upper()}",
                ]
                f.write(",".join(initial_entry) + "\n")

            logger.info(f"Created Kelly bankroll file: {bankroll_file}")


def create_environment_configs():
    """Create environment-specific configurations"""

    environments = {
        "dev": {
            "kelly_fraction": 0.10,  # More conservative for dev
            "max_bankroll_risk": 0.10,
            "starting_balance": 500.0,
            "auto_deploy": False,
            "discord_enabled": True,
            "simulation_mode": True,
        },
        "staging": {
            "kelly_fraction": 0.20,
            "max_bankroll_risk": 0.12,
            "starting_balance": 1000.0,
            "auto_deploy": True,
            "discord_enabled": True,
            "simulation_mode": False,
        },
        "production": {
            "kelly_fraction": 0.25,
            "max_bankroll_risk": 0.15,
            "starting_balance": 2000.0,
            "auto_deploy": True,
            "discord_enabled": True,
            "simulation_mode": False,
        },
    }

    for env_name, config in environments.items():
        config_file = Path(f"configs/environments/kelly_{env_name}.json")

        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        logger.info(f"Created environment config: {config_file}")

    # Create master configuration
    master_config = {
        "default_environment": "dev",
        "environments": list(environments.keys()),
        "kelly_formula": "f* = (bp - q) / b",
        "risk_management": {
            "fractional_kelly_enabled": True,
            "correlation_analysis_enabled": True,
            "multi_bet_optimization": True,
            "bankroll_growth_tracking": True,
        },
        "azure_ml_integration": {
            "enabled": True,
            "auto_deploy_environments": ["staging", "production"],
            "model_versioning": True,
            "real_time_optimization": True,
        },
        "discord_integration": {
            "bet_alerts": True,
            "settlement_notifications": True,
            "milestone_alerts": True,
            "daily_reports": True,
        },
    }

    with open("configs/kelly_master_config.json", "w") as f:
        json.dump(master_config, f, indent=2)


def create_launch_scripts():
    """Create convenient launch scripts for different use cases"""

    # Kelly CLI launcher
    kelly_cli_script = '''#!/usr/bin/env python3
"""
Kelly Criterion CLI Launcher
Quick access to Kelly Criterion calculations and management
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Launch Kelly CLI with environment detection"""

    # Default to expert Kelly integration system
    script_path = Path(__file__).parent / "expert_kelly_integration.py"

    if len(sys.argv) == 1:
        # Show help if no arguments
        subprocess.run([sys.executable, str(script_path), "--help"])
    else:
        # Pass through all arguments
        subprocess.run([sys.executable, str(script_path)] + sys.argv[1:])

if __name__ == "__main__":
    main()
'''

    with open("kelly_cli.py", "w") as f:
        f.write(kelly_cli_script)

    # Environment switcher
    env_switcher_script = '''#!/usr/bin/env python3
"""
Quick Environment Switcher for Kelly System
"""

import sys
import subprocess

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ["dev", "staging", "production"]:
        print("Usage: python switch_kelly_env.py <dev|staging|production>")
        return 1

    env = sys.argv[1]
    subprocess.run([
        sys.executable, "expert_kelly_integration.py",
        "--switch-environment", env
    ])

if __name__ == "__main__":
    sys.exit(main())
'''

    with open("switch_kelly_env.py", "w") as f:
        f.write(env_switcher_script)

    # Quick Kelly calculation script
    quick_kelly_script = '''#!/usr/bin/env python3
"""
Quick Kelly Calculation Tool
"""

import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Quick Kelly Calculation")
    parser.add_argument("odds", type=float, help="Decimal odds (e.g., 2.1)")
    parser.add_argument("probability", type=float, help="True probability (0-1)")
    parser.add_argument("--bankroll", type=float, default=1000.0, help="Current bankroll")
    parser.add_argument("--fraction", type=float, default=0.25, help="Kelly fraction")

    args = parser.parse_args()

    if not (0 < args.probability < 1):
        print("Error: Probability must be between 0 and 1")
        return 1

    if args.odds <= 1.0:
        print("Error: Odds must be greater than 1.0")
        return 1

    # Calculate Kelly
    b = args.odds - 1.0
    p = args.probability
    q = 1.0 - p

    full_kelly = (b * p - q) / b
    fractional_kelly = full_kelly * args.fraction
    stake = args.bankroll * fractional_kelly

    edge = p - (1.0 / args.odds)
    expected_value = (args.odds * p) - 1.0

    print("\\n🧮 KELLY CALCULATION RESULTS")
    print(f"   Odds: {args.odds:.2f}")
    print(f"   True Probability: {args.probability:.1%}")
    print(f"   Edge: {edge:.3f} ({edge*100:.1f}%)")
    print(f"   Expected Value: {expected_value:.3f}")
    print(f"   Full Kelly: {full_kelly:.3f} ({full_kelly*100:.1f}%)")
    print(f"   Fractional Kelly: {fractional_kelly:.3f} ({fractional_kelly*100:.1f}%)")
    print(f"   Recommended Stake: ${stake:.2f}")

    if edge <= 0:
        print("   ⚠️  WARNING: Negative edge - Do not bet!")
    elif full_kelly > 0.10:
        print("   ⚠️  WARNING: High Kelly percentage - Consider reducing fraction")
    else:
        print("   ✅ Kelly calculation looks good")

if __name__ == "__main__":
    main()
'''

    with open("quick_kelly.py", "w") as f:
        f.write(quick_kelly_script)

    # Make scripts executable on Unix systems
    if os.name != "nt":
        for script in ["kelly_cli.py", "switch_kelly_env.py", "quick_kelly.py"]:
            os.chmod(script, 0o755)

    logger.info("Created launch scripts: kelly_cli.py, switch_kelly_env.py, quick_kelly.py")


def setup_cli_tools():
    """Setup CLI tools for Kelly management"""

    cli_tools = {
        "kelly_report.py": '''#!/usr/bin/env python3
"""Kelly Performance Reporter"""
import subprocess, sys
subprocess.run([sys.executable, "expert_kelly_integration.py", "--comprehensive-report"] + sys.argv[1:])
''',
        "kelly_multi_bet.py": '''#!/usr/bin/env python3
"""Multi-Bet Kelly Analyzer"""
import subprocess, sys
if len(sys.argv) < 2:
    print("Usage: python kelly_multi_bet.py <bets_file.json>")
    sys.exit(1)
subprocess.run([sys.executable, "expert_kelly_integration.py", "--multi-bet-analysis", "--bets-file", sys.argv[1]] + sys.argv[2:])
''',
        "kelly_simulate.py": '''#!/usr/bin/env python3
"""Kelly Simulation Mode"""
import subprocess, sys
subprocess.run([sys.executable, "expert_kelly_integration.py", "--simulate"] + sys.argv[1:])
''',
    }

    cli_dir = Path("cli/kelly")
    cli_dir.mkdir(parents=True, exist_ok=True)

    for tool_name, tool_code in cli_tools.items():
        tool_path = cli_dir / tool_name
        with open(tool_path, "w") as f:
            f.write(tool_code)

        if os.name != "nt":
            os.chmod(tool_path, 0o755)

    logger.info("Created CLI tools in cli/kelly/")


def create_expert_kelly_documentation():
    """Create comprehensive documentation for Expert Kelly Integration"""

    documentation = """# EQ12 Expert Kelly Integration System

## Overview

The Expert Kelly Integration System is the central bankroll management module for EQ12's sports betting optimization platform. It implements the Kelly Criterion formula `f* = (bp - q) / b` as the core mathematical foundation for optimal bet sizing and risk management.

## Core Components

### 1. Kelly Bankroll Manager (`kelly_bankroll_manager.py`)
- **Purpose**: Central bankroll management with Kelly Criterion optimization
- **Features**:
  - Fractional Kelly controls for risk management
  - Multi-bet correlation analysis
  - Discord integration for real-time notifications
  - Persistent CSV-based bankroll tracking
  - Statistical probability model integration

### 2. Azure ML Workspace Manager (`azure_ml_manager.py`)
- **Purpose**: Multi-environment Azure ML workspace management
- **Features**:
  - Dev/Staging/Production environment separation
  - Automated model deployment pipelines
  - Compute cluster auto-scaling
  - Environment switching and migration

### 3. Expert Kelly Integration System (`expert_kelly_integration.py`)
- **Purpose**: Central control system coordinating all components
- **Features**:
  - Multi-bet Kelly strategy calculation
  - Azure ML integration and deployment
  - Comprehensive performance reporting
  - Environment management and data migration

## Kelly Criterion Implementation

### Mathematical Foundation
```
f* = (bp - q) / b

Where:
- f* = Optimal fraction of bankroll to bet
- b = Net odds received (decimal_odds - 1)
- p = True probability of winning
- q = Probability of losing (1 - p)
```

### Risk Management Features
- **Fractional Kelly**: Multiply full Kelly by safety factor (default: 0.25)
- **Maximum Bankroll Risk**: Cap total exposure (default: 15% of bankroll)
- **Correlation Analysis**: Adjust sizing for correlated bets
- **Edge Threshold**: Minimum edge required to place bet (default: 1%)

## Environment Configuration

### Development Environment
- Kelly Fraction: 0.10 (conservative)
- Max Bankroll Risk: 10%
- Starting Balance: $500
- Simulation Mode: Enabled

### Staging Environment
- Kelly Fraction: 0.20
- Max Bankroll Risk: 12%
- Starting Balance: $1,000
- Auto-deploy: Enabled

### Production Environment
- Kelly Fraction: 0.25
- Max Bankroll Risk: 15%
- Starting Balance: $2,000
- Auto-deploy: Enabled

## Usage Examples

### Quick Kelly Calculation
```bash
python quick_kelly.py 2.1 0.52 --bankroll 1000 --fraction 0.25
```

### Multi-Bet Analysis
```bash
python kelly_cli.py --multi-bet-analysis --bets-file sample_bets.json
```

### Environment Switching
```bash
python switch_kelly_env.py production
```

### Comprehensive Report
```bash
python kelly_cli.py --comprehensive-report --environment production
```

## Data Storage Structure

### Bankroll Tracking CSV Format
- `timestamp`: UTC timestamp of bet/settlement
- `bet_id`: Unique bet identifier
- `sport`, `event`, `market`: Betting context
- `decimal_odds`: Bookmaker odds
- `true_probability`: Estimated true win probability
- `edge`: Calculated edge (true_prob - implied_prob)
- `kelly_fraction`: Kelly fraction setting used
- `full_kelly_pct`: Full Kelly percentage
- `adjusted_kelly_pct`: Fractional Kelly percentage
- `stake`: Actual bet amount
- `balance_before`/`balance_after`: Bankroll state
- `result`: Bet outcome (win/loss/push/void)
- `roi`: Return on investment percentage
- `bankroll_growth_rate`: Growth rate impact

### Azure ML Integration
- Model versioning and deployment automation
- Real-time probability model updates
- Performance monitoring and optimization
- Multi-environment CI/CD pipelines

## Discord Integration

### Notification Types
- **Bet Alerts**: New Kelly bets with sizing analysis
- **Settlement Notifications**: Bet outcomes and P/L
- **Milestone Alerts**: Bankroll milestones and growth
- **Daily Reports**: Performance summaries

### Rich Embed Format
- Color-coded by performance/risk level
- Kelly percentage and edge calculations
- Real-time bankroll status
- Risk level indicators

## CLI Tools Reference

### Main Commands
- `kelly_cli.py`: Main CLI interface
- `quick_kelly.py`: Fast Kelly calculations
- `switch_kelly_env.py`: Environment switching
- `kelly_report.py`: Performance reports
- `kelly_multi_bet.py`: Multi-bet analysis
- `kelly_simulate.py`: Simulation mode

### Configuration Files
- `configs/kelly_master_config.json`: Master system configuration
- `configs/environments/kelly_{env}.json`: Environment-specific settings
- `.azureml/config-{env}.json`: Azure ML workspace configurations

## Statistical Models Integration

### Probability Estimation
The system supports pluggable statistical models for true probability estimation:

```python
def custom_probability_model(event_data):
    # Implement custom probability estimation
    # Return probability between 0 and 1
    pass
```

### Correlation Analysis
Multi-bet scenarios use correlation matrices to adjust Kelly sizing:

```python
correlation_matrix = {
    ("bet1", "bet2"): 0.3,  # 30% correlation
    ("bet1", "bet3"): -0.1, # Negative correlation
}
```

## Performance Monitoring

### Key Metrics
- **Bankroll Growth Rate**: Compound annual growth rate
- **Kelly Efficiency**: Actual vs theoretical Kelly performance
- **Sharpe Ratio**: Risk-adjusted return measurement
- **Win Rate**: Percentage of winning bets
- **Average Edge**: Mean edge across all bets
- **ROI**: Return on investment percentage

### Risk Assessment
- **Current Risk Level**: Real-time risk assessment
- **Drawdown Recovery**: Recovery efficiency from losses
- **Bet Sizing Accuracy**: Adherence to optimal Kelly sizing
- **Diversification Score**: Portfolio diversification measure

## Security and Access Control

### Environment Isolation
- Separate Azure ML workspaces per environment
- Environment-specific authentication and secrets
- Network isolation for production deployments

### Data Protection
- Encrypted storage for sensitive bankroll data
- Audit logging for all bankroll transactions
- Access control for environment switching

## Troubleshooting

### Common Issues
1. **Kelly Manager Not Initialized**: Check environment configuration files
2. **Azure ML Connection Failed**: Verify subscription ID and resource group
3. **Discord Notifications Not Working**: Check webhook URL configuration
4. **Negative Kelly Percentage**: Indicates negative edge - do not bet

### Validation Steps
1. Check bankroll CSV files exist and are properly formatted
2. Verify Azure ML configuration files are present
3. Test Discord webhook connectivity
4. Validate environment variable settings

## Integration with EQ12 Platform

The Expert Kelly Integration System seamlessly integrates with:
- **Sports Betting Optimizer**: Receives bet opportunities and odds
- **Browser Extension**: Real-time bet sizing for DraftKings/FanDuel
- **Discord Bot**: Automated notifications and alerts
- **Dashboard**: Performance visualization and reporting
- **Slip Export**: Automatic bet placement with optimal sizing

## Future Enhancements

### Planned Features
- Machine learning probability models
- Advanced correlation detection
- Real-time market monitoring
- Portfolio optimization algorithms
- Mobile app integration
- Advanced risk management tools

---

For technical support or feature requests, refer to the main EQ12 documentation or contact the development team.
"""

    with open("KELLY_INTEGRATION_GUIDE.md", "w") as f:
        f.write(documentation)

    # Create sample bets file for testing
    sample_bets = [
        {
            "bet_id": "sample-001",
            "sport": "NFL",
            "event": "Chiefs vs Patriots",
            "market": "Moneyline",
            "decimal_odds": 2.1,
            "true_probability": 0.52,
            "correlation_group": "nfl_week1",
        },
        {
            "bet_id": "sample-002",
            "sport": "NBA",
            "event": "Lakers vs Warriors",
            "market": "Spread",
            "decimal_odds": 1.95,
            "true_probability": 0.53,
            "correlation_group": "nba_west",
        },
    ]

    with open("sample_bets.json", "w") as f:
        json.dump(sample_bets, f, indent=2)

    logger.info("Created documentation: KELLY_INTEGRATION_GUIDE.md")


def validate_setup():
    """Validate that the setup was successful"""

    validation_checks = [
        ("Directory structure", check_directories),
        ("Configuration files", check_configs),
        ("Launch scripts", check_scripts),
        ("Data files", check_data_files),
        ("CLI tools", check_cli_tools),
    ]

    all_passed = True

    for check_name, check_func in validation_checks:
        try:
            result = check_func()
            if result:
                print(f"   ✅ {check_name}: PASS")
            else:
                print(f"   ❌ {check_name}: FAIL")
                all_passed = False
        except Exception as e:
            print(f"   ❌ {check_name}: ERROR - {e}")
            all_passed = False

    return all_passed


def check_directories():
    """Check that all required directories exist"""
    required_dirs = [
        "data/bankrolls",
        "configs/environments",
        ".azureml",
        "cli/kelly",
        "logs/kelly",
    ]
    return all(Path(d).exists() for d in required_dirs)


def check_configs():
    """Check that configuration files exist"""
    required_configs = [
        "configs/kelly_master_config.json",
        "configs/environments/kelly_dev.json",
        ".azureml/config-dev.json",
    ]
    return all(Path(f).exists() for f in required_configs)


def check_scripts():
    """Check that launch scripts exist"""
    required_scripts = ["kelly_cli.py", "switch_kelly_env.py", "quick_kelly.py"]
    return all(Path(s).exists() for s in required_scripts)


def check_data_files():
    """Check that data files exist"""
    required_data = ["data/bankrolls/kelly_bankroll_dev.csv", "sample_bets.json"]
    return all(Path(f).exists() for f in required_data)


def check_cli_tools():
    """Check that CLI tools exist"""
    required_tools = ["cli/kelly/kelly_report.py", "cli/kelly/kelly_multi_bet.py"]
    return all(Path(t).exists() for t in required_tools)


def print_usage_instructions():
    """Print usage instructions after setup"""

    instructions = """
🎯 EXPERT KELLY INTEGRATION SYSTEM - READY TO USE!

📋 Quick Start Commands:

   # Quick Kelly calculation
   python quick_kelly.py 2.1 0.52 --bankroll 1000

   # Switch to production environment
   python switch_kelly_env.py production

   # Generate comprehensive report
   python kelly_cli.py --comprehensive-report

   # Analyze multiple bets
   python kelly_cli.py --multi-bet-analysis --bets-file sample_bets.json

   # Run in simulation mode
   python kelly_cli.py --simulate --environment dev

📁 Key Files Created:
   - KELLY_INTEGRATION_GUIDE.md (Complete documentation)
   - kelly_cli.py (Main CLI interface)
   - quick_kelly.py (Fast calculations)
   - sample_bets.json (Example data)
   - configs/kelly_master_config.json (Master config)

🔧 Environment Setup:
   1. Set Azure subscription: export AZURE_SUBSCRIPTION_ID="your-id"
   2. Set Discord webhook: export DISCORD_WEBHOOK_URL="your-webhook"
   3. Run: python expert_kelly_integration.py --environment dev

📖 For complete documentation, see: KELLY_INTEGRATION_GUIDE.md

🚀 The Kelly Criterion is now your central bankroll management system!
    """

    print(instructions)


if __name__ == "__main__":
    try:
        setup_expert_kelly_system()
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)
