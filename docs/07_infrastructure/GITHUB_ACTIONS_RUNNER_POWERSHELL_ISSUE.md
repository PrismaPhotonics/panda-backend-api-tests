# GitHub Actions Runner - PowerShell Not Found Issue

**Run:** Smoke Tests #289  
**URL:** https://github.com/PrismaPhotonics/panda-backend-api-tests/actions/runs/19851454352  
**Date:** December 2, 2025 08:04  
**Status:** ❌ FAILED  
**Duration:** 28s

---

## 🔴 Problem Summary

The GitHub Actions workflow fails immediately with **"powershell: command not found"** errors. All steps that use `shell: powershell` fail because PowerShell cannot be found on the runner.

### Error Messages:

```
[smoke] powershell: command not found (5 errors)
[smoke] No files were found with the provided path: test-results\*.xml (2 warnings)
```

---

## 🔍 Root Cause Analysis

### Workflow Configuration:

**File:** `.github/workflows/smoke-tests.yml`  
**Runner Configuration:**
```yaml
runs-on: [self-hosted, windows, "panda_automation"]
```

**All Steps Use:**
```yaml
shell: powershell
```

### The Problem:

The runner labeled `"panda_automation"` is either:
1. ❌ **Not a Windows runner** - Running on Linux/macOS where PowerShell is not available by default
2. ❌ **Windows runner without PowerShell** - PowerShell is not installed or not in PATH
3. ❌ **Misconfigured labels** - The runner doesn't have the `windows` label properly set

---

## 📋 Evidence from Run #289

### Failed Steps:

1. **Step 3:** `Set up Python` - `powershell: command not found`
2. **Step 10:** `Install deps` - `powershell: command not found`
3. **Step 11:** `Install project in editable mode` - `powershell: command not found`
4. **Step 12:** `Verify Python and pytest installation` - `powershell: command not found`
5. **Step 13:** `Verify infrastructure access` - `powershell: command not found`

### Warnings:

- **Step 15:** No files found: `test-results\*.xml` (because tests never ran)
- **Step 11:** No files found: `test-results/junit-*.xml` (because tests never ran)

---

## ✅ Solutions

### Solution 1: Verify Runner OS and Labels (RECOMMENDED)

**Check the runner configuration:**

1. Go to: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
2. Find the runner named `panda_automation`
3. Verify:
   - ✅ **OS:** Windows
   - ✅ **Labels:** Should include `self-hosted`, `windows`, `panda_automation`
   - ✅ **Status:** Online/Idle

**If the runner is Linux/macOS:**
- Either install PowerShell Core (`pwsh`) on the runner
- Or change the workflow to use `bash`/`sh` instead of `powershell`

---

### Solution 2: Install PowerShell on the Runner

**If the runner is Windows but PowerShell is missing:**

#### Option A: Use PowerShell Core (pwsh)

Update the workflow to use `pwsh` instead of `powershell`:

```yaml
shell: pwsh  # PowerShell Core (cross-platform)
```

#### Option B: Install PowerShell on Windows Runner

On the Windows machine running the runner:

```powershell
# Check if PowerShell exists
Get-Command powershell -ErrorAction SilentlyContinue

# If not found, PowerShell might be in a different location
# Try: C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
```

---

### Solution 3: Use Default Shell (Fallback)

If PowerShell is not available, use the default shell for the OS:

```yaml
# Remove shell: powershell from steps
# GitHub Actions will use the default shell for the OS
```

**For Windows:** Default is `cmd.exe` (not PowerShell)  
**For Linux:** Default is `bash`

---

### Solution 4: Detect OS and Use Appropriate Shell

Update the workflow to detect the OS and use the appropriate shell:

```yaml
- name: Set up Python
  shell: ${{ runner.os == 'Windows' && 'powershell' || 'bash' }}
  run: |
    # Use OS-appropriate commands
    if [ "${{ runner.os }}" == "Windows" ]; then
      # PowerShell commands
    else
      # Bash commands
    fi
```

---

## 🔧 Immediate Fix (Quick Workaround)

### Option 1: Change Shell to `pwsh` (PowerShell Core)

Update all `shell: powershell` to `shell: pwsh`:

```yaml
- name: Set up Python
  shell: pwsh  # Changed from powershell
  run: |
    # ... existing code ...
```

**Note:** Requires PowerShell Core to be installed on the runner.

---

### Option 2: Use `cmd` for Windows

Change to `cmd` shell (Windows Command Prompt):

```yaml
- name: Set up Python
  shell: cmd
  run: |
    @echo off
    py --version
    REM ... rest of commands ...
```

**Note:** Requires rewriting all PowerShell commands to CMD syntax.

---

### Option 3: Use `bash` if Runner is Linux

If the runner is actually Linux, change to `bash`:

```yaml
- name: Set up Python
  shell: bash
  run: |
    python3 --version
    # ... rest of commands ...
```

**Note:** Requires rewriting all PowerShell commands to Bash syntax.

---

## 📝 Verification Steps

### Step 1: Check Runner Status

1. Go to: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
2. Find `panda_automation` runner
3. Check:
   - **Status:** Should be "Online" or "Idle"
   - **OS:** Should show "Windows" or "Linux"
   - **Labels:** Should include `windows` if it's Windows

### Step 2: Test Runner Locally

SSH into the runner machine and test:

```powershell
# On Windows runner
powershell --version
# Should output: PowerShell version number

# On Linux runner
pwsh --version
# Should output: PowerShell Core version number
```

### Step 3: Check Runner Logs

On the runner machine, check logs:

**Windows:**
```
C:\actions-runner\_diag\Runner_*.log
```

**Linux:**
```
~/actions-runner/_diag/Runner_*.log
```

Look for errors related to PowerShell or shell execution.

---

## 🎯 Recommended Action Plan

### Immediate (Fix Current Run):

1. ✅ **Check runner configuration** at: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
2. ✅ **Verify runner OS** - Is it Windows or Linux?
3. ✅ **Check runner labels** - Does it have `windows` label?

### Short-term (Fix Workflow):

**If runner is Windows:**
- Option A: Install PowerShell Core (`pwsh`) and change `shell: powershell` to `shell: pwsh`
- Option B: Verify PowerShell is in PATH: `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`

**If runner is Linux:**
- Option A: Install PowerShell Core: `sudo apt-get install -y powershell` (or use `pwsh`)
- Option B: Rewrite workflow to use `bash` instead of `powershell`

### Long-term (Best Practice):

1. ✅ **Document runner requirements** - PowerShell version, installation path
2. ✅ **Add runner health checks** - Verify PowerShell availability before running tests
3. ✅ **Use conditional shells** - Detect OS and use appropriate shell

---

## 📊 Workflow Changes Needed

### Current (Broken):

```yaml
- name: Set up Python
  shell: powershell  # ❌ Fails if PowerShell not found
  run: |
    py --version
```

### Fixed Option 1 (PowerShell Core):

```yaml
- name: Set up Python
  shell: pwsh  # ✅ PowerShell Core (cross-platform)
  run: |
    py --version
```

### Fixed Option 2 (OS Detection):

```yaml
- name: Set up Python
  shell: ${{ runner.os == 'Windows' && 'powershell' || 'bash' }}
  run: |
    if [ "${{ runner.os }}" == "Windows" ]; then
      py --version
    else
      python3 --version
    fi
```

### Fixed Option 3 (Default Shell):

```yaml
- name: Set up Python
  # No shell specified - uses default for OS
  run: |
    # Use OS-agnostic commands or detect OS
    py --version || python3 --version
```

---

## 🔗 Related Documentation

- **Runner Setup:** `docs/07_infrastructure/github_actions_local_and_self_hosted.md`
- **Runner Scripts:** `scripts/setup_self_hosted_runner.ps1`
- **Workflow File:** `.github/workflows/smoke-tests.yml`

---

## 📞 Next Steps

1. **Check runner configuration** at the provided URL
2. **Verify runner OS** (Windows vs Linux)
3. **Choose appropriate fix** based on runner OS
4. **Update workflow** with the chosen solution
5. **Test the fix** by running the workflow again

---

**Generated:** 2025-12-02  
**Issue:** PowerShell command not found on self-hosted runner  
**Status:** 🔴 Needs immediate attention

