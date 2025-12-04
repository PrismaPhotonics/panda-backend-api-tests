# VS Code Terminal Troubleshooting Guide

**Quick Reference for Terminal Launch Failures**

---

## 🚀 Quick Diagnostic

Run the diagnostic script to check your terminal configuration:

```powershell
.\scripts\diagnose_terminal_issues.ps1
```

This will check:
- ✅ VS Code version
- ✅ PowerShell versions (Desktop & Core)
- ✅ Windows version (ConPTY support)
- ✅ Compatibility mode
- ✅ VS Code terminal settings
- ✅ Anti-virus exclusions
- ✅ Legacy console mode
- ✅ Shell availability
- ✅ Environment variables
- ✅ Process conflicts

---

## 🔍 Common Issues & Solutions

### Issue 1: Terminal Exits with Code 1 (WSL)

**Symptom:** Terminal fails with exit code 1, using WSL as default shell

**Solution:**
```powershell
# Check WSL distributions
wslconfig.exe /l

# Set default distribution
wslconfig.exe /setdefault "Ubuntu-20.04"
```

**Note:** `docker-desktop-data` is NOT a valid distribution.

---

### Issue 2: Native Exception Occurred

**Symptom:** "A native exception occurred" error

**Cause:** Anti-virus blocking terminal components

**Critical files that must be excluded:**
```
{install_path}\resources\app\node_modules.asar.unpacked\node-pty\build\Release\winpty.dll
{install_path}\resources\app\node_modules.asar.unpacked\node-pty\build\Release\winpty-agent.exe
{install_path}\resources\app\node_modules.asar.unpacked\node-pty\build\Release\conpty.node
{install_path}\resources\app\node_modules.asar.unpacked\node-pty\build\Release\conpty_console_list.node
```

**Default VS Code path:**
```
%LOCALAPPDATA%\Programs\Microsoft VS Code
```

**Solution by Antivirus:**

#### Cynet Endpoint Security (Most Common)

1. **Open Cynet:**
   - In Windows Security → Click "Open app" under "Cynet Endpoint Security"
   - OR Click "Manage providers" → Open Cynet

2. **Add Exclusion:**
   - Look for "Exclusions", "Exceptions", "Whitelist", or "Exclude Files/Folders"
   - Add folder: `C:\Users\{YourUsername}\AppData\Local\Programs\Microsoft VS Code`
   - Apply changes

3. **Restore Quarantined Files:**
   - Check Cynet quarantine/history
   - Restore any VS Code files that were removed
   - If files are missing, reinstall VS Code

#### Windows Defender

1. Open Windows Security
2. Virus & threat protection → Virus & threat protection settings → Manage settings
3. Exclusions → Add or remove exclusions
4. Add folder → Select VS Code installation folder

#### Other Antivirus Software

- Look for "Exclusions", "Exceptions", or "Whitelist" settings
- Add the entire VS Code installation folder
- Report false positive to antivirus vendor to help prevent future issues

**After adding exclusions:**
1. Restart VS Code
2. If files are still missing, reinstall VS Code
3. Run diagnostic script to verify: `.\scripts\check_vscode_terminal_files.ps1`

---

### Issue 3: Terminal Exits with Code 259

**Symptom:** Exit code 259 (STILL_ACTIVE)

**Causes:**
- Too many terminal processes running
- Anti-virus interference
- Process conflicts

**Solutions:**
1. Kill unused terminal processes:
   ```powershell
   Get-Process | Where-Object {$_.ProcessName -match "powershell|pwsh|cmd|bash"} | Stop-Process -Force
   ```

2. Check anti-virus exclusions (see Issue 2)

3. Restart VS Code

---

### Issue 4: Terminal Exits with Code 3221225786

**Symptom:** Exit code 3221225786 or similar

**Cause:** Legacy console mode enabled

**Solution:**
1. Open `cmd.exe` from Start Menu
2. Right-click title bar → Properties
3. Options tab → **Uncheck "Use legacy console"**
4. Restart VS Code

---

### Issue 5: Compatibility Mode Enabled

**Symptom:** Terminal breaks after Windows upgrade

**Cause:** Compatibility mode automatically enabled

**Solution:**
1. Find VS Code executable:
   - Usually: `%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe`
2. Right-click → Properties
3. Compatibility tab → **Uncheck "Run this program in compatibility mode"**
4. Restart VS Code

---

## ⚙️ VS Code Terminal Settings

### Key Settings to Check

Open Settings (Ctrl+,) and search for these:

| Setting | Description | Default |
|---------|-------------|---------|
| `terminal.integrated.defaultProfile.windows` | Default shell profile | PowerShell |
| `terminal.integrated.profiles.windows` | Defined shell profiles | Auto-detected |
| `terminal.integrated.cwd` | Working directory | `${workspaceFolder}` |
| `terminal.integrated.env.windows` | Environment variables | `{}` |
| `terminal.integrated.inheritEnv` | Inherit VS Code env | `true` |
| `terminal.integrated.windowsEnableConpty` | Use ConPTY backend | `true` |

### View Modified Settings

1. Open Settings (Ctrl+,)
2. Search for: `@modified`
3. Review any terminal-related settings

### Edit settings.json

1. Command Palette (Ctrl+Shift+P)
2. Run: `Preferences: Open User Settings (JSON)`
3. Check for terminal settings

---

## 🧪 Testing Your Shell

### Test PowerShell Directly

```powershell
# Test PowerShell Desktop
powershell.exe -NoProfile -Command "Write-Host 'Test'"

# Test PowerShell Core
pwsh.exe -NoProfile -Command "Write-Host 'Test'"

# Test CMD
cmd.exe /c echo Test

# Test Git Bash (if installed)
bash.exe --version
```

### Check Exit Codes

If you see an exit code:
1. Search online: `"PowerShell" "exit code 4294901760"`
2. Check shell's GitHub issues
3. For WSL: https://github.com/microsoft/WSL/issues

---

## 📋 Step-by-Step Troubleshooting

### Step 1: Check Settings
- [ ] Review `terminal.integrated.*` settings
- [ ] Use `@modified` filter in Settings
- [ ] Check `settings.json` for custom terminal config

### Step 2: Test Shell Outside VS Code
- [ ] Run shell directly from external terminal
- [ ] Verify shell works correctly
- [ ] Check for shell-specific errors

### Step 3: Update VS Code
- [ ] Check version: `Help > About`
- [ ] Update to latest: https://code.visualstudio.com/updates
- [ ] Update shell to latest version

### Step 4: Enable Trace Logging
1. Command Palette (Ctrl+Shift+P)
2. Run: `Developer: Set Log Level`
3. Select: `Trace`
4. Try opening terminal
5. Check Output panel → "Log (Window)" or "Log (Extension Host)"

### Step 5: Check Windows Version
- [ ] Windows 10 1903+ (build 18362+) for ConPTY
- [ ] Windows 10 1809 or below uses legacy winpty
- [ ] Consider upgrading Windows

### Step 6: Check Compatibility Mode
- [ ] VS Code Properties → Compatibility tab
- [ ] Ensure compatibility mode is **disabled**

### Step 7: Check Anti-Virus
- [ ] Identify your antivirus (check Windows Security)
- [ ] Add VS Code folder to exclusions:
  - **Cynet:** Open app → Exclusions → Add folder
  - **Windows Defender:** Exclusions → Add folder
  - **Other:** Look for Exclusions/Exceptions/Whitelist
- [ ] Check quarantine and restore files if found
- [ ] If files missing, reinstall VS Code
- [ ] Run: `.\scripts\check_vscode_terminal_files.ps1` to verify
- [ ] Report false positive to anti-virus vendor

### Step 8: Check Legacy Console
- [ ] CMD Properties → Options tab
- [ ] Ensure "Use legacy console" is **unchecked**

---

## 🔧 Advanced Troubleshooting

### Enable Trace Logging

1. **Via Command Palette:**
   - Ctrl+Shift+P
   - `Developer: Set Log Level`
   - Select `Trace`

2. **Via settings.json:**
   ```json
   {
     "log.level": "trace"
   }
   ```

3. **Check logs:**
   - View → Output
   - Select "Log (Window)" or "Log (Extension Host)"
   - Look for terminal-related errors

### Check Terminal Process Creation

The trace log shows:
- Shell executable path
- Arguments passed to shell
- Environment variables
- Working directory
- Any errors during process creation

---

## 📞 Getting Help

### If Still Having Issues

1. **Stack Overflow**
   - Tag: `visual-studio-code` + `terminal`
   - Include exit code and shell type

2. **VS Code Issue Reporter**
   - Help > Report Issue
   - Auto-fills relevant information
   - See: [Creating great terminal issues](https://github.com/microsoft/vscode/wiki/Terminal-Issues)

3. **Extension Issues**
   - If terminal launched from extension
   - Help > Report Issue
   - Set "File On" = "An Extension"

---

## ✅ Quick Checklist

Before reporting an issue, verify:

- [ ] VS Code is up to date
- [ ] Shell is up to date
- [ ] Compatibility mode is disabled
- [ ] Legacy console is disabled
- [ ] Anti-virus exclusions set
- [ ] Windows version supports ConPTY (1903+)
- [ ] Shell works outside VS Code
- [ ] Trace logging enabled and reviewed
- [ ] No custom terminal settings causing issues

---

## 🔗 Resources

- **VS Code Terminal User Guide:** https://code.visualstudio.com/docs/terminal/basics
- **VS Code Release Notes:** https://code.visualstudio.com/updates
- **Terminal Troubleshooting:** https://code.visualstudio.com/docs/terminal/troubleshooting
- **Creating Terminal Issues:** https://github.com/microsoft/vscode/wiki/Terminal-Issues
- **WSL Issues:** https://github.com/microsoft/WSL/issues

---

## 🎯 Project-Specific Notes

### PowerShell Core (pwsh) Recommended

For this project, we recommend using PowerShell Core (`pwsh`) because:
- ✅ Cross-platform (Windows, Linux, macOS)
- ✅ Better CI/CD support
- ✅ More reliable in automated environments
- ✅ Active development and updates

### VS Code Terminal Profile

Recommended `settings.json` configuration:

```json
{
  "terminal.integrated.defaultProfile.windows": "PowerShell Core",
  "terminal.integrated.profiles.windows": {
    "PowerShell Core": {
      "path": "pwsh.exe",
      "args": ["-NoProfile"]
    },
    "PowerShell": {
      "path": "powershell.exe",
      "args": ["-NoProfile"]
    }
  },
  "terminal.integrated.windowsEnableConpty": true
}
```

---

---

## 🛠️ Diagnostic Scripts

### Quick Check Script
```powershell
.\scripts\diagnose_terminal_issues.ps1
```
Comprehensive check of all terminal-related settings and configurations.

### Antivirus Exclusion Helper
```powershell
.\scripts\fix_vscode_antivirus_exclusions.ps1
```
Shows exact paths to add to antivirus exclusions.

### File Verification Script
```powershell
.\scripts\check_vscode_terminal_files.ps1
```
Verifies that all critical terminal files are present after adding exclusions.

---

**Last Updated:** 2025-12-02  
**Based on:** VS Code Official Troubleshooting Guide  
**Diagnostic Scripts:** `scripts\diagnose_terminal_issues.ps1`, `scripts\fix_vscode_antivirus_exclusions.ps1`, `scripts\check_vscode_terminal_files.ps1`

