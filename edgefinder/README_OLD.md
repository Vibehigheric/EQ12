# EdgeFinder - Ethical Repository Reconnaissance Tool

⚠️ **IMPORTANT LEGAL NOTICE**: This tool accesses only **public content**. Verify license compatibility and get explicit permission before reusing or redistributing code. Do not use for proprietary or private repository inspection. Always respect rate limits and terms of service.

## Overview

EdgeFinder is a robust, well-documented Python CLI tool designed for ethical reconnaissance of public GitHub and Hugging Face repositories. It helps identify candidate projects that could enhance the EQ12 system while maintaining strict legal and ethical compliance.

## Key Features

- 🔍 **Public Repository Search**: Search GitHub and Hugging Face using official APIs
- ⚖️ **License Compliance**: Automatic license detection and compatibility checking
- 🛡️ **Security Analysis**: Static analysis with security scanning capabilities
- 📊 **Intelligent Scoring**: Heuristic-based candidate ranking system
- 🔧 **Safe Patch Generation**: AST-based code modification with safety checks
- 📋 **Comprehensive Reporting**: JSON and human-readable output formats
- 🔒 **Audit Trail**: Complete logging of all actions and API calls

## Installation

```bash
cd C:\EQ12\edgefinder
pip install -e .
```

For development with additional tools:
```bash
pip install -e ".[dev,security,analysis]"
```

## Configuration

### Environment Variables

```bash
# Optional but recommended for higher rate limits
export GITHUB_TOKEN=ghp_your_github_token_here
export HUGGINGFACE_TOKEN=hf_your_huggingface_token_here

# Security scanning (optional)
export BANDIT_ENABLED=true
export SAFETY_ENABLED=true
```

### Configuration File

Create `config.yaml`:

```yaml
# EdgeFinder Configuration
search:
  max_results_per_source: 50
  timeout_seconds: 30
  retry_attempts: 3
  
github:
  base_url: "https://api.github.com"
  rate_limit_buffer: 10  # requests to reserve
  
huggingface:
  base_url: "https://huggingface.co"
  api_base_url: "https://huggingface.co/api"
  
analysis:
  download_enabled: true
  security_scan_enabled: true
  max_file_size_mb: 100
  
scoring:
  license_bonus: 20
  stars_weight: 0.3
  activity_weight: 0.2
  keyword_weight: 0.2
  language_bonus: 10
  security_penalty: -50

licenses:
  allowed:
    - "MIT"
    - "Apache-2.0"
    - "BSD-3-Clause"
    - "BSD-2-Clause"
    - "ISC"
    - "Unlicense"
  blocked:
    - "GPL-3.0"
    - "GPL-2.0"
    - "AGPL-3.0"
    - "LGPL-3.0"
    - "LGPL-2.1"
```

## Usage

### Basic Search

```bash
# Search for odds API projects
edgefinder search --keywords "odds api parlay" --lang python --max 30

# Search with license filtering
edgefinder search --keywords "mlb betting" --lang python,javascript --license-allowlist MIT,Apache-2.0 --min-stars 10

# Search with date filtering
edgefinder search --keywords "llama agent" --since 2024-01-01 --max 50
```

### Advanced Analysis

```bash
# Analyze specific candidate
edgefinder analyze --candidate github:owner/repo --download --generate-patch

# Download repositories for offline analysis
edgefinder download --candidate-ids id1,id2,id3

# Generate patches for integration
edgefinder patch --candidate github:owner/repo --target-integration eq12-betting

# Generate comprehensive report
edgefinder report --format markdown --out integration-report.md
```

### Complete Workflow Example

```bash
# 1. Search for candidates
GITHUB_TOKEN=ghp_xxx HUGGINGFACE_TOKEN=hf_xxx \
  edgefinder search \
    --keywords "odds api parlay sportsbook" \
    --lang python \
    --max 30 \
    --since 2024-01-01 \
    --license-allowlist MIT,Apache-2.0,BSD-3-Clause \
    --min-stars 5 \
    --output candidates.json

# 2. Analyze top candidates
edgefinder analyze \
  --input candidates.json \
  --top 10 \
  --download \
  --security-scan \
  --output analysis.json

# 3. Generate integration patches
edgefinder patch \
  --input analysis.json \
  --candidate-score-min 70 \
  --target-project eq12 \
  --output patches/

# 4. Create final report
edgefinder report \
  --input analysis.json \
  --format markdown \
  --include-patches \
  --out integration-report.md
```

## Command Reference

### `edgefinder search`

Search public repositories based on criteria.

**Options:**
- `--keywords TEXT`: Space-separated search terms
- `--lang TEXT`: Programming languages (comma-separated)
- `--min-stars INT`: Minimum star count (default: 0)
- `--max INT`: Maximum results per source (default: 50)
- `--since DATE`: Only repos updated after this date (YYYY-MM-DD)
- `--license-allowlist TEXT`: Comma-separated allowed licenses
- `--output PATH`: Output file for results (JSON)
- `--sources TEXT`: Sources to search (github,huggingface)

### `edgefinder analyze`

Perform detailed analysis of candidates.

**Options:**
- `--candidate TEXT`: Single candidate ID to analyze
- `--input PATH`: JSON file with candidates
- `--top INT`: Analyze only top N candidates
- `--download`: Download repositories for analysis
- `--security-scan`: Run security analysis
- `--generate-patch`: Generate integration patches
- `--output PATH`: Output file for analysis results

### `edgefinder download`

Download repositories for offline analysis.

**Options:**
- `--candidate-ids TEXT`: Comma-separated candidate IDs
- `--input PATH`: JSON file with candidates
- `--output-dir PATH`: Download directory (default: ./downloads)
- `--format TEXT`: Download format (zip, tar.gz)

### `edgefinder patch`

Generate safe integration patches.

**Options:**
- `--candidate TEXT`: Candidate to patch
- `--input PATH`: Analysis results file
- `--target-integration TEXT`: Integration target (eq12-betting, eq12-analysis)
- `--patch-type TEXT`: Type of patch (wrapper, enhancement, update)
- `--output PATH`: Output directory for patches
- `--dry-run`: Show patches without creating files

### `edgefinder report`

Generate comprehensive reports.

**Options:**
- `--input PATH`: Analysis results file
- `--format TEXT`: Output format (json, markdown, html)
- `--include-patches`: Include patch summaries
- `--include-security`: Include security analysis
- `--template PATH`: Custom report template
- `--out PATH`: Output file

## Security & Safety

### Built-in Protections

1. **Public-Only Access**: Tool only accesses public repositories
2. **License Validation**: Automatic license compatibility checking
3. **Rate Limit Respect**: Exponential backoff and retry logic
4. **Sandboxed Analysis**: Static analysis without code execution
5. **Audit Logging**: Complete trail of all actions
6. **Interactive Confirmation**: Prompts before destructive actions

### Security Scanning

When enabled, EdgeFinder runs multiple security tools:

- **Bandit**: Python security linting
- **Safety**: Python dependency vulnerability scanning
- **Custom Rules**: Repository-specific security patterns
- **License Scanner**: Comprehensive license detection

### Safe Patch Generation

Patches are generated using:

- **AST-based Modification**: No string replacement risks
- **Sandbox Testing**: Patches tested in isolation
- **Rollback Support**: Easy patch reversal
- **Manual Review Required**: No automatic application

## Docker Usage

For isolated execution:

```bash
# Build container
docker build -t edgefinder .

# Run search in container
docker run --rm \
  -v $(pwd)/output:/app/output \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  -e HUGGINGFACE_TOKEN=$HUGGINGFACE_TOKEN \
  edgefinder search --keywords "odds api" --output /app/output/results.json
```

## Integration with EQ12

EdgeFinder integrates seamlessly with the EQ12 ecosystem:

### Dashboard Integration

All reports include hardcoded dashboard URLs:
- **Main Dashboard**: `https://eq12.local/dashboards/edgefinder_analysis.html`
- **Security Dashboard**: `https://eq12.local/dashboards/edgefinder_security.html`
- **Integration Status**: `https://eq12.local/dashboards/edgefinder_integration.html`

### EQ12 Specific Workflows

```bash
# Search for betting-related enhancements
edgefinder search \
  --keywords "sports betting odds api parlay" \
  --lang python \
  --license-allowlist MIT,Apache-2.0 \
  --eq12-integration betting

# Analyze ML/AI enhancements
edgefinder search \
  --keywords "machine learning llama agent transformer" \
  --lang python \
  --eq12-integration ai-analysis

# Generate EQ12-specific patches
edgefinder patch \
  --target-integration eq12-betting \
  --patch-style eq12-standards \
  --include-tests
```

## Legal & Ethical Guidelines

### ✅ Permitted Actions

- Search public repositories using official APIs
- Download public releases and archives
- Analyze public code for compatibility
- Generate patches for manual review
- Create integration documentation

### ❌ Prohibited Actions

- Access private repositories
- Bypass authentication or rate limits
- Automatically apply patches to external repos
- Redistribute code without license compliance
- Scrape private or restricted content

### License Compliance

EdgeFinder automatically:
1. Detects repository licenses
2. Checks compatibility with allowed list
3. Flags incompatible licenses
4. Provides license attribution templates
5. Generates compliance reports

## Troubleshooting

### Common Issues

**Rate Limit Exceeded**
```bash
# Use authenticated requests
export GITHUB_TOKEN=your_token

# Reduce request frequency
edgefinder search --max 10 --delay 2
```

**License Detection Failed**
```bash
# Manual license check
edgefinder analyze --candidate github:owner/repo --force-license-scan
```

**Download Failures**
```bash
# Check network and permissions
edgefinder download --candidate github:owner/repo --verbose
```

### Debug Mode

```bash
# Enable detailed logging
export EDGEFINDER_DEBUG=true
edgefinder search --keywords "test" --verbose
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all security checks pass
5. Submit a pull request

### Development Setup

```bash
git clone https://github.com/eq12/edgefinder
cd edgefinder
pip install -e ".[dev,security,analysis]"
pre-commit install
```

### Running Tests

```bash
# Full test suite
pytest

# Security tests only
pytest -m security

# Skip network tests
pytest -m "not network"
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Support

For issues and questions:
- GitHub Issues: https://github.com/eq12/edgefinder/issues
- Documentation: https://github.com/eq12/edgefinder/blob/main/README.md
- EQ12 Dashboard: https://eq12.local/dashboards/edgefinder_support.html