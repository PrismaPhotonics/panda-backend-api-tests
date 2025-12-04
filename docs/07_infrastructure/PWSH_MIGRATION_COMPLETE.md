# PowerShell Core (pwsh) Migration - Complete ✅

**Date:** 2025-12-02  
**File:** `.github/workflows/smoke-tests.yml`  
**Status:** ✅ Migration Complete

---

## ✅ Changes Applied

### All Steps Changed from `powershell` to `pwsh`

**Changed Steps (10 total):**

1. ✅ Set up Python
2. ✅ Install deps
3. ✅ Install project in editable mode
4. ✅ Verify Python and pytest installation
5. ✅ Verify infrastructure access
6. ✅ Preflight – check Focus availability
7. ✅ Run smoke tests
8. ✅ List test result files
9. ✅ Get Check Run ID
10. ✅ Parse and Display Test Results
11. ✅ Fail workflow if tests failed

---

## 🎯 Why `pwsh` is Better

### Advantages:

1. **✅ Cross-platform** - Works on Windows, Linux, macOS
2. **✅ More modern** - PowerShell Core 7+ is the future
3. **✅ Better CI/CD** - More reliable in automated environments
4. **✅ Better error handling** - Improved error messages and debugging
5. **✅ Active development** - Regular updates and improvements

### Compatibility:

- **Windows:** ✅ Works with PowerShell Core (pwsh.exe)
- **Linux:** ✅ Works if PowerShell Core installed
- **macOS:** ✅ Works if PowerShell Core installed

---

## 📋 What Changed

### Before:
```yaml
- name: Set up Python
  shell: powershell  # ❌ Windows-only, may not be available
  run: |
    # ... PowerShell code ...
```

### After:
```yaml
- name: Set up Python
  shell: pwsh  # ✅ Cross-platform PowerShell Core
  run: |
    # ... PowerShell code ...
```

---

## ⚠️ Requirements

### Runner Must Have PowerShell Core Installed

**Windows:**
- PowerShell Core should be installed
- Usually available as `pwsh.exe` in PATH
- Can install via: `winget install Microsoft.PowerShell`

**Linux:**
- Install PowerShell Core:
  ```bash
  # Ubuntu/Debian
  sudo apt-get update
  sudo apt-get install -y wget apt-transport-https software-properties-common
  wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb
  sudo dpkg -i packages-microsoft-prod.deb
  sudo apt-get update
  sudo apt-get install -y powershell
  ```

**macOS:**
- Install via Homebrew:
  ```bash
  brew install --cask powershell
  ```

---

## 🔍 Verification

### Check if pwsh is available:

**Windows:**
```powershell
pwsh --version
```

**Linux/macOS:**
```bash
pwsh --version
```

---

## 📊 Summary

| Item | Before | After |
|------|--------|-------|
| **Shell** | `powershell` | `pwsh` |
| **Platform Support** | Windows only | Windows, Linux, macOS |
| **Steps Changed** | 0 | 11 |
| **Compatibility** | ⚠️ Windows only | ✅ Cross-platform |

---

## ✅ Next Steps

1. **Verify runner has pwsh installed**
   - Check: `pwsh --version` on runner machine
   - If not installed, install PowerShell Core

2. **Test the workflow**
   - Run the workflow manually
   - Verify all steps execute successfully

3. **Monitor for issues**
   - Check if any PowerShell syntax needs adjustment
   - Most PowerShell 5.1 code works in pwsh, but verify

---

## 🔗 Related Documentation

- **PowerShell Core Docs:** https://docs.microsoft.com/powershell/
- **GitHub Actions Shells:** https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#using-a-specific-shell
- **Workflow File:** `.github/workflows/smoke-tests.yml`

---

**Status:** ✅ Migration Complete  
**Next:** Test the workflow to verify it works

