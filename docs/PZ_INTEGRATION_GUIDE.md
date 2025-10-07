# PZ Development Repository Integration Guide

## 📋 Overview

This document describes the integration between the Focus Server Automation Framework and the PrismaPhotonics PZ development repository. This integration enables automated tests to run against the **latest production code** from the development team.

---

## 🎯 Purpose

The integration serves several critical purposes:

1. **Always Test Latest Code**: Ensure tests run against the most current version of PZ services
2. **Code Reusability**: Import and use production code directly in tests
3. **Version Synchronization**: Keep test framework synchronized with development
4. **Seamless Access**: Transparent access to all PZ microservices

---

## 🏗️ Architecture

### Directory Structure

```
focus_server_automation/
├── external/
│   ├── __init__.py
│   ├── pz_integration.py          # Main integration module
│   └── pz/                         # PZ repository (Git submodule)
│       └── microservices/
│           ├── focus_server/
│           ├── analyzer/
│           ├── data_manager/
│           ├── pzpy/
│           └── ... (40+ microservices)
├── scripts/
│   └── sync_pz_code.py            # PZ sync utility
├── tests/
│   ├── conftest.py                # Auto-loads PZ integration
│   └── integration/
│       └── infrastructure/
│           └── test_pz_integration.py
└── docs/
    └── PZ_INTEGRATION_GUIDE.md    # This file
```

### Components

1. **Git Submodule**: PZ repository linked as `external/pz`
2. **Integration Module**: `external/pz_integration.py` - provides access layer
3. **Sync Script**: `scripts/sync_pz_code.py` - updates PZ to latest
4. **Pytest Integration**: Automatic PYTHONPATH configuration in `conftest.py`

---

## 🚀 Setup

### Initial Setup

#### 1. Clone PZ Repository as Submodule

```bash
# Initialize the submodule
git submodule update --init --recursive

# This will clone the entire PZ repository into external/pz/
```

#### 2. Verify Installation

```bash
# Run PZ integration tests
pytest tests/integration/infrastructure/test_pz_integration.py -v

# Or check status directly
python scripts/sync_pz_code.py --status
```

#### 3. Configure Git (if needed)

If you have authentication issues with Bitbucket:

```bash
# Ensure Git is configured for Bitbucket
git config --global credential.helper manager

# Or use SSH keys
git config --global url."git@bitbucket.org:".insteadOf "https://bitbucket.org/"
```

---

## 📖 Usage

### Using PZ Code in Tests

#### Method 1: Using the Integration Module

```python
from external.pz_integration import get_pz_integration

def test_using_pz_code(pz_integration):
    """Example test using PZ integration."""
    
    # Get path to a specific microservice
    focus_server_path = pz_integration.get_microservice_path('focus_server')
    
    # List all available microservices
    services = pz_integration.list_microservices()
    print(f"Available services: {services}")
    
    # Import a module from PZ
    # pz_module = pz_integration.import_module('pzpy.some_module')
```

#### Method 2: Direct Import (after PYTHONPATH setup)

```python
# PYTHONPATH is automatically configured by conftest.py
# You can import PZ modules directly:

def test_direct_import():
    """Example with direct import."""
    try:
        # Import from PZ microservices
        # from focus_server.app import some_function
        # result = some_function()
        pass
    except ImportError as e:
        pytest.skip(f"PZ module not available: {e}")
```

#### Method 3: Using the Pytest Fixture

```python
@pytest.mark.pz
def test_with_fixture(pz_integration):
    """Test using pz_integration fixture."""
    
    # Get version info
    version = pz_integration.get_version_info()
    print(f"Testing against PZ commit: {version['commit']}")
    
    # Get microservice path
    service_path = pz_integration.get_microservice_path('analyzer')
    assert service_path.exists()
```

---

## 🔄 Synchronization

### Keeping PZ Up-to-Date

#### Manual Sync

```bash
# Sync to latest master
python scripts/sync_pz_code.py --sync

# Sync to specific branch
python scripts/sync_pz_code.py --sync --branch develop

# Check current status
python scripts/sync_pz_code.py --status

# Verbose output
python scripts/sync_pz_code.py --sync --verbose
```

#### Programmatic Sync

```python
from external.pz_integration import sync_pz

# Sync in test setup
def test_setup():
    success = sync_pz()
    assert success, "Failed to sync PZ repository"
```

#### Automatic Sync (CI/CD)

```yaml
# Example GitHub Actions workflow
- name: Sync PZ Repository
  run: |
    git submodule update --init --recursive
    python scripts/sync_pz_code.py --sync --verbose
```

---

## 🧪 Testing

### Running PZ Integration Tests

```bash
# Run all PZ integration tests
pytest -m pz -v

# Run with detailed output
pytest tests/integration/infrastructure/test_pz_integration.py -v -s

# Run specific test
pytest tests/integration/infrastructure/test_pz_integration.py::test_pz_repository_available -v
```

### Available Test Markers

```python
@pytest.mark.pz              # PZ integration tests
@pytest.mark.infrastructure  # Infrastructure tests
@pytest.mark.integration     # Integration tests
```

---

## 📊 Version Information

### Checking PZ Version

```python
from external.pz_integration import get_pz_integration

pz = get_pz_integration()
version_info = pz.get_version_info()

print(f"Commit: {version_info['commit']}")
print(f"Branch: {version_info['branch']}")
print(f"Last Update: {version_info['last_update']}")
```

### Command Line Version Check

```bash
python -c "from external.pz_integration import *; pz = PZIntegration(); print(pz.get_version_info())"
```

---

## 🔍 Available Microservices

The PZ repository contains 40+ microservices. Key services include:

### Core Services
- **focus_server** - Main Focus Server service
- **analyzer** - Data analysis service
- **data_manager** - Data management service
- **controller** - System controller

### Support Services
- **pzpy** - Core Python library
- **pz_core_libs** - Core libraries
- **logger** - Logging service
- **storage_manager** - Storage management

### Specialized Services
- **baby_analyzer** - Specialized analyzer
- **bbox_generation** - Bounding box generation
- **fiber_inspector** - Fiber inspection
- **otdr_report** - OTDR reporting
- **pzwaterfall** - Waterfall visualization

### Access Services

```python
from external.pz_integration import list_microservices, get_microservice_path

# List all services
services = list_microservices()
print(f"Total microservices: {len(services)}")

# Get specific service path
focus_path = get_microservice_path('focus_server')
```

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. Submodule Not Initialized

**Error**: `PZ repository not found`

**Solution**:
```bash
git submodule update --init --recursive
```

#### 2. Authentication Issues

**Error**: `fatal: could not read Username for 'https://bitbucket.org'`

**Solution**: Configure Git credentials or use SSH
```bash
# Store credentials
git config --global credential.helper manager

# Or switch to SSH
git remote set-url origin git@bitbucket.org:prismaphotonics/pz.git
```

#### 3. Import Errors

**Error**: `ModuleNotFoundError: No module named 'some_pz_module'`

**Solution**: Ensure PYTHONPATH is configured
```python
# In test file
import sys
print(sys.path)  # Check if PZ paths are present
```

#### 4. Stale Code

**Error**: Tests failing against old PZ code

**Solution**: Sync to latest
```bash
python scripts/sync_pz_code.py --sync
```

---

## 🔐 Security Considerations

1. **Credentials**: Never commit Bitbucket credentials
2. **Submodule**: PZ repository may contain sensitive code
3. **Access Control**: Ensure only authorized team members have access
4. **CI/CD**: Use secure credential management in pipelines

---

## 📈 Best Practices

### 1. Regular Synchronization

```bash
# Before running critical tests
python scripts/sync_pz_code.py --sync
pytest -m critical
```

### 2. Version Tracking

```python
# Log PZ version in test reports
def test_with_version_tracking(pz_integration):
    version = pz_integration.get_version_info()
    logger.info(f"Testing against PZ: {version['commit']} ({version['branch']})")
    # ... rest of test
```

### 3. Graceful Degradation

```python
# Handle missing PZ gracefully
try:
    from external.pz_integration import get_pz_integration
    pz = get_pz_integration()
except FileNotFoundError:
    pytest.skip("PZ repository not available")
```

### 4. CI/CD Integration

```yaml
# Always sync before test runs
before_script:
  - git submodule update --init --recursive
  - python scripts/sync_pz_code.py --sync --branch master
```

---

## 🔗 References

- **PZ Repository**: https://bitbucket.org/prismaphotonics/pz
- **Git Submodules**: https://git-scm.com/book/en/v2/Git-Tools-Submodules
- **Project README**: [../README.md](../README.md)

---

## 📞 Support

For issues related to:
- **PZ Integration**: Contact QA Automation team
- **PZ Repository**: Contact PrismaPhotonics development team
- **Access Issues**: Contact DevOps/IT team

---

**Last Updated**: October 2025  
**Author**: QA Automation Architect  
**Version**: 1.0.0

