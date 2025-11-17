# Test Logs Directory

**Automatic Test Logging System**

This directory contains all test execution logs, automatically generated with timestamps and test type information.

---

## 📂 Directory Structure

```
logs/
├── test_runs/          # Current test run logs (ALL levels)
│   └── YYYY-MM-DD_HH-MM-SS_<test_type>.log
├── errors/             # Error logs only (ERROR and CRITICAL)
│   └── YYYY-MM-DD_HH-MM-SS_<test_type>_ERRORS.log
├── warnings/           # Warning logs only (WARNING and above)
│   └── YYYY-MM-DD_HH-MM-SS_<test_type>_WARNINGS.log
├── archive/            # Archived old logs
│   └── older logs moved here
└── README.md           # This file
```

---

## 📝 Log File Naming Convention

**Three log files** are automatically created for each test run:

### Main Log (all levels)
```
test_runs/YYYY-MM-DD_HH-MM-SS_<test_type>.log
```

### Errors Log (ERROR and CRITICAL only)
```
errors/YYYY-MM-DD_HH-MM-SS_<test_type>_ERRORS.log
```

### Warnings Log (WARNING and above)
```
warnings/YYYY-MM-DD_HH-MM-SS_<test_type>_WARNINGS.log
```

**Examples:**
- `test_runs/2025-10-23_15-30-45_integration_tests.log` (all logs)
- `errors/2025-10-23_15-30-45_integration_tests_ERRORS.log` (errors only)
- `warnings/2025-10-23_15-30-45_integration_tests_WARNINGS.log` (warnings only)

### Test Type Detection

The system automatically detects the test type from:

1. **Test markers** (e.g., `-m critical` → `marker_critical`)
2. **Test path** (e.g., `tests/integration/` → `integration_tests`)
3. **Specific directories:**
   - `unit` → `unit_tests`
   - `integration` → `integration_tests`
   - `infrastructure` → `infrastructure_tests`
   - `api` → `api_tests`
   - `performance` → `performance_tests`

---

## 🚀 Usage

### Automatic Logging (Default)

Just run pytest normally - **3 log files** are automatically created:

```bash
# Run all tests - creates 3 files:
pytest
# → test_runs/YYYY-MM-DD_HH-MM-SS_all_tests.log
# → errors/YYYY-MM-DD_HH-MM-SS_all_tests_ERRORS.log
# → warnings/YYYY-MM-DD_HH-MM-SS_all_tests_WARNINGS.log

# Run integration tests - creates 3 files:
pytest tests/integration/
# → test_runs/YYYY-MM-DD_HH-MM-SS_integration_tests.log
# → errors/YYYY-MM-DD_HH-MM-SS_integration_tests_ERRORS.log
# → warnings/YYYY-MM-DD_HH-MM-SS_integration_tests_WARNINGS.log
```

### Log Content

Each log file contains:

```
2025-10-23 15:30:45 [    INFO] root: ================================================================================
2025-10-23 15:30:45 [    INFO] root: TEST SESSION STARTED: integration_tests
2025-10-23 15:30:45 [    INFO] root: Log file: logs/test_runs/2025-10-23_15-30-45_integration_tests.log
2025-10-23 15:30:45 [    INFO] root: Environment: new_production
2025-10-23 15:30:45 [    INFO] root: ================================================================================
2025-10-23 15:30:45 [    INFO] conftest: Setting up test: test_something
... test execution logs ...
2025-10-23 15:31:20 [    INFO] root: ✅ tests/integration/test_something.py::test_something - PASSED
... more test results ...
2025-10-23 15:32:00 [    INFO] root: ================================================================================
2025-10-23 15:32:00 [    INFO] root: TEST SESSION COMPLETED
2025-10-23 15:32:00 [    INFO] root: Log saved to: logs/test_runs/2025-10-23_15-30-45_integration_tests.log
2025-10-23 15:32:00 [    INFO] root: ================================================================================
```

### Finding Logs

After test execution, you'll see all 3 log file locations:

```
✅ Test logs saved:
   📝 All logs: logs\test_runs\2025-10-23_15-30-45_integration_tests.log
   ⚠️  Warnings: logs\warnings\2025-10-23_15-30-45_integration_tests_WARNINGS.log
   ❌ Errors: logs\errors\2025-10-23_15-30-45_integration_tests_ERRORS.log
```

---

## 🗂️ Log Management

### Viewing Recent Logs

```bash
# List all logs (newest first)
ls -lt logs/test_runs/

# View latest log
cat logs/test_runs/$(ls -t logs/test_runs/ | head -1)

# Search for specific test in logs
grep "test_something" logs/test_runs/*.log
```

### PowerShell (Windows)

```powershell
# List all logs (newest first)
Get-ChildItem logs\test_runs\ | Sort-Object LastWriteTime -Descending

# View latest log
Get-Content (Get-ChildItem logs\test_runs\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName

# Search for specific test
Select-String "test_something" logs\test_runs\*.log
```

### Archiving Old Logs

To keep the `test_runs` directory clean, move old logs to `archive`:

```bash
# Move logs older than 7 days to archive
find logs/test_runs/ -name "*.log" -mtime +7 -exec mv {} logs/archive/ \;
```

PowerShell:
```powershell
# Move logs older than 7 days to archive
Get-ChildItem logs\test_runs\*.log | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} | Move-Item -Destination logs\archive\
```

---

## 🔧 Configuration

### Disable Logging (if needed)

To run tests without file logging:

```bash
pytest --dry-run
```

### Change Log Level

Edit `pytest.ini`:

```ini
log_file_level = DEBUG  # Change to INFO, WARNING, ERROR
```

---

## 📊 Log Analysis

### Common Queries

**Find all errors (quick!):**
```powershell
# Just check the errors directory
Get-Content logs\errors\*.log
```

**Find all warnings (quick!):**
```powershell
# Just check the warnings directory
Get-Content logs\warnings\*.log
```

**Find all failed tests:**
```bash
grep "❌.*FAILED" logs/test_runs/*.log
```

**Find tests by name:**
```bash
grep "test_mongodb" logs/test_runs/*.log
```

**Find by date:**
```bash
ls logs/test_runs/2025-10-23*.log
ls logs/errors/2025-10-23*.log
ls logs/warnings/2025-10-23*.log
```

---

## 🎯 Best Practices

1. **Check errors first** - Start with `logs/errors/` directory for quick error detection
2. **Review warnings** - Check `logs/warnings/` for potential issues
3. **Use appropriate log file** - Don't search all logs when you only need errors
4. **Archive old logs** - Move old logs from all 3 directories to archive
5. **Share relevant logs** - Send specific error/warning logs for debugging
6. **Monitor error trends** - Track if error files are getting larger over time

---

## 📝 Notes

- **3 log files** created automatically for every test run
- **Separate error/warning logs** - easier debugging and monitoring
- **UTF-8 encoding** - supports all characters including Hebrew
- **Timestamped filenames** - easy to find specific test runs
- **Separate logs per session** - one set of logs per pytest execution
- **Console + file** - logs appear both in console and file
- **Empty error logs** - if no errors occurred, error file will be empty (0 bytes) ✅

---

**Last Updated:** October 23, 2025  
**Plugin:** `tests/pytest_logging_plugin.py`  
**Configuration:** `pytest.ini` + `tests/conftest.py`

