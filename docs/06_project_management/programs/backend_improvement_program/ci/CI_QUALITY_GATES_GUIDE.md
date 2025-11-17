# CI Quality Gates Guide
## Setup, Configuration & Usage

**Last Updated:** 2025-10-29  
**Version:** 1.0

---

## 📋 **Overview**

The CI Quality Gates workflow enforces automated quality checks on every Pull Request. This ensures:
- ✅ Code quality (linting, type checking)
- ✅ Test coverage (≥70% unit tests)
- ✅ Contract validation (OpenAPI/AsyncAPI)
- ✅ Backward compatibility warnings
- ✅ Performance smoke tests
- ✅ Security scanning

---

## 🚀 **Quick Start**

### **1. Enable the Workflow**

Copy the workflow file to your repository:

```bash
# If using GitHub Actions
mkdir -p .github/workflows
cp docs/06_project_management/programs/backend_improvement_program/ci/github_workflow_quality_gates.yml \
   .github/workflows/quality-gates.yml
```

### **2. Configure Python Version**

Edit `.github/workflows/quality-gates.yml`:

```yaml
env:
  PYTHON_VERSION: '3.12'  # Change to your Python version
```

### **3. Install Required Tools**

Ensure these are in your `requirements.txt` or CI environment:

```txt
# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
pytest-xdist>=3.3.0

# Linting & Formatting
ruff>=0.1.0
black>=23.0.0
mypy>=1.6.0

# Contract Testing
openapi-spec-validator>=0.7.0
jsonschema>=4.19.0

# Security
bandit>=1.7.5
safety>=2.3.0

# Performance
pytest-benchmark>=4.0.0
locust>=2.17.0
```

---

## 📊 **Quality Gates Explained**

### **Gate 1: Lint & Type Check** ✅ Required

**What it checks:**
- Code formatting (Ruff, Black)
- Type hints (MyPy)
- Code style violations

**How to pass:**
```bash
# Run locally before pushing:
ruff check src/ tests/
ruff format src/ tests/
black --check src/ tests/
mypy src/
```

**Failure action:** Fix linting errors and reformat code.

---

### **Gate 2: Unit Tests & Coverage** ✅ Required

**What it checks:**
- All unit tests pass
- Code coverage ≥70%

**How to pass:**
```bash
# Run locally:
pytest tests/unit/ --cov=src --cov-report=term --cov-fail-under=70
```

**Failure action:**
- Fix failing tests
- Add tests to increase coverage if below 70%

---

### **Gate 3: Contract Tests** ✅ Required

**What it checks:**
- OpenAPI schema validation
- AsyncAPI schema validation (if applicable)
- Request/response schema compliance

**How to pass:**
```bash
# Run locally:
pytest tests/contract/
```

**Failure action:**
- Fix contract violations
- Update OpenAPI/AsyncAPI specs if needed
- Align code with contracts

---

### **Gate 4: Backward Compatibility** ⚠️ Warning

**What it checks:**
- API breaking changes detected
- Schema versioning issues

**How to pass:**
- Review breaking changes manually
- Document migration path if needed
- Update API version if applicable

**Failure action:** Manual review required (doesn't block merge, but must be reviewed).

---

### **Gate 5: Performance Smoke Tests** ⚠️ Warning

**What it checks:**
- P95 latency < threshold (default: 200ms)
- Basic throughput validation

**How to pass:**
```bash
# Run locally:
pytest tests/performance/smoke/
```

**Failure action:** 
- Investigate performance regression
- Optimize slow endpoints
- Manual review if threshold exceeded

---

### **Gate 6: Security Scan** ⚠️ Warning

**What it checks:**
- Common security vulnerabilities (Bandit)
- Dependency vulnerabilities (Safety)

**How to pass:**
```bash
# Run locally:
bandit -r src/
safety check
```

**Failure action:**
- Fix security issues
- Update vulnerable dependencies
- Manual review required

---

### **Gate 7: Component Tests** ✅ Recommended

**What it checks:**
- Service-level integration tests
- Database/message queue interactions

**How to pass:**
```bash
# Run locally (requires MongoDB & RabbitMQ):
pytest tests/integration/component/
```

**Failure action:**
- Fix integration issues
- Check test environment setup

---

## ⚙️ **Configuration**

### **Adjust Coverage Thresholds**

Edit `.github/workflows/quality-gates.yml`:

```yaml
# Unit tests: Change from 70% to 75%
--cov-fail-under=75

# Component tests: Add coverage threshold
--cov-fail-under=80
```

### **Adjust Performance Thresholds**

Create/update `scripts/check_performance_threshold.py`:

```python
# Example: Check P95 < 200ms
P95_THRESHOLD_MS = 200

# Read from benchmark results and validate
```

### **Customize Linting Rules**

Create `ruff.toml`:

```toml
[tool.ruff]
line-length = 120
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501"]  # Ignore line length errors
```

### **Customize Type Checking**

Create `mypy.ini`:

```ini
[mypy]
python_version = 3.12
warn_return_any = True
warn_unused_configs = True
ignore_missing_imports = True
```

---

## 📊 **Understanding Results**

### **✅ All Checks Pass**

```
✅ All required checks passed
- ✅ Lint & Type Check
- ✅ Unit Tests (75% coverage)
- ✅ Contract Tests
- ✅ Component Tests
```

**Action:** Merge is approved (if other PR requirements met).

---

### **⚠️ Warnings (Non-Blocking)**

```
⚠️ Some warnings, but required checks passed
- ✅ Lint & Type Check
- ✅ Unit Tests
- ⚠️ Backward Compatibility (manual review)
- ⚠️ Performance (P95: 220ms > 200ms)
```

**Action:** Review warnings manually, but merge is allowed.

---

### **❌ Required Checks Failed**

```
❌ Some required checks failed
- ✅ Lint & Type Check
- ❌ Unit Tests (65% coverage < 70%)
- ✅ Contract Tests
```

**Action:** Fix failures before merging.

---

## 🔧 **Troubleshooting**

### **Issue: Workflow Not Running**

**Solution:**
1. Check workflow file is in `.github/workflows/`
2. Verify file syntax (YAML valid)
3. Check GitHub Actions is enabled for repository
4. Verify branch protection rules (if any)

---

### **Issue: Tests Fail Locally but Pass in CI**

**Possible causes:**
- Environment variables differ
- Test data not properly isolated
- Race conditions (fix with proper test isolation)

**Solution:**
```bash
# Run tests in CI-like environment:
docker run -it --rm \
  -v $(pwd):/app \
  python:3.12 \
  bash -c "cd /app && pip install -r requirements.txt && pytest tests/"
```

---

### **Issue: Coverage Too Low**

**Solution:**
1. Identify uncovered code: `pytest --cov=src --cov-report=html`
2. Open `htmlcov/index.html` to see coverage report
3. Add tests for uncovered critical paths
4. Focus on business logic (≥70% core logic)

---

### **Issue: Performance Tests Too Slow**

**Solution:**
1. Move slow tests to nightly suite
2. Use `pytest -m "not slow"` for PR checks
3. Optimize performance test setup/teardown
4. Use `pytest-xdist` for parallel execution

---

## 🚀 **Advanced: Custom Quality Gates**

### **Add Custom Gate**

Example: Add custom validation gate:

```yaml
# Add to workflow
- name: Custom Validation
  run: |
    python scripts/custom_validator.py
    if [ $? -ne 0 ]; then
      echo "Custom validation failed"
      exit 1
    fi
```

### **Add Database Schema Validation**

```yaml
- name: Validate Database Schema
  run: |
    python scripts/validate_db_schema.py
```

### **Add Documentation Check**

```yaml
- name: Check Documentation
  run: |
    python scripts/check_docs.py
```

---

## 📈 **Nightly Jobs (Full Test Suite)**

### **Recommended Nightly Jobs**

Create `.github/workflows/nightly-full-suite.yml`:

```yaml
name: Nightly Full Test Suite

on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily
  workflow_dispatch:  # Manual trigger

jobs:
  full-api-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run full API test suite
        run: pytest tests/integration/api/ -v

  full-performance-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run full performance suite
        run: pytest tests/performance/ -v

  full-e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run full E2E suite
        run: pytest tests/e2e/ -v
```

---

## 📊 **Metrics & Reporting**

### **View Quality Metrics**

1. **GitHub Actions Tab:** View workflow runs
2. **Codecov (if integrated):** View coverage trends
3. **PR Comments:** Automatic summary posted
4. **Artifacts:** Download test reports and coverage

### **Trend Analysis**

Track over time:
- Coverage trends (should increase)
- Test execution time (should be stable)
- Flaky test rate (should decrease)
- Performance metrics (should improve)

---

## ✅ **Best Practices**

1. **Run Locally First:** Always run quality checks locally before pushing
2. **Fix Early:** Address issues in PR, not after merge
3. **Monitor Trends:** Track quality metrics over time
4. **Iterate:** Adjust thresholds based on team maturity
5. **Document:** Keep quality gate documentation updated

---

## 📎 **Related Documents**

- [Feature Design Template](../templates/FEATURE_DESIGN_TEMPLATE.md)
- [Component Test Document](../templates/COMPONENT_TEST_DOCUMENT_TEMPLATE.md)
- [Test Review Checklist](../templates/TEST_REVIEW_CHECKLIST.md)
- [Program Roadmap](../PROGRAM_ROADMAP.md)

---

**Template Version:** 1.0  
**Last Updated:** 2025-10-29  
**Maintained by:** DevOps & QA Teams

---

**[← Back to Program](../../README.md)**


