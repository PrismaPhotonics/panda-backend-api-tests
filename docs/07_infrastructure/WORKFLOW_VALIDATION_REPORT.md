# Workflow Validation Report - smoke-tests.yml

**Date:** 2025-12-02  
**File:** `.github/workflows/smoke-tests.yml`  
**Status:** ✅ Syntax Valid | ⚠️ Potential Issues Found

---

## ✅ Syntax Validation

### YAML Structure:
- ✅ Valid YAML syntax
- ✅ Proper indentation
- ✅ All required fields present

---

## 🔍 Detailed Analysis

### 1. Workflow Triggers ✅

```yaml
on:
  push:
    branches: [ main, develop, master, "chore/add-roy-tests" ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      require_server:
        description: "Fail if Focus server is unreachable"
        default: "true"
        type: choice
        options: [ "true", "false" ]
```

**Status:** ✅ Valid

---

### 2. Runner Configuration ⚠️

```yaml
runs-on: [self-hosted, windows, "panda_automation"]
```

**Issues Found:**
- ⚠️ **Label `windows` is lowercase** - GitHub Actions labels are case-sensitive
- ⚠️ **All steps use `shell: powershell`** - Will fail if PowerShell not available

**Recommendations:**
- Verify runner has label `windows` (not `Windows`)
- Consider using `shell: pwsh` (PowerShell Core) for better compatibility
- Or add fallback detection for shell availability

---

### 3. Environment Variables ✅

```yaml
env:
  FOCUS_SERVER_HOST: ${{ secrets.FOCUS_SERVER_HOST || '10.10.10.100' }}
  FOCUS_SERVER_PORT: ${{ secrets.FOCUS_SERVER_PORT || '' }}
  FOCUS_API_PREFIX: ${{ secrets.FOCUS_API_PREFIX || '/focus-server' }}
  VERIFY_SSL: ${{ secrets.VERIFY_SSL || 'false' }}
  REQUIRE_SERVER: ${{ inputs.require_server || secrets.REQUIRE_SERVER || 'true' }}
  ENVIRONMENT: ${{ secrets.ENVIRONMENT || 'staging' }}
  PYTHONDONTWRITEBYTECODE: 1
  PYTHONUNBUFFERED: 1
```

**Status:** ✅ Valid - Good use of defaults

---

### 4. Steps Analysis

#### Step 1: Checkout ✅
```yaml
- name: Checkout
  uses: actions/checkout@v4
```
**Status:** ✅ Valid

---

#### Step 2: Set up Python ⚠️
```yaml
- name: Set up Python
  shell: powershell
```

**Issues:**
- ⚠️ Uses `shell: powershell` - Will fail if PowerShell not found
- ✅ Good fallback logic for finding Python
- ✅ Proper PATH handling

**Recommendation:**
- Change to `shell: pwsh` or add PowerShell detection

---

#### Step 3: Install deps ⚠️
```yaml
- name: Install deps
  shell: powershell
```

**Issues:**
- ⚠️ Uses `shell: powershell`
- ✅ Good dependency installation logic

---

#### Step 4: Install project ⚠️
```yaml
- name: Install project in editable mode
  shell: powershell
```

**Issues:**
- ⚠️ Uses `shell: powershell`
- ✅ Good error handling with `continue-on-error` logic

---

#### Step 5: Verify Python ⚠️
```yaml
- name: Verify Python and pytest installation
  shell: powershell
```

**Issues:**
- ⚠️ Uses `shell: powershell`

---

#### Step 6: Verify infrastructure ⚠️
```yaml
- name: Verify infrastructure access
  shell: powershell
```

**Issues:**
- ⚠️ Uses `shell: powershell`
- ✅ Comprehensive infrastructure checks
- ✅ Good error messages

---

#### Step 7: Preflight check ⚠️
```yaml
- name: Preflight – check Focus availability
  id: preflight
  shell: powershell
  continue-on-error: true
```

**Issues:**
- ⚠️ Uses `shell: powershell`
- ✅ Good use of `continue-on-error`
- ✅ Proper output handling

**Bug Found:**
- ⚠️ Line 281: Variable `$code` might not be defined if exception occurs before try block
- Should initialize `$code = "000"` before try block

---

#### Step 8: Run smoke tests ⚠️
```yaml
- name: Run smoke tests
  id: run-smoke-tests
  shell: powershell
  continue-on-error: true
```

**Issues:**
- ⚠️ Uses `shell: powershell`
- ✅ Good error handling
- ✅ Proper XML generation for skipped tests

---

#### Step 9: List test results ⚠️
```yaml
- name: List test result files
  shell: powershell
  if: always()
```

**Issues:**
- ⚠️ Uses `shell: powershell`
- ✅ Good use of `if: always()`

---

#### Step 10: Publish Test Results ✅
```yaml
- name: Publish Test Results
  uses: dorny/test-reporter@v1
  if: always()
```

**Status:** ✅ Valid - Uses action, not shell

---

#### Step 11: Get Check Run ID ⚠️
```yaml
- name: Get Check Run ID
  shell: powershell
```

**Issues:**
- ⚠️ Uses `shell: powershell`
- ✅ Good error handling

---

#### Step 12: Parse Test Results ⚠️
```yaml
- name: Parse and Display Test Results
  shell: powershell
```

**Issues:**
- ⚠️ Uses `shell: powershell`
- ⚠️ **Missing file check** - Assumes `parse_junit_results.py` exists
- Should add: `if: always() && steps.run-smoke-tests.outcome != 'skipped'`

---

#### Step 13: Fail workflow ⚠️
```yaml
- name: Fail workflow if tests failed
  shell: powershell
```

**Issues:**
- ⚠️ Uses `shell: powershell`
- ✅ Good logic for checking test results

---

#### Step 14: Upload artifacts ✅
```yaml
- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: smoke-test-reports
    path: test-results\*.xml
    if-no-files-found: warn
```

**Status:** ✅ Valid

---

## 🐛 Issues Found

### Critical Issues:

1. **❌ All steps use `shell: powershell`**
   - **Impact:** Will fail if PowerShell not available on runner
   - **Fix:** Change to `shell: pwsh` or add PowerShell detection

2. **⚠️ Variable `$code` might be undefined** (Line 281)
   - **Location:** Preflight step
   - **Fix:** Initialize `$code = "000"` before try block

3. **⚠️ Missing file check** (Line 387)
   - **Location:** Parse Test Results step
   - **Issue:** Assumes `parse_junit_results.py` exists
   - **Fix:** Add file existence check or make step conditional

### Medium Issues:

4. **⚠️ Label case sensitivity**
   - **Issue:** Uses `windows` (lowercase) - verify runner has this exact label
   - **Recommendation:** Check runner labels match exactly

5. **⚠️ No PowerShell fallback**
   - **Issue:** No detection or fallback if PowerShell unavailable
   - **Recommendation:** Add shell detection step

---

## ✅ What's Good

1. ✅ Comprehensive error handling
2. ✅ Good use of `continue-on-error` where appropriate
3. ✅ Proper use of `if: always()` for cleanup steps
4. ✅ Good environment variable defaults
5. ✅ Proper output handling for steps
6. ✅ Good infrastructure verification
7. ✅ Proper test result XML generation

---

## 🔧 Recommended Fixes

### Fix 1: Change Shell to pwsh (Recommended)

Replace all `shell: powershell` with `shell: pwsh`:

```yaml
- name: Set up Python
  shell: pwsh  # Changed from powershell
  run: |
    # ... existing code ...
```

**Pros:**
- Works on Windows, Linux, macOS
- More modern PowerShell
- Better error handling

**Cons:**
- Requires PowerShell Core installation on runner

---

### Fix 2: Add Shell Detection (Alternative)

Add a step to detect available shell:

```yaml
- name: Detect Shell
  id: detect-shell
  run: |
    if command -v pwsh &> /dev/null; then
      echo "shell=pwsh" >> $GITHUB_OUTPUT
    elif command -v powershell &> /dev/null; then
      echo "shell=powershell" >> $GITHUB_OUTPUT
    else
      echo "shell=bash" >> $GITHUB_OUTPUT
    fi

- name: Set up Python
  shell: ${{ steps.detect-shell.outputs.shell }}
  run: |
    # ... existing code ...
```

---

### Fix 3: Fix Variable Initialization

In Preflight step, initialize `$code` before try:

```yaml
run: |
  $code = "000"  # Initialize before try block
  echo "reachable=false" | Out-File -FilePath $env:GITHUB_OUTPUT -Append -Encoding utf8
  echo "status=$code" | Out-File -FilePath $env:GITHUB_OUTPUT -Append -Encoding utf8
  
  # ... rest of code ...
```

---

### Fix 4: Add File Check for Parse Step

```yaml
- name: Parse and Display Test Results
  if: always() && steps.run-smoke-tests.outcome != 'skipped' && hashFiles('parse_junit_results.py') != ''
  shell: powershell
  run: |
    if (Test-Path parse_junit_results.py) {
      py parse_junit_results.py
    } else {
      Write-Host "::warning::parse_junit_results.py not found, skipping"
    }
```

---

## 📊 Summary

| Category | Status | Count |
|----------|--------|-------|
| **Syntax Errors** | ✅ None | 0 |
| **Critical Issues** | ⚠️ 3 | 3 |
| **Medium Issues** | ⚠️ 2 | 2 |
| **Warnings** | ⚠️ Multiple | - |
| **Valid Steps** | ✅ 14 | 14 |

---

## 🎯 Priority Actions

1. **HIGH:** Fix PowerShell shell issue (change to `pwsh` or add detection)
2. **MEDIUM:** Fix `$code` variable initialization
3. **MEDIUM:** Add file check for `parse_junit_results.py`
4. **LOW:** Verify runner labels match exactly

---

**Generated:** 2025-12-02  
**Validation Method:** Manual review + YAML syntax check

