# PHP Type Guard Action
## GitHub Action for Enforcing PHP Type Safety Standards

**Stop type-related bugs before they reach production. Enforce professional PHP type standards in every pull request.**

[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-PHP%20Type%20Guard-blue.svg?colorA=24292e&colorB=0366d6&style=flat&longCache=true&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAM6wAADOsB5dZE0gAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAERSURBVCiRhZG/SsMxFEafKoEEEUGsFFjdyoMCK+7i4ifo6OLi4uLi4CoIioOLi4ODg4Ojg4OLgIICrQqtWmdgp03a2kmTn+H7/X7fTfIlcC8+A4jf0x5fjQEQoYU5A4KNKJ5xdofWfOGLdmWf+Hzb2ehqy3r7ePqq1vD5OJJh5UN/PUvOAA==)](https://github.com/marketplace/actions/php-type-guard)
[![CI](https://github.com/eq12/php-type-guard-action/workflows/CI/badge.svg)](https://github.com/eq12/php-type-guard-action/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚨 **The Problem**

**PHP teams struggle with type safety:**
- ❌ PRs introduce `mixed` types and untyped parameters
- ❌ Functions missing return type annotations  
- ❌ No enforcement of type coverage standards
- ❌ Type violations discovered too late in production
- ❌ Inconsistent type standards across team members

**PHP Type Guard fixes this at the PR level.**

---

## ✅ **What It Does**

### **Automatic Type Analysis**
- 🔍 **Scans every PHP file** in your PR
- 📊 **Calculates type coverage** percentage
- 🎯 **Detects missing type hints** on parameters and returns
- 🚫 **Flags use of `mixed` types** where specific types possible
- 📈 **Tracks type coverage trends** over time

### **PR Enforcement**
- ⛔ **Fails PRs** below your type coverage threshold
- 💬 **Comments on PRs** with detailed violation reports
- 📋 **Generates HTML reports** with actionable fixes
- 🎯 **Suggests specific improvements** for each violation
- 🔧 **Integrates with existing CI/CD** pipelines

### **Team Standards**
- 📏 **Enforces consistent standards** across all developers
- 🎓 **Educates team** on type safety best practices
- 📈 **Improves code quality** incrementally over time
- 🚀 **Boosts Intelephense performance** with better types

---

## 🚀 **Quick Setup**

### **1. Add to Your Workflow**
Create `.github/workflows/type-guard.yml`:

```yaml
name: PHP Type Guard

on:
  pull_request:
    paths:
      - '**.php'
  push:
    branches: [main, develop]

jobs:
  type-guard:
    runs-on: ubuntu-latest
    name: PHP Type Safety Check
    
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
        
      - name: PHP Type Guard
        uses: eq12/php-type-guard-action@v1
        with:
          type-coverage-threshold: 85
          fail-on-mixed: true
          fail-on-missing-return: true
          exclude-paths: 'vendor/,tests/legacy/'
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

### **2. Configure Your Standards**
```yaml
- name: PHP Type Guard
  uses: eq12/php-type-guard-action@v1
  with:
    # Minimum type coverage required (0-100)
    type-coverage-threshold: 80
    
    # Fail if mixed types detected
    fail-on-mixed: true
    
    # Fail if functions missing return types  
    fail-on-missing-return: true
    
    # Fail if parameters missing type hints
    fail-on-missing-param: false
    
    # Paths to exclude from analysis
    exclude-paths: 'vendor/,tests/legacy/,tmp/'
    
    # PHPStan analysis level (0-8)
    phpstan-level: 6
    
    # Generate detailed HTML report
    generate-report: true
    
    # Add PR comments with results
    comment-on-pr: true
```

### **3. See Results Immediately**
Your next PR will get automatic type analysis with detailed feedback!

---

## 📊 **Example PR Comment**

```
## ✅ PHP Type Guard Analysis - PASSED

**Type Coverage:** 92.3%
**Violations Found:** 0

### 🎉 All Type Checks Passed!

This PR maintains excellent type safety standards.

### 📊 Analysis Details

- **Threshold:** 85%
- **PHPStan Level:** 6
- **Fail on Mixed:** true
- **Fail on Missing Returns:** true

📋 [View Detailed Report](https://github.com/your-org/your-repo/actions/runs/123456)

---
*Analysis powered by [PHP Type Guard](https://github.com/eq12/php-type-guard-action)*
```

---

## 🔴 **Failure Example**

When type violations are found:

```
## ❌ PHP Type Guard Analysis - FAILED

**Type Coverage:** 67.8%
**Violations Found:** 12

### 🚨 Type Violations

This PR introduces type safety violations that must be fixed:

- Missing return type: `UserService::createUser()` on line 45
- Mixed type parameter: `$data` in `OrderProcessor::validate()` on line 78
- Missing parameter type: `$id` in `ProductRepository::find()` on line 23
- Array without shape: `$config` should use array shape in `ApiClient::__construct()` on line 12

*...and 8 more violations*

### 📝 How to Fix

1. Add missing type hints to function parameters
2. Add return type annotations to all functions  
3. Replace `mixed` types with specific types where possible
4. Add PHPDoc array shapes for complex arrays
5. Run `composer cs:fix` to auto-fix formatting issues
```

---

## 🎯 **Advanced Configuration**

### **Custom Type Rules**
Create `type-guard-rules.json`:

```json
{
  "required_annotations": [
    "@param",
    "@return",
    "@throws"
  ],
  "forbidden_types": [
    "mixed",
    "object", 
    "resource"
  ],
  "array_shape_threshold": 3,
  "minimum_method_coverage": 90,
  "custom_patterns": [
    {
      "pattern": "function.*\\(.*\\$.*\\)",
      "message": "All parameters must have type hints",
      "severity": "error"
    }
  ]
}
```

Use in workflow:
```yaml
- name: PHP Type Guard
  uses: eq12/php-type-guard-action@v1
  with:
    custom-rules: 'type-guard-rules.json'
    type-coverage-threshold: 90
```

### **Framework-Specific Rules**

#### **Laravel Projects**
```yaml
- name: PHP Type Guard (Laravel)
  uses: eq12/php-type-guard-action@v1  
  with:
    type-coverage-threshold: 85
    exclude-paths: 'vendor/,bootstrap/cache/,storage/'
    custom-rules: '.github/laravel-type-rules.json'
```

#### **Symfony Projects**  
```yaml
- name: PHP Type Guard (Symfony)
  uses: eq12/php-type-guard-action@v1
  with:
    type-coverage-threshold: 90
    exclude-paths: 'vendor/,var/cache/,var/log/'
    phpstan-level: 7
```

#### **WordPress Projects**
```yaml
- name: PHP Type Guard (WordPress)
  uses: eq12/php-type-guard-action@v1
  with:
    type-coverage-threshold: 75
    fail-on-missing-param: false  # WordPress hooks often untyped
    exclude-paths: 'wp-admin/,wp-includes/,vendor/'
```

---

## 📈 **Type Coverage Trends**

Track your project's type safety improvement over time:

```yaml
- name: PHP Type Guard with Trends
  uses: eq12/php-type-guard-action@v1
  with:
    type-coverage-threshold: 80
    generate-report: true
    
- name: Upload Coverage Trend
  uses: actions/upload-artifact@v3
  with:
    name: type-coverage-${{ github.run_number }}
    path: type-coverage-report.html
```

---

## 🏢 **Enterprise Features**

### **Team Dashboards**
- 📊 **Centralized type coverage** across all repositories
- 📈 **Team progress tracking** and improvement metrics  
- 🎯 **Custom goals** and type safety KPIs
- 👥 **Developer scorecards** and recognition

### **Advanced Analysis**
- 🔬 **Deep type inference** using static analysis
- 🧠 **Machine learning** suggestions for better types
- 🔄 **Automated type refactoring** recommendations
- 🚀 **Performance impact** analysis of type improvements

### **Integration Options**
- 💬 **Slack notifications** for type violations
- 📧 **Email reports** for team leads
- 🔌 **API access** for custom integrations  
- 📊 **Metrics export** to analytics platforms

---

## 💰 **Pricing**

### **Free Tier**
- ✅ **Public repositories** (unlimited)
- ✅ **Basic type coverage** analysis
- ✅ **PR comments** and status checks
- ✅ **Standard HTML reports**

### **Pro - $29/month**
- ✅ **Private repositories** (unlimited)
- ✅ **Advanced type inference** 
- ✅ **Custom rules** and patterns
- ✅ **Team analytics** dashboard
- ✅ **Priority support**

### **Enterprise - $199/month**
- ✅ **Unlimited everything**
- ✅ **Self-hosted runners** support
- ✅ **Custom integrations**
- ✅ **Dedicated success manager**
- ✅ **SLA guarantees**

---

## 🛠️ **Supported Environments**

- ✅ **PHP 7.4+** (including PHP 8.0, 8.1, 8.2, 8.3)
- ✅ **All major frameworks** (Laravel, Symfony, WordPress, etc.)
- ✅ **GitHub Actions** (ubuntu-latest, windows-latest, macos-latest)  
- ✅ **Self-hosted runners** (Pro/Enterprise)
- ✅ **Monorepos** and complex project structures

---

## 🎯 **Success Stories**

> **"PHP Type Guard helped us go from 45% to 94% type coverage in 3 months. Our IDE performance is incredible now."**  
> — *Sarah Chen, Engineering Manager at FinTech Startup*

> **"We catch type-related bugs at PR time instead of production. Saved us from 3 major incidents already."**
> — *Marcus Torres, Lead Developer at E-commerce Giant*  

> **"The team loves the instant feedback. Code reviews focus on logic instead of missing type hints."**
> — *Alex Kim, CTO at SaaS Company*

---

## 📞 **Get Started**

### **[Add to Your Repository](https://github.com/marketplace/actions/php-type-guard)**
### **[View Documentation](https://docs.php-type-guard.dev)**  
### **[Enterprise Inquiry](mailto:enterprise@eq12.dev)**

---

## 🤝 **Contributing**

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

### **Development Setup**
```bash
git clone https://github.com/eq12/php-type-guard-action.git
cd php-type-guard-action
composer install
npm install
```

### **Testing**
```bash
# Run PHP tests
composer test

# Run Action tests  
npm test

# Test with act (GitHub Actions locally)
act pull_request -e test/fixtures/pull_request.json
```

---

**Stop shipping type bugs. Start enforcing professional PHP standards.**

[![Use This Action](https://img.shields.io/badge/Use%20This%20Action-PHP%20Type%20Guard-success?style=for-the-badge)](https://github.com/marketplace/actions/php-type-guard)