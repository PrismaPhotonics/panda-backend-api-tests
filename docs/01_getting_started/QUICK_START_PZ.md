# PZ Integration - Quick Start Guide

## 🚀 Quick Setup (5 Minutes)

### Step 1: Clone PZ Repository

```bash
# From project root
git submodule update --init --recursive
```

⏱️ **Note**: This will take 5-15 minutes depending on connection speed (large repository).

### Step 2: Verify Installation

```bash
# Check if PZ was cloned successfully
python -c "from external.pz_integration import get_pz_integration; pz = get_pz_integration(); print(f'✅ Found {len(pz.list_microservices())} microservices')"
```

### Step 3: Run Integration Tests

```bash
pytest -m pz -v
```

---

## ⚡ Quick Commands

### Sync PZ to Latest

```bash
python scripts/sync_pz_code.py --sync
```

### Check Current Status

```bash
python scripts/sync_pz_code.py --status
```

### Use in Tests

```python
def test_example(pz_integration):
    # Get microservice path
    path = pz_integration.get_microservice_path('focus_server')
    
    # List services
    services = pz_integration.list_microservices()
    
    # Get version
    version = pz_integration.get_version_info()
```

---

## 🆘 Troubleshooting

### Clone Stuck or Failed

```bash
# Cancel current operation (Ctrl+C)
# Remove partial clone
Remove-Item -Recurse -Force external/pz

# Try again
git submodule update --init --recursive
```

### Authentication Issues

```bash
# Use Git credential manager
git config --global credential.helper manager

# Test access
git ls-remote https://bitbucket.org/prismaphotonics/pz.git
```

### Import Errors

```python
# Ensure PZ is in Python path
import sys
print([p for p in sys.path if 'pz' in p.lower()])
```

---

## 📖 Full Documentation

See [PZ_INTEGRATION_GUIDE.md](PZ_INTEGRATION_GUIDE.md) for complete documentation.

