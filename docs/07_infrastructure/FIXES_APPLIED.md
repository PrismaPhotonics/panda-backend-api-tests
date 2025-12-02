# Fixes Applied to smoke-tests.yml

**Date:** 2025-12-02  
**Issue:** PowerShell command not found  
**Root Cause:** Runner changed or PowerShell unavailable

---

## ✅ Fixes Applied

### Fix 1: Added `shell:` to Last Step ✅

**Before:**
```yaml
- name: Fail workflow if tests failed
  if: always()
  env:
    RUN_TESTS_OUTCOME: ${{ steps.run-smoke-tests.outcome }}
  run: py check_test_failures.py  # ❌ No shell specified
```

**After:**
```yaml
- name: Fail workflow if tests failed
  if: always()
  shell: powershell  # ✅ Added shell
  env:
    RUN_TESTS_OUTCOME: ${{ steps.run-smoke-tests.outcome }}
  run: py check_test_failures.py
```

**Location:** Line 389-393

---

### Fix 2: Initialize `$code` Variable ✅

**Before:**
```yaml
Write-Host "  URL: $BASE/channels"

try {  # ❌ $code might be undefined
  # ...
```

**After:**
```yaml
Write-Host "  URL: $BASE/channels"

$code = "000"  # ✅ Initialize before try block
try {
  # ...
```

**Location:** Line 243 (Preflight step)

---

## ⚠️ Remaining Issue

### All Steps Still Use `shell: powershell`

**Current State:**
- All 10 steps use `shell: powershell`
- If PowerShell not available → all steps fail

**Recommended Fix:**
Change all `shell: powershell` to `shell: pwsh` (PowerShell Core)

**Why `pwsh` is better:**
- ✅ Works on Windows, Linux, macOS
- ✅ More modern and reliable
- ✅ Better for CI/CD environments
- ✅ Cross-platform compatible

---

## 🔄 Next Steps (Optional but Recommended)

### Option 1: Change All to `pwsh` (Best)

Replace all `shell: powershell` with `shell: pwsh`:

```yaml
- name: Set up Python
  shell: pwsh  # Changed from powershell
  run: |
    # ... existing code ...
```

**Requires:** PowerShell Core installed on runner

---

### Option 2: Add Shell Detection

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

## 📋 Summary

### Fixed:
- ✅ Added `shell: powershell` to "Fail workflow" step
- ✅ Initialize `$code` variable before try block

### Still Needs Attention:
- ⚠️ All steps use `shell: powershell` (will fail if PowerShell unavailable)
- ⚠️ Consider changing to `pwsh` for better compatibility

---

**Status:** ✅ Critical fixes applied  
**Next:** Test the workflow and verify it works

