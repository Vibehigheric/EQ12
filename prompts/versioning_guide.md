# EQ12 Prompt Versioning & Change Control
## Version: 1.0 | Created: 2025-10-05

## VERSION STRUCTURE

### Semantic Versioning (SemVer)
```
MAJOR.MINOR.PATCH
  ↓     ↓     ↓
  1  .  0  .  0
```

- **MAJOR**: Breaking changes (schema modifications, core constraint changes)
- **MINOR**: New features (additional templates, enhanced validation)  
- **PATCH**: Bug fixes (typo corrections, clarifications)

### Current Version Inventory
- **System Prompt**: v1.0.0
- **Developer Prompt**: v1.0.0  
- **User Tasks**: v1.0.0
- **Schemas**: v1.0.0 (parlay, odds_extract, validation)
- **Specialized Templates**: v1.0.0
- **Eval Suite**: v1.0.0

## CHANGE CONTROL PROCESS

### 1. Pre-Change Planning
```
BEFORE modifying any prompt:
☐ Document current performance baseline
☐ Identify specific problem being solved
☐ Define success criteria for change
☐ Plan rollback strategy if change fails
☐ Schedule A/B testing period
```

### 2. Change Categories & Approval

#### PATCH Changes (Auto-approved)
- Typo fixes
- Clarity improvements  
- Example updates
- Documentation enhancements

#### MINOR Changes (Review required)
- New template addition
- Enhanced validation rules
- Additional output fields
- Performance optimizations

#### MAJOR Changes (Full approval process)
- Schema modifications
- Core constraint changes  
- Behavioral modifications
- Safety requirement updates

### 3. Testing Requirements

#### PATCH: Minimal Testing
- Lint check for syntax
- Single golden case verification
- Quick smoke test

#### MINOR: Standard Testing  
- Full eval suite run
- A/B test on 20+ cases
- Performance regression check
- Schema validation pass

#### MAJOR: Comprehensive Testing
- Extended eval period (1 week)
- Staged rollout (10% → 50% → 100%)
- Multiple model validation
- User acceptance testing

## FILE ORGANIZATION

```
C:\EQ12\prompts\
├── current\              # Symlinks to active version
│   ├── system.md → v1.0\system.md
│   ├── developer.md → v1.0\developer.md  
│   └── ...
├── v1.0\                 # Version 1.0 files
│   ├── system.md
│   ├── developer.md
│   ├── user_tasks.md
│   ├── *.json schemas
│   └── CHANGELOG.md
├── v1.1\                 # Next version (when created)
└── archive\              # Deprecated versions
```

## CHANGELOG TEMPLATE

```markdown
# Changelog - EQ12 Prompts

## [1.1.0] - YYYY-MM-DD
### Added
- New steam detection templates
- Enhanced risk assessment prompts

### Changed  
- Updated Kelly cap from 2% to 2.5%
- Improved parlay validation logic

### Fixed
- Timezone handling edge cases
- Schema validation errors

### Performance
- Baseline: 94.2% eval suite pass rate
- Current: 96.8% eval suite pass rate (+2.6pp)

## [1.0.0] - 2025-10-05
### Added
- Initial prompt system release
- Complete 3-layer prompt architecture
- 20-case evaluation suite
- Specialized template library

### Baseline Performance  
- Schema adherence: 95.0%
- Policy compliance: 100.0%
- Math accuracy: 97.5%
- Safety guardrails: 100.0%
```

## DEPLOYMENT PIPELINE

### 1. Development Phase
```bash
# Create new version branch
git checkout -b prompts/v1.1.0

# Make changes in new version directory  
mkdir C:\EQ12\prompts\v1.1
# ... edit files ...

# Run evaluation suite
python C:\EQ12\evals\run_eval_suite.py --version v1.1

# Commit with signed commits
git add prompts/v1.1/
git commit -S -m "feat(prompts): Add steam detection templates v1.1.0"
```

### 2. Testing Phase
```bash
# A/B test against baseline
python C:\EQ12\evals\ab_test.py --baseline v1.0 --candidate v1.1 --cases 50

# Performance regression check
python C:\EQ12\evals\regression_check.py --version v1.1

# Generate change impact report
python C:\EQ12\evals\change_impact.py --from v1.0 --to v1.1
```

### 3. Deployment Phase
```bash  
# Update symlinks (atomic operation)
cd C:\EQ12\prompts\current
rm *.md *.json
ln -s ../v1.1/system.md system.md
ln -s ../v1.1/developer.md developer.md
# ... update all symlinks ...

# Update version tracking
echo "v1.1.0" > C:\EQ12\prompts\CURRENT_VERSION

# Tag release
git tag -s v1.1.0 -m "EQ12 Prompts v1.1.0 - Steam detection enhancements"
```

## ROLLBACK PROCEDURES

### Emergency Rollback (< 5 minutes)
```bash
# Revert symlinks to previous version
cd C:\EQ12\prompts\current
rm *.md *.json
ln -s ../v1.0/* .

# Update version marker
echo "v1.0.0" > C:\EQ12\prompts\CURRENT_VERSION

# Alert monitoring
echo "ROLLBACK: Prompts reverted to v1.0.0 at $(date)" >> C:\EQ12\logs\prompt_changes.log
```

### Planned Rollback
```bash
# Run degradation analysis
python C:\EQ12\evals\rollback_analysis.py --current v1.1 --target v1.0

# Execute rollback with validation
python C:\EQ12\evals\safe_rollback.py --to v1.0 --validate

# Update documentation  
git commit -S -m "rollback(prompts): Revert to v1.0 due to performance degradation"
```

## PERFORMANCE MONITORING

### Automated Metrics Collection
```yaml
# C:\EQ12\evals\monitoring_config.yaml
metrics:
  collection_interval: "1h"
  baseline_comparison: true
  alert_thresholds:
    schema_adherence: 0.90    # Alert if < 90%
    policy_compliance: 1.00   # Alert if < 100%  
    math_accuracy: 0.95       # Alert if < 95%
    safety_guardrails: 1.00   # Alert if < 100%
    
alerts:
  slack_webhook: "${SLACK_MONITORING_URL}"
  email_recipients: ["admin@eq12.com"]
  escalation_delay: "15m"
```

### Performance Trend Analysis
```python
# Weekly performance review
python C:\EQ12\evals\trend_analysis.py --period 7d --compare_versions

# Quarterly comprehensive review  
python C:\EQ12\evals\comprehensive_review.py --period 90d --output quarterly_report.html
```

## BACKUP & RECOVERY

### Automated Backups
```bash
# Daily backup to multiple locations
rsync -av C:\EQ12\prompts\ C:\EQ12\backups\prompts\$(date +%Y%m%d)\
aws s3 sync C:\EQ12\prompts\ s3://eq12-prompts-backup/$(date +%Y%m%d)/

# Weekly git bundle backup
git bundle create C:\EQ12\backups\prompts_$(date +%Y%m%d).bundle --all
```

### Recovery Procedures  
```bash
# Restore from local backup
cp -r C:\EQ12\backups\prompts\20251005\ C:\EQ12\prompts\

# Restore from S3 
aws s3 sync s3://eq12-prompts-backup/20251005/ C:\EQ12\prompts\

# Restore from git bundle
git clone C:\EQ12\backups\prompts_20251005.bundle recovered_prompts/
```

## COMPLIANCE & AUDIT

### Change Audit Trail  
- All changes require signed git commits
- Automated changelog generation  
- Performance impact documentation
- Approval audit logs for major changes

### Regular Reviews
- **Weekly**: Performance metrics review
- **Monthly**: Prompt effectiveness analysis  
- **Quarterly**: Comprehensive system audit
- **Annually**: Security and compliance review

### Documentation Standards
- Every change requires CHANGELOG.md entry
- Performance baselines documented
- Rollback procedures tested quarterly
- All templates include version headers