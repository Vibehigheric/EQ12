# EQ12 Contributor Guidelines & AI Assistant Rules

## 🎯 Mission Statement

EQ12 is a deterministic, secure, production-grade mathematical engine for sports betting analysis. All contributors (human and AI) must maintain these core principles:

- **Security First**: No secrets, keys, or sensitive data in code
- **Deterministic Math**: Core calculations must be reproducible and testable
- **Production Quality**: Code must be maintainable, tested, and documented

## 🤖 AI Assistant Integration

### GitHub Copilot Configuration

**Default Mode: QUIET** - Copilot is configured for minimal requests:
- Inline suggestions: **DISABLED** by default
- Copilot Chat: **ENABLED** for on-demand help
- Scope: Python and PowerShell only

**Burst Mode**: Use `Ctrl+Shift+P` → "EQ12: Enable Copilot Burst Mode" when you need intensive assistance, then disable when done.

### ChatGPT via Continue Extension

For complex refactoring, planning, and multi-file changes:

1. Open Continue panel (`Ctrl+Shift+I`)
2. Use custom commands:
   - `/eq12` - General EQ12 questions
   - `/math` - Mathematical function help
   - `/security` - Security review requests

## 📋 Coding Standards

### Python Code (PEP8 + EQ12 Extensions)

```python
# Good: Deterministic function with clear inputs/outputs
def calculate_parlay_odds(individual_odds: List[Decimal]) -> Decimal:
    """Calculate parlay odds from individual bet odds.

    Args:
        individual_odds: List of decimal odds for each bet

    Returns:
        Combined decimal odds for the parlay

    Raises:
        ValueError: If any odds are <= 1.0
    """
    if not individual_odds:
        raise ValueError("Cannot calculate parlay with no bets")

    combined = Decimal("1.0")
    for odds in individual_odds:
        if odds <= Decimal("1.0"):
            raise ValueError(f"Invalid odds: {odds}")
        combined *= odds

    return combined

# Bad: Non-deterministic, unclear inputs
def get_odds():  # No type hints
    api_key = "sk-12345"  # Secret in code!
    odds = random.random()  # Non-deterministic!
    return odds  # No validation
```

### PowerShell Code (OTBS Style)

```powershell
# Good: Proper error handling and validation
function Start-EQ12Service {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ServiceName,

        [ValidateRange(1000, 65535)]
        [int]$Port = 8000
    )

    try {
        Write-Verbose "Starting EQ12 service: $ServiceName on port $Port"

        # Validate service exists
        if (-not (Test-Path ".\$ServiceName.py")) {
            throw "Service file not found: $ServiceName.py"
        }

        # Start service
        $process = Start-Process -FilePath "python" -ArgumentList "$ServiceName.py" -PassThru

        Write-Output "✅ Service started: PID $($process.Id)"
        return $process.Id
    }
    catch {
        Write-Error "❌ Failed to start service: $_"
        throw
    }
}
```

## 🔒 Security Requirements

### Secrets Management

**NEVER** include in code:
- API keys (`sk-`, `pk-`, etc.)
- Database passwords
- JWT secrets
- URLs with authentication tokens

**USE** instead:
- Environment variables: `os.getenv("OPENAI_API_KEY")`
- Windows Credential Manager
- Azure Key Vault references
- `.env` files (gitignored)

### Pre-commit Validation

Before any commit, run:
```bash
# Security scan
gitleaks detect --verbose

# Dependency audit
pip audit

# Code quality
ruff --fix .
black .

# Tests
pytest tests/ -v
```

## 🧮 Mathematical Function Standards

### Core Math Requirements

1. **Deterministic**: Same inputs → Same outputs
2. **Validated**: Input validation with clear error messages
3. **Tested**: Unit tests with known good values
4. **Documented**: Docstrings with math formulas

### Example: Proper EV Calculation

```python
from decimal import Decimal
from typing import Union

def calculate_expected_value(
    probability: Union[float, Decimal],
    win_amount: Union[float, Decimal],
    loss_amount: Union[float, Decimal]
) -> Decimal:
    """Calculate expected value of a bet.

    Formula: EV = (P_win * Win_Amount) + (P_loss * Loss_Amount)

    Args:
        probability: Probability of winning (0.0 to 1.0)
        win_amount: Amount won if bet wins (positive)
        loss_amount: Amount lost if bet loses (negative)

    Returns:
        Expected value as Decimal

    Raises:
        ValueError: If probability not in valid range

    Example:
        >>> calculate_expected_value(0.5, 100, -100)
        Decimal('0')
    """
    prob = Decimal(str(probability))
    win = Decimal(str(win_amount))
    loss = Decimal(str(loss_amount))

    if not (Decimal('0') <= prob <= Decimal('1')):
        raise ValueError(f"Probability must be 0-1, got: {prob}")

    prob_loss = Decimal('1') - prob
    ev = (prob * win) + (prob_loss * loss)

    return ev
```

## 🚀 Development Workflow

### Making Changes

1. **Plan** (use Continue for complex changes):
   ```
   TASK: Add new Kelly criterion function
   GOALS:
   1) Implement fractional Kelly with edge and odds
   2) Add input validation and edge case handling
   3) Create comprehensive unit tests

   CONSTRAINTS:
   - No secrets in code
   - Keep deterministic
   - Follow EQ12 math standards
   ```

2. **Implement** with tests:
   ```bash
   # Create feature branch
   git checkout -b feature/kelly-criterion

   # Run development cycle
   ruff --fix .
   pytest tests/ -v
   pip audit
   ```

3. **Review & Commit**:
   ```bash
   # Stage changes
   git add .

   # Commit with clear message
   git commit -m "feat(math): add Kelly criterion calculator

   - Implements fractional Kelly sizing formula
   - Adds validation for edge and odds parameters
   - Includes 15 unit tests with known good values
   - Handles edge cases: zero edge, negative edge

   Closes: #123"
   ```

### Pull Request Standards

**Required PR Checklist:**
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Security scan clean (`gitleaks detect`)
- [ ] Dependencies audited (`pip audit`)
- [ ] Code formatted (`ruff --fix . && black .`)
- [ ] No secrets in diff
- [ ] Math functions have unit tests
- [ ] Breaking changes documented

## 🎛️ VS Code Task Commands

Quick access via `Ctrl+Shift+P`:

- **EQ12: Enable Copilot Burst Mode** - Temporarily enable inline suggestions
- **EQ12: Disable Copilot (Quiet Mode)** - Return to minimal mode
- **EQ12: Run Tests** - Execute full test suite
- **EQ12: Security Scan** - Check for vulnerabilities
- **EQ12: Health Check** - Run EQ12 diagnostics
- **EQ12: Start Control Plane** - Launch SaaS control plane

## 🚨 Red Flags - Auto-Reject

If you see any of these in code or suggestions:

- Hardcoded API keys or secrets
- `random.random()` in core math functions
- Network calls in `eq12_math/` directory
- Commits without tests for new math functions
- Database passwords in configuration files
- Unsigned commits (when signing required)

## 📖 Learning Resources

### EQ12 Architecture
- `README.md` - Project overview and setup
- `eq12_math/` - Core mathematical functions
- `tests/smoke_math.py` - Mathematical validation tests
- `eq12_api.py` - FastAPI service endpoints

### Mathematical References
- Kelly Criterion: [Wikipedia](https://en.wikipedia.org/wiki/Kelly_criterion)
- Expected Value: [Investopedia](https://www.investopedia.com/terms/e/expectedvalue.asp)
- Parlay Odds: [Sports betting mathematics](https://en.wikipedia.org/wiki/Mathematics_of_bookmaking)

---

**Remember**: When in doubt, ask in Copilot Chat or Continue! Both tools are configured with these same guidelines and can help ensure your code meets EQ12 standards.
