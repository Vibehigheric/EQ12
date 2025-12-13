# EdgeFinder - Ethical Repository Reconnaissance Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

EdgeFinder is a comprehensive, ethical repository reconnaissance tool designed to discover and analyze public GitHub and Hugging Face repositories for EQ12 system enhancement. It provides secure, automated analysis with strict adherence to legal and ethical guidelines.

## 🚀 Key Features

### 🔍 **Multi-Source Repository Discovery**
- **GitHub Integration**: Full REST API support with authentication and rate limiting
- **Hugging Face Integration**: Model and dataset search with API and HTML fallback
- **Intelligent Filtering**: Language, license, popularity, and activity filters
- **Advanced Search**: Keyword matching, topic analysis, and date-based filtering

### 🛡️ **Security-First Design**
- **Static Analysis**: Bandit integration for security vulnerability detection
- **License Compliance**: Automated license compatibility checking
- **Safe Downloads**: Zip bomb protection, size limits, and validation
- **Security Scoring**: Comprehensive security assessment with threat analysis

### 🎯 **EQ12 Integration**
- **Smart Scoring**: Bonus points for EQ12-relevant keywords (betting, AI, analytics)
- **Dashboard Integration**: Seamless integration with EQ12 dashboards
- **Custom Keywords**: Pre-configured keyword sets for betting, AI, and analytics domains
- **Integration Patches**: AST-based safe code integration with EQ12 systems

### ⚡ **Advanced Analytics**
- **Dependency Analysis**: Automatic dependency parsing from multiple file formats
- **Code Quality Metrics**: Maintainability, complexity, and quality scoring
- **Popularity Metrics**: Stars, forks, downloads, and community engagement analysis
- **Activity Analysis**: Update frequency, issue activity, and maintenance status

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- Git (for repository operations)
- Optional: Docker (for containerized deployment)

### Standard Installation
```bash
# Clone the repository
git clone https://github.com/eq12/edgefinder.git
cd edgefinder

# Install dependencies
pip install -e .
```

### Docker Installation
```bash
# Using Docker Compose (recommended)
./docker-run.sh setup
./docker-run.sh build

# Or build manually
docker build -t edgefinder .
```

## ⚙️ Configuration

### Environment Setup
1. Copy the example configuration:
   ```bash
   cp example-config.yaml config.yaml
   ```

2. Configure API tokens:
   ```yaml
   github:
     token: "ghp_your_github_personal_access_token"
     rate_limit_requests: 5000
   
   huggingface:
     token: "hf_your_huggingface_token"
     rate_limit_requests: 1000
   
   security:
     max_file_size_mb: 100
     scan_timeout: 300
   
   eq12_integration:
     dashboard_base_url: "https://eq12.local/dashboards/"
     betting_keywords: ["odds", "parlay", "sportsbook", "betting"]
     ai_keywords: ["transformer", "neural", "machine-learning"]
   ```

### API Token Setup

#### GitHub Token
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with scopes: `public_repo` (or `repo` for private access)
3. Add token to configuration

#### Hugging Face Token
1. Visit [Hugging Face Settings](https://huggingface.co/settings/tokens)
2. Create new token with read access
3. Add token to configuration (optional but recommended for higher rate limits)

## 🎯 Usage Examples

### Basic Repository Search
```bash
# Search for betting-related Python repositories
edgefinder search \
  --keywords "betting odds api parlay" \
  --lang python \
  --min-stars 10 \
  --max 50 \
  --license-allowlist MIT,Apache-2.0

# Search multiple sources with date filter
edgefinder search \
  --keywords "machine learning sports prediction" \
  --sources github,huggingface \
  --since 2024-01-01 \
  --eq12-integration ai
```

### Advanced Analysis Workflow
```bash
# 1. Search and save results
edgefinder search \
  --keywords "odds api" \
  --lang python \
  --output search_results.json

# 2. Analyze top candidates
edgefinder analyze \
  --input search_results.json \
  --top 10 \
  --download \
  --security-scan \
  --output analysis_results.json

# 3. Generate integration patches
edgefinder patch \
  --input analysis_results.json \
  --patch-type wrapper \
  --target-integration eq12 \
  --output patches/
```

### Docker Usage
```bash
# Quick search using Docker
docker run --rm \
  -e GITHUB_TOKEN="$GITHUB_TOKEN" \
  -v $(pwd)/data:/data \
  edgefinder search --keywords "betting api" --output /data/results.json

# Development mode with source mounting
./docker-run.sh start dev

# Security scanning mode
./docker-run.sh security
```

## 🔧 Command Reference

### Search Command
```bash
edgefinder search [OPTIONS]

Options:
  --keywords TEXT         Search keywords (required)
  --lang, --languages     Programming languages (comma-separated)
  --min-stars INTEGER     Minimum star count
  --max INTEGER          Maximum results per source
  --since DATETIME       Only repos updated since date (YYYY-MM-DD)
  --license-allowlist    Allowed licenses (comma-separated)
  --sources TEXT         Sources: github,huggingface
  --output PATH          Output file for results (JSON)
  --score-min FLOAT      Minimum score threshold
  --eq12-integration     EQ12 integration type: betting,ai,analytics
```

### Analyze Command
```bash
edgefinder analyze [OPTIONS]

Options:
  --candidate TEXT       Single candidate ID to analyze
  --input PATH          JSON file with candidates
  --top INTEGER         Analyze only top N candidates
  --download            Download repositories for analysis
  --security-scan       Run security analysis
  --generate-patch      Generate integration patches
  --output PATH         Output file for analysis results
```

### Patch Command
```bash
edgefinder patch [OPTIONS]

Options:
  --candidate TEXT      Candidate to patch
  --input PATH         Analysis results file
  --patch-type         Type: wrapper,enhancement,update
  --target-integration Integration target (default: eq12)
  --output PATH        Output directory for patches
  --dry-run           Show patches without creating files
```

## 🔒 Security Guidelines

### Ethical Usage Principles
EdgeFinder is designed with strict ethical guidelines:

✅ **Allowed Actions:**
- Access only **public** repositories and APIs
- Respect all rate limits and terms of service
- Verify license compatibility before code reuse
- Use generated patches as starting points for manual review

❌ **Prohibited Actions:**
- Never attempt to access private or restricted content
- Never bypass authentication or security measures
- Never redistribute code without proper licensing
- Never use for competitive intelligence or corporate espionage

### Security Features
- **Sandboxed Execution**: All analysis runs in isolated environments
- **Input Validation**: Comprehensive validation of all external inputs
- **Resource Limits**: Memory, CPU, and disk usage limits
- **Security Scanning**: Automatic vulnerability detection in target repositories
- **Audit Logging**: Complete audit trail of all operations

## 📊 Integration with EQ12

### Dashboard Integration
EdgeFinder seamlessly integrates with EQ12 dashboards:

```python
# Automatic dashboard URL generation
search_url = config.get_dashboard_url('edgefinder_search_results.html')
analysis_url = config.get_dashboard_url('edgefinder_analysis.html')
security_url = config.get_dashboard_url('edgefinder_security.html')
```

### EQ12-Specific Scoring
Repositories receive bonus scores for EQ12 relevance:

- **Betting Integration**: +2.0 points for betting/odds-related keywords
- **AI Integration**: +1.5 points for machine learning/AI keywords  
- **Analytics Integration**: +1.0 points for analytics/dashboard keywords

### Sample EQ12 Workflow
```bash
# 1. Search for EQ12-relevant repositories
edgefinder search \
  --keywords "sports betting odds api" \
  --eq12-integration betting \
  --min-stars 50 \
  --license-allowlist MIT,BSD-3-Clause \
  --output eq12_betting_search.json

# 2. Analyze with EQ12 focus
edgefinder analyze \
  --input eq12_betting_search.json \
  --top 5 \
  --security-scan \
  --generate-patch \
  --output eq12_betting_analysis.json

# 3. Generate EQ12 integration wrappers
edgefinder patch \
  --input eq12_betting_analysis.json \
  --patch-type wrapper \
  --target-integration eq12 \
  --output eq12_integrations/
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/edgefinder --cov-report=html

# Run specific test categories
pytest -m "unit"          # Unit tests only
pytest -m "integration"   # Integration tests only
pytest -m "security"      # Security tests only
```

### Docker Testing
```bash
# Run tests in Docker
./docker-run.sh run pytest -v

# Run security tests
./docker-run.sh security
```

## 🚀 Development

### Development Environment
```bash
# Setup development environment
./docker-run.sh setup
./docker-run.sh start dev

# Open development shell
./docker-run.sh shell edgefinder-dev
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Security scan
bandit -r src/

# Type checking
mypy src/edgefinder/
```

### Contributing
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Ensure all tests pass: `pytest`
5. Format code: `black .`
6. Commit changes: `git commit -m 'Add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Create Pull Request

## 📋 API Reference

### Configuration Classes
```python
from edgefinder import Config, GitHubConfig, HuggingFaceConfig

config = Config(
    github=GitHubConfig(token="your_token"),
    huggingface=HuggingFaceConfig(token="your_token")
)
```

### Search API
```python
from edgefinder import SearchCriteria, GitHubSearcher

criteria = SearchCriteria(
    keywords=["betting", "api"],
    languages=["python"],
    min_stars=10
)

async with GitHubSearcher(config) as searcher:
    candidates = await searcher.search_repositories(criteria)
```

### Analysis API
```python
from edgefinder import RepositoryAnalyzer

analyzer = RepositoryAnalyzer(config)
result = analyzer.analyze_repository(repo_path)
```

## 🆘 Troubleshooting

### Common Issues

#### Rate Limit Errors
```bash
# Check rate limit status
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/rate_limit
```

#### Permission Errors
```bash
# Verify token permissions
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/user
```

#### Docker Issues
```bash
# Clean Docker environment
./docker-run.sh cleanup

# Rebuild from scratch
./docker-run.sh build --no-cache
```

### Debug Mode
```bash
# Enable debug logging
edgefinder --debug search --keywords "test"

# Or set environment variable
export EDGEFINDER_LOG_LEVEL=DEBUG
```

## 📄 License Compliance

EdgeFinder respects software licenses and provides automated compliance checking:

### Supported Licenses
- ✅ **Compatible**: MIT, BSD-2-Clause, BSD-3-Clause, Apache-2.0, ISC
- ⚠️ **Review Required**: LGPL-2.1, LGPL-3.0, EPL-1.0, MPL-2.0
- ❌ **Incompatible**: GPL-2.0, GPL-3.0, AGPL-3.0, Copyleft licenses

### License Checking
```bash
# Search only compatible licenses
edgefinder search \
  --keywords "api client" \
  --license-allowlist MIT,Apache-2.0,BSD-3-Clause
```

## 🤝 Support and Community

### Getting Help
- 📖 **Documentation**: Check this README and inline documentation
- 🐛 **Bug Reports**: Open an issue on GitHub
- 💡 **Feature Requests**: Discuss in GitHub Discussions
- 🔒 **Security Issues**: Email security@eq12.local

### EQ12 Integration Support
- 📊 **Dashboard Issues**: Contact EQ12 dashboard team
- 🔧 **Integration Problems**: Check EQ12 integration documentation
- 🎯 **Scoring Questions**: Review EQ12 scoring configuration

## 📈 Roadmap

### Upcoming Features
- [ ] GitLab repository search integration
- [ ] Bitbucket API support  
- [ ] Advanced machine learning for repository scoring
- [ ] Real-time security vulnerability monitoring
- [ ] Enhanced patch generation with AI assistance
- [ ] GraphQL API for advanced queries

### EQ12 Enhancements
- [ ] Direct EQ12 database integration
- [ ] Real-time dashboard updates
- [ ] Automated betting odds integration
- [ ] Enhanced AI model discovery
- [ ] Advanced analytics pipeline integration

## 📊 Metrics and Analytics

EdgeFinder provides comprehensive metrics for repository analysis:

### Scoring Metrics
- **Popularity Score**: Stars, forks, watchers (0-10 scale)
- **Activity Score**: Recent commits, issue activity (0-10 scale) 
- **Quality Score**: Code quality, documentation (0-10 scale)
- **Security Score**: Vulnerability analysis (0-10 scale)
- **License Score**: Compatibility assessment (0-10 scale)
- **EQ12 Relevance**: Integration potential (0-10 scale)

### Dashboard Metrics
- Total repositories analyzed
- Security vulnerabilities found
- License compliance rate
- EQ12 integration candidates
- Download success rate

## 🔍 Example Outputs

### Search Results
```json
{
  "search_criteria": {
    "keywords": ["betting", "api"],
    "languages": ["python"],
    "min_stars": 10
  },
  "candidates": [
    {
      "id": "github_123",
      "full_name": "example/betting-api",
      "description": "Python API for sports betting odds",
      "score": 8.5,
      "license_info": {
        "spdx_id": "MIT",
        "compatibility": "compatible"
      },
      "stats": {
        "stars": 450,
        "forks": 89
      }
    }
  ]
}
```

### Analysis Results  
```json
{
  "candidate_id": "github_123",
  "security_warnings": [
    {
      "rule_id": "B602",
      "severity": "high",
      "message": "subprocess call with shell=True"
    }
  ],
  "dependencies": ["requests", "click", "pydantic"],
  "code_quality_score": 8.2,
  "security_score": 7.5,
  "eq12_integration_potential": 9.1
}
```

## 📞 Contact

**EQ12 Development Team**
- 📧 Email: dev@eq12.local
- 🔗 GitHub: https://github.com/eq12/edgefinder
- 📱 Dashboard: https://eq12.local/dashboards/edgefinder.html

---

**⚠️ Legal Notice**: This tool accesses only public content. Users are responsible for complying with all applicable laws, terms of service, and ethical guidelines. Always verify license compatibility and obtain proper permissions before using discovered code in production systems.

**🔒 Security Notice**: EdgeFinder includes comprehensive security scanning, but users should always perform additional security reviews before integrating external code into production systems.