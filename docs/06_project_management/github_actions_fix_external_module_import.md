# GitHub Actions Fix: External Module Import Error

## Issue Summary

**Date:** November 23, 2025  
**Workflow Affected:** Load and Performance Tests (#15)  
**Error:** `PZ integration failed: No module named 'external'`

## Root Cause

The GitHub Actions workflows were installing all required Python dependencies via `scripts/install_dependencies.ps1`, but they were **not installing the project itself** in editable mode. This caused the following problems:

1. The `external` module (located at `external/`) was not importable
2. The `src` module was not importable
3. Any script that tried to import these modules would fail with `ModuleNotFoundError`

## The Problem

When the workflow ran the health check (which includes PZ integration verification), it tried to:
```python
import external
```

But since the project wasn't installed as a package, Python couldn't find the `external` module in its path, even though the files existed in the repository.

## The Solution

Added a new step to all GitHub Actions workflows to install the project in **editable mode** after installing dependencies:

```yaml
- name: Install project in editable mode
  shell: powershell
  run: |
    Write-Host "Installing project in editable mode..."
    pip install -e .
    if ($LASTEXITCODE -ne 0) {
      Write-Host "::error::Failed to install project in editable mode"
      exit 1
    }
    Write-Host "Project installed successfully"
```

This command (`pip install -e .`) reads the `setup.py` file and installs the project in development/editable mode, which:
- Makes all project modules (`external`, `src`, etc.) importable
- Allows changes to the code without reinstalling
- Properly sets up the Python package structure

## Files Modified

1. `.github/workflows/load-performance.yml`
2. `.github/workflows/regression-tests.yml`
3. `.github/workflows/smoke-tests.yml`

## Testing

To verify this fix works, you can:

1. Manually trigger the "Load and Performance Tests" workflow
2. Check that the new "Install project in editable mode" step completes successfully
3. Verify that the health check passes without the `No module named 'external'` error

## Expected Result

After this fix, the workflows should:
- ✅ Successfully install all dependencies
- ✅ Install the project in editable mode
- ✅ Successfully import `external` and `src` modules
- ✅ Pass the PZ integration health check
- ✅ Run the actual tests without import errors

## Why This Wasn't Caught Earlier

This issue likely went unnoticed because:
1. Local development environments often have the project installed via `pip install -e .` or similar
2. The error only manifests in fresh CI/CD environments
3. The workflows were recently restructured with the health check that uses PZ integration

## Best Practices

Going forward, all CI/CD workflows should:
1. Install dependencies first
2. Install the project in editable mode (`pip install -e .`)
3. Then run any scripts or tests that import project modules

This is standard practice for Python projects and ensures consistency between local development and CI/CD environments.

