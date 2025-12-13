# EdgeFinder Usage Guide

Complete guide to using EdgeFinder for ethical repository reconnaissance and EQ12 system enhancement.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Usage Examples](#basic-usage-examples)
3. [Advanced Workflows](#advanced-workflows)
4. [EQ12 Integration Examples](#eq12-integration-examples)
5. [Configuration Guide](#configuration-guide)
6. [Security Best Practices](#security-best-practices)
7. [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Installation and Setup
```bash
# Clone and install EdgeFinder
git clone https://github.com/eq12/edgefinder.git
cd edgefinder
pip install -e .

# Copy configuration template
cp example-config.yaml config.yaml

# Edit configuration with your API tokens
# GitHub: https://github.com/settings/tokens/new
# HuggingFace: https://huggingface.co/settings/tokens
```

### 2. First Search
```bash
# Search for Python betting APIs
edgefinder search \
  --keywords "betting odds api" \
  --lang python \
  --min-stars 5 \
  --max 20 \
  --output first_search.json
```

### 3. View Results
```bash
# Check the JSON output
cat first_search.json

# Or use the report command (when implemented)
edgefinder report --input first_search.json --format markdown
```

## Basic Usage Examples

### Simple Repository Search

#### Search GitHub for Python APIs
```bash
edgefinder search \
  --keywords "api client python" \
  --lang python \
  --min-stars 100 \
  --license-allowlist MIT,Apache-2.0 \
  --output python_apis.json
```

#### Search Hugging Face for ML Models
```bash
edgefinder search \
  --keywords "sports prediction model" \
  --sources huggingface \
  --max 10 \
  --output ml_models.json
```

#### Multi-Source Search
```bash
edgefinder search \
  --keywords "neural network pytorch" \
  --sources github,huggingface \
  --lang python \
  --since 2024-01-01 \
  --output neural_nets.json
```

### License-Specific Searches

#### Only MIT and Apache Licensed Code
```bash
edgefinder search \
  --keywords "data processing pipeline" \
  --license-allowlist MIT,Apache-2.0 \
  --min-stars 50 \
  --output license_safe.json
```

#### Exclude GPL Licensed Code
```bash
# Search with comprehensive license allowlist (excluding GPL)
edgefinder search \
  --keywords "web scraper" \
  --license-allowlist MIT,Apache-2.0,BSD-3-Clause,ISC \
  --output no_gpl_scrapers.json
```

### Language and Technology Filtering

#### JavaScript/TypeScript Packages
```bash
edgefinder search \
  --keywords "react component library" \
  --lang javascript,typescript \
  --min-stars 200 \
  --output react_components.json
```

#### Python Data Science Tools
```bash
edgefinder search \
  --keywords "pandas numpy matplotlib data analysis" \
  --lang python \
  --min-stars 500 \
  --output data_science.json
```

## Advanced Workflows

### Complete Analysis Pipeline

#### 1. Search and Initial Filtering
```bash
# Comprehensive search for betting-related repositories
edgefinder search \
  --keywords "sports betting odds parlay prop bet" \
  --lang python,javascript \
  --min-stars 10 \
  --max 100 \
  --license-allowlist MIT,Apache-2.0,BSD-3-Clause \
  --since 2023-01-01 \
  --score-min 5.0 \
  --output betting_search.json
```

#### 2. Detailed Analysis
```bash
# Analyze top 20 candidates
edgefinder analyze \
  --input betting_search.json \
  --top 20 \
  --download \
  --security-scan \
  --generate-patch \
  --output betting_analysis.json
```

#### 3. Generate Integration Patches
```bash
# Create EQ12 integration wrappers
edgefinder patch \
  --input betting_analysis.json \
  --patch-type wrapper \
  --target-integration eq12 \
  --output eq12_betting_patches/ \
  --dry-run  # Review patches first
```

#### 4. Production Patch Generation
```bash
# Generate actual patches after review
edgefinder patch \
  --input betting_analysis.json \
  --patch-type wrapper \
  --target-integration eq12 \
  --output eq12_betting_patches/
```

### Security-Focused Workflow

#### High-Security Repository Analysis
```bash
# Search with strict security requirements
edgefinder search \
  --keywords "cryptography secure authentication" \
  --min-stars 500 \
  --license-allowlist MIT,Apache-2.0 \
  --output security_libs.json

# Security-focused analysis
edgefinder analyze \
  --input security_libs.json \
  --top 5 \
  --security-scan \
  --download \
  --output security_analysis.json

# Review security findings
grep -A 5 -B 5 "security_warnings" security_analysis.json
```

## EQ12 Integration Examples

### Betting System Enhancement

#### EQ12 Betting API Integration
```bash
# Search specifically for EQ12 betting enhancement
edgefinder search \
  --keywords "odds api sportsbook betting line movement" \
  --eq12-integration betting \
  --lang python \
  --min-stars 25 \
  --license-allowlist MIT,Apache-2.0 \
  --output eq12_betting_candidates.json

# Detailed betting system analysis
edgefinder analyze \
  --input eq12_betting_candidates.json \
  --top 10 \
  --download \
  --security-scan \
  --generate-patch \
  --output eq12_betting_detailed.json

# Generate EQ12-specific integration patches
edgefinder patch \
  --input eq12_betting_detailed.json \
  --patch-type enhancement \
  --target-integration eq12 \
  --output eq12_betting_integrations/
```

#### Generated Integration Example
The patch command creates EQ12 integration wrappers like:

```python
# eq12_betting_integrations/odds_api_wrapper.py
"""
EQ12 Integration Wrapper for Odds API
Generated by EdgeFinder - Review and customize before use
"""

from original_module import OddsAPI
from eq12.core import BaseIntegration
from eq12.logging import get_logger

class EQ12OddsAPIWrapper(BaseIntegration):
    """
    EQ12-compatible wrapper for external Odds API
    Provides secure integration with audit logging
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.logger = get_logger('eq12.odds_api')
        self.api = OddsAPI(api_key=config.odds_api_key)
    
    def get_odds(self, sport, market=None):
        """Get odds with EQ12 logging and validation"""
        try:
            self.logger.info(f"Fetching odds for {sport}")
            
            # Input validation
            if not self._validate_sport(sport):
                raise ValueError(f"Invalid sport: {sport}")
            
            # Call original API
            odds = self.api.get_odds(sport, market)
            
            # EQ12 data transformation
            eq12_odds = self._transform_to_eq12_format(odds)
            
            self.logger.info(f"Successfully fetched {len(eq12_odds)} odds")
            return eq12_odds
            
        except Exception as e:
            self.logger.error(f"Odds API error: {e}")
            raise
    
    def _validate_sport(self, sport):
        """Validate sport against EQ12 supported sports"""
        supported_sports = ['nfl', 'nba', 'mlb', 'nhl', 'soccer']
        return sport.lower() in supported_sports
    
    def _transform_to_eq12_format(self, odds_data):
        """Transform external odds format to EQ12 standard"""
        # Implementation would depend on EQ12 data schema
        return odds_data
```

### AI/ML Model Integration

#### Machine Learning Model Discovery
```bash
# Search for AI models relevant to EQ12
edgefinder search \
  --keywords "neural network sports prediction machine learning" \
  --eq12-integration ai \
  --sources github,huggingface \
  --min-stars 20 \
  --license-allowlist MIT,Apache-2.0,BSD-3-Clause \
  --output eq12_ai_models.json

# AI-focused analysis
edgefinder analyze \
  --input eq12_ai_models.json \
  --top 15 \
  --security-scan \
  --generate-patch \
  --output eq12_ai_analysis.json
```

### Analytics Dashboard Integration

#### Analytics Component Discovery
```bash
# Search for dashboard and analytics components
edgefinder search \
  --keywords "dashboard visualization react chart analytics" \
  --eq12-integration analytics \
  --lang javascript,typescript,python \
  --min-stars 100 \
  --output eq12_analytics_components.json

# Analytics integration analysis
edgefinder analyze \
  --input eq12_analytics_components.json \
  --top 12 \
  --download \
  --generate-patch \
  --output eq12_analytics_analysis.json
```

## Configuration Guide

### Basic Configuration File
```yaml
# config.yaml - Basic EdgeFinder configuration

# Output directories
output_dir: "output"
downloads_dir: "downloads"

# Logging configuration
log_level: "INFO"
verbose: false
debug: false

# GitHub API configuration
github:
  token: "ghp_your_github_token_here"
  base_url: "https://api.github.com"
  rate_limit_requests: 5000
  rate_limit_window: 3600

# Hugging Face API configuration  
huggingface:
  token: "hf_your_huggingface_token_here"
  base_url: "https://huggingface.co"
  api_base_url: "https://huggingface.co/api"
  rate_limit_requests: 1000
  rate_limit_window: 3600

# Security configuration
security:
  max_file_size_mb: 100
  scan_timeout: 300
  allowed_extensions: [".py", ".js", ".ts", ".json", ".yaml", ".yml", ".md", ".txt"]
  dangerous_patterns: 
    - "eval("
    - "exec("
    - "__import__"
    - "subprocess.call"
    - "os.system"

# EQ12 integration configuration
eq12_integration:
  dashboard_base_url: "https://eq12.local/dashboards/"
  betting_keywords:
    - "odds"
    - "betting"
    - "sportsbook" 
    - "parlay"
    - "prop"
    - "line"
    - "spread"
    - "moneyline"
  ai_keywords:
    - "neural"
    - "transformer"
    - "machine-learning"
    - "deep-learning"
    - "pytorch"
    - "tensorflow"
    - "sklearn"
  analytics_keywords:
    - "dashboard"
    - "visualization"
    - "chart"
    - "analytics"
    - "metrics"
    - "reporting"
  scoring_bonuses:
    eq12_integration: 2.0
    betting_relevance: 1.5
    ai_relevance: 1.2
    security_compliance: 1.0
```

### Environment Variables
```bash
# .env file for sensitive configuration
GITHUB_TOKEN=ghp_your_github_token_here
HUGGINGFACE_TOKEN=hf_your_huggingface_token_here
EDGEFINDER_OUTPUT_DIR=/custom/output/path
EDGEFINDER_DOWNLOADS_DIR=/custom/downloads/path
EDGEFINDER_LOG_LEVEL=INFO
EDGEFINDER_DEBUG=false
```

### Advanced Security Configuration
```yaml
security:
  max_file_size_mb: 50  # Stricter file size limit
  scan_timeout: 180     # Faster timeout for security scans
  
  # Comprehensive dangerous patterns
  dangerous_patterns:
    - "eval("
    - "exec("
    - "__import__"
    - "subprocess"
    - "os.system"
    - "shell=True"
    - "input("
    - "raw_input("
    - "compile("
    - "globals("
    - "locals("
  
  # Allowed file extensions for analysis
  allowed_extensions:
    - ".py"      # Python
    - ".js"      # JavaScript  
    - ".ts"      # TypeScript
    - ".json"    # JSON config
    - ".yaml"    # YAML config
    - ".yml"     # YAML config
    - ".md"      # Documentation
    - ".txt"     # Text files
    - ".toml"    # TOML config
    - ".cfg"     # Config files
  
  # Blocked file types (security risk)
  blocked_extensions:
    - ".exe"
    - ".dll" 
    - ".so"
    - ".dylib"
    - ".bat"
    - ".sh"
    - ".ps1"
```

## Security Best Practices

### Pre-Analysis Security Checklist

1. **Verify Repository Legitimacy**
   ```bash
   # Check repository age and activity
   edgefinder search --keywords "your_search" --min-stars 50 --since 2023-01-01
   ```

2. **License Compliance Verification**
   ```bash
   # Only search compatible licenses
   edgefinder search \
     --keywords "your_search" \
     --license-allowlist MIT,Apache-2.0,BSD-3-Clause
   ```

3. **Security Scan All Candidates**
   ```bash
   # Always run security scans
   edgefinder analyze \
     --input search_results.json \
     --security-scan \
     --output security_analysis.json
   ```

### Post-Analysis Security Review

1. **Review Security Warnings**
   ```bash
   # Extract security issues from analysis
   grep -r "security_warnings" analysis_results.json
   
   # Check for critical vulnerabilities
   grep -r "critical\|high" analysis_results.json
   ```

2. **Manual Code Review**
   ```bash
   # Download repositories for manual inspection
   edgefinder analyze \
     --input results.json \
     --download \
     --output manual_review/
   ```

3. **Patch Validation**
   ```bash
   # Generate patches with dry-run first
   edgefinder patch \
     --input analysis.json \
     --patch-type wrapper \
     --dry-run
   
   # Review generated patches before applying
   # Then generate actual patches
   edgefinder patch \
     --input analysis.json \
     --patch-type wrapper \
     --output validated_patches/
   ```

### Integration Security Guidelines

1. **Sandbox Testing**
   - Always test integrations in isolated environments
   - Use Docker containers for initial testing
   - Validate all external inputs

2. **EQ12 Integration Security**
   - Review all generated integration wrappers
   - Ensure proper error handling and logging
   - Validate against EQ12 security standards

3. **Ongoing Monitoring**
   - Set up regular security scans
   - Monitor for new vulnerabilities in integrated code
   - Keep audit logs of all EdgeFinder operations

## Troubleshooting

### Common Issues and Solutions

#### API Rate Limiting
```bash
# Problem: GitHub rate limit exceeded
# Solution: Check rate limit status
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit

# Wait for reset or use different token
# Configure lower rate limits in config
```

#### Permission Errors
```bash
# Problem: GitHub token permissions
# Solution: Verify token scopes
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Ensure token has 'public_repo' scope
```

#### Download Failures
```bash
# Problem: Repository download timeout
# Solution: Increase timeout in config
security:
  scan_timeout: 600  # 10 minutes

# Or skip problematic repositories
edgefinder analyze --input results.json --top 5  # Analyze fewer
```

#### Docker Issues
```bash
# Problem: Docker container fails to start
# Solution: Check Docker setup
./docker-run.sh status

# Cleanup and rebuild
./docker-run.sh cleanup
./docker-run.sh build --no-cache
```

### Debug Mode
```bash
# Enable verbose debug output
edgefinder --debug --verbose search --keywords "test"

# Or set environment variables
export EDGEFINDER_DEBUG=true
export EDGEFINDER_LOG_LEVEL=DEBUG
export EDGEFINDER_VERBOSE=true
```

### Getting Help

1. **Check Logs**
   ```bash
   # View recent logs
   tail -f logs/edgefinder.log
   
   # Search for errors
   grep ERROR logs/edgefinder.log
   ```

2. **Validate Configuration**
   ```bash
   # Test configuration
   edgefinder version  # Should show version info
   
   # Test API connectivity
   edgefinder search --keywords "test" --max 1 --dry-run
   ```

3. **Community Support**
   - GitHub Issues: Report bugs and request features
   - Documentation: Check README.md for latest updates
   - EQ12 Support: Contact EQ12 team for integration issues

## Best Practices Summary

1. **Always start with small searches** to test configuration
2. **Use license allowlists** to ensure compliance
3. **Run security scans** on all analyzed repositories
4. **Review patches manually** before integration
5. **Keep audit logs** of all EdgeFinder operations
6. **Regular updates** of dependencies and security rules
7. **Respect rate limits** and terms of service
8. **Use Docker** for isolated execution environments

## Example Complete Workflow

Here's a complete example workflow for EQ12 betting system enhancement:

```bash
# 1. Initial search for betting APIs
edgefinder search \
  --keywords "sports betting odds api line movement" \
  --eq12-integration betting \
  --lang python \
  --min-stars 20 \
  --license-allowlist MIT,Apache-2.0,BSD-3-Clause \
  --since 2023-06-01 \
  --max 50 \
  --output eq12_betting_initial.json

# 2. Security analysis of top candidates
edgefinder analyze \
  --input eq12_betting_initial.json \
  --top 15 \
  --download \
  --security-scan \
  --output eq12_betting_analysis.json

# 3. Review security findings
grep -A 10 "security_warnings" eq12_betting_analysis.json

# 4. Generate integration patches for safe candidates
edgefinder patch \
  --input eq12_betting_analysis.json \
  --patch-type wrapper \
  --target-integration eq12 \
  --dry-run  # Review first

# 5. Generate actual patches
edgefinder patch \
  --input eq12_betting_analysis.json \
  --patch-type wrapper \
  --target-integration eq12 \
  --output eq12_betting_patches/

# 6. Manual review and integration
ls -la eq12_betting_patches/
# Review each generated wrapper
# Test in EQ12 development environment
# Deploy to production after validation
```

This completes the comprehensive EdgeFinder usage guide!