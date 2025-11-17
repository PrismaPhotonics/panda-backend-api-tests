# 🔗 Xray Integration Guide - Complete Setup

**Date:** October 27, 2025  
**Status:** ✅ Ready to Use  
**Implementation:** Based on your original request model

---

## 📋 What Was Created?

### ✅ Configuration Files
1. **`config/xray_config.yaml`** - Xray configuration
2. **`tests/conftest_xray.py`** - pytest integration hooks

### ✅ Scripts
3. **`scripts/xray_upload.py`** - Upload script for Xray Cloud
4. **`.github/workflows/xray_upload.yml`** - CI/CD integration

### ✅ Documentation
5. **`XRAY_INTEGRATION_GUIDE.md`** (this file) - Complete guide

---

## 🎯 Quick Start

### 1. Setup Environment Variables

```bash
# Linux/Mac
export XRAY_CLIENT_ID="your_client_id"
export XRAY_CLIENT_SECRET="your_client_secret"

# Windows PowerShell
$env:XRAY_CLIENT_ID="your_client_id"
$env:XRAY_CLIENT_SECRET="your_client_secret"

# Windows CMD
set XRAY_CLIENT_ID=your_client_id
set XRAY_CLIENT_SECRET=your_client_secret
```

### 2. Mark Tests with Xray Keys

```python
# tests/integration/api/test_example.py
import pytest

@pytest.mark.xray("PZ-13909")
def test_historic_config_missing_end_time():
    """Test PZ-13909: Historic Configuration Missing end_time Field"""
    pass

@pytest.mark.xray("PZ-13907", "PZ-13909")  # One test covers multiple Xray tests
def test_comprehensive_historic_validation():
    """This one test validates both PZ-13907 and PZ-13909"""
    pass

@pytest.mark.anchor("PZ-5000")
def test_high_level_historic_flow():
    """Anchor test for historic playback"""
    pass
```

### 3. Run Tests with Xray Integration

```bash
# Run tests with Xray
pytest tests/ --xray

# Run specific test
pytest tests/integration/api/test_example.py::test_historic_config_missing_end_time --xray

# Generate reports
pytest tests/ \
  --xray \
  --junitxml=reports/junit.xml \
  --html=reports/report.html
```

### 4. Upload Results to Xray

```bash
# Upload automatically detected report
python scripts/xray_upload.py

# Upload specific format
python scripts/xray_upload.py --format json
python scripts/xray_upload.py --format junit

# Link to existing Test Execution
python scripts/xray_upload.py --test-exec-key PZ-EXE-123
```

---

## 🏗️ Architecture: Anchor Test Model

### How It Works

```
┌─────────────────────────────────────────────────┐
│ Automated Test (pytest)                         │
│                                                  │
│  @pytest.mark.xray("PZ-13909")                  │
│  def test_historic_config():                     │
│      pass                                        │
└────────────┬──────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│ Xray Test: PZ-13909 (Anchor)                    │
│  Type: Automated                                 │
│  Status: Automated                               │
└────────────┬──────────────────────────────────────┘
             │
             ▼ (Linked via Issues/Test Sets)
┌─────────────────────────────────────────────────┐
│ Manual Tests / Requirements                      │
│  • PZ-13907 (manual)                            │
│  • PZ-13908 (manual)                            │
└─────────────────────────────────────────────────┘
```

### Why Anchor Tests?

✅ **One-to-Many Mapping:** One automated test can validate multiple manual tests  
✅ **Flexible:** Easy to refactor later to 1:1 if needed  
✅ **Clear Traceability:** Links show coverage  
✅ **No Breaking Changes:** Manual tests stay as-is

---

## 📊 Example: Mapping Current Tests

Based on your CSV, here's how to map:

### Test 1: PZ-13909 - Historic Configuration Missing end_time

```python
# tests/integration/api/test_prelaunch_validations.py
@pytest.mark.xray("PZ-13909")
def test_time_range_validation_missing_end_time(focus_server_api):
    """PZ-13909: Historic Configuration Missing end_time Field"""
    # Your test logic
    pass
```

### Test 2: PZ-13984 - Future Timestamp Validation

```python
# tests/integration/api/test_prelaunch_validations.py
@pytest.mark.xray("PZ-13984")
def test_time_range_validation_future_timestamps(focus_server_api):
    """PZ-13984: Future Timestamp Validation Gap"""
    # Your existing test (already has the bug!)
    pass
```

### Test 3: PZ-13985 - LiveMetadata Missing Fields

```python
# tests/integration/api/test_api_endpoints_high_priority.py
@pytest.mark.xray("PZ-13985")
def test_get_live_metadata(focus_server_api):
    """PZ-13985: LiveMetadata Missing Required Fields"""
    # Your existing test
    pass
```

---

## 🔧 Step-by-Step Implementation

### Step 1: Add Xray Markers to Existing Tests

```bash
# Find all test files
find tests/ -name "test_*.py" | head -5

# Example mapping:
# tests/integration/api/test_prelaunch_validations.py → PZ-13909, PZ-13984
# tests/data_quality/test_mongodb_data_quality.py → PZ-13983 (optional)
# tests/integration/api/test_api_endpoints_high_priority.py → PZ-13985
```

### Step 2: Create Anchor Tests in Xray

For each category, create an Anchor Test:

1. **Go to Jira** → Create Test Issue
2. **Type:** Test  
3. **Summary:** `Focus Server: Historic Playback (Anchor)`
4. **Test Type:** Automated
5. **Test Automation Status:** Automated
6. **Test Key:** `PZ-13909-ANCHOR` (for example)

### Step 3: Link Manual Tests to Anchor

1. **In Jira:** Open manual test (e.g., PZ-13907)
2. **Add link:** Link to PZ-13909-ANCHOR (Relates/Tests)
3. **Test Set:** Add both to same Test Set

### Step 4: Run Tests and Upload

```bash
# Run tests
pytest tests/ --xray -v

# Check generated reports
ls -lh reports/
# reports/xray-exec.json
# reports/junit.xml
# reports/report.html

# Upload to Xray
python scripts/xray_upload.py
```

### Step 5: Verify in Jira

1. **Go to Xray** → Test Execution
2. **Find your execution** (created by upload)
3. **See results:** Pass/Fail per test
4. **Drill down:** Click test to see details

---

## 🎨 CI/CD Integration

### GitHub Actions (Already Created!)

The workflow `.github/workflows/xray_upload.yml` will:

1. ✅ Run tests automatically
2. ✅ Generate Xray JSON
3. ✅ Upload to Xray
4. ✅ Comment on PRs
5. ✅ Upload artifacts

### Setup GitHub Secrets

```bash
# In GitHub repo → Settings → Secrets → Actions
# Add:
XRAY_CLIENT_ID
XRAY_CLIENT_SECRET
```

### Manual Run

```bash
# Trigger via GitHub CLI
gh workflow run xray_upload.yml

# Or manually trigger in GitHub UI:
# Actions → Upload Test Results to Xray → Run workflow
```

---

## 📈 Results & Reporting

### What Gets Reported to Xray?

✅ **Test Status:** PASSED / FAILED  
✅ **Test Execution:** New execution created per run  
✅ **Test Duration:** Start/finish time  
✅ **Comments:** Error messages  
✅ **Evidences:** Logs, screenshots (optional)

### Viewing Results

1. **Jira → Xray**
2. **Test Execution**
3. **Your Test** → See status
4. **Test Plan Coverage** → See which tests covered

---

## 🔄 Migration Path

### Currently (Manual Only)

```
Jira Tests (Manual) → Run manually → Update Jira
```

### With This Integration (Hybrid)

```
Jira Anchor Tests (Automated) ←→ pytest (Automated)
      ↓
   Linked to Manual Tests
```

### Future (Full Automation)

```
Jira Tests (Automated) ←→ pytest (1:1) ←→ Full automation
```

---

## 🐛 Troubleshooting

### "Authentication failed"

```bash
# Check environment variables
echo $XRAY_CLIENT_ID
echo $XRAY_CLIENT_SECRET

# Re-authenticate
export XRAY_CLIENT_ID="your_client_id"
export XRAY_CLIENT_SECRET="your_client_secret"
```

### "No Xray keys found"

```python
# Check that tests have markers
@pytest.mark.xray("PZ-1234")  # ← Make sure this exists
def test_something():
    pass
```

### "File not found: reports/xray-exec.json"

```bash
# Run tests first
pytest tests/ --xray

# Check that conftest_xray.py is loaded
pytest tests/ --collect-only | grep xray
```

---

## 📚 Next Steps

1. ✅ **Add Xray markers to your tests** (use examples above)
2. ✅ **Create Anchor Tests in Jira** (1 per category)
3. ✅ **Link manual tests to anchors**
4. ✅ **Run first upload** to test
5. ✅ **Monitor results in Xray**

---

## 🎯 Summary

**What you asked for:**
> "לשייכים בין Xray לבין בדיקות האוטומציה גם כשאין התאמה 1:1"

**What you got:**
✅ Anchor Test model (no 1:1 required!)  
✅ pytest markers support  
✅ Automatic JSON generation  
✅ CI/CD integration  
✅ Complete upload script  
✅ Step-by-step guide

**Ready to use!** 🚀

---

## 📞 Support

**Files created:**
- `config/xray_config.yaml`
- `tests/conftest_xray.py`
- `scripts/xray_upload.py`
- `.github/workflows/xray_upload.yml`
- `XRAY_INTEGRATION_GUIDE.md` (this file)

**Next:** Add `@pytest.mark.xray("KEY")` to your tests and run!

