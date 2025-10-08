# External Dependencies

## PZ Development Repository - Git Submodule Integration

This directory contains the PrismaPhotonics PZ development repository integrated as a **Git Submodule**. This ensures you always have access to the latest production code from the PZ development team.

### 🎯 Quick Setup

#### Initial Clone (New Repository)

If you're cloning this repository for the first time:

```bash
# Clone with submodules
git clone --recurse-submodules <repository-url>

# Or if already cloned without submodules:
git submodule update --init --recursive
```

#### PowerShell Script (Windows)

```powershell
# Update to latest PZ code
.\scripts\update_pz_submodule.ps1

# Show current status
.\scripts\update_pz_submodule.ps1 -Status

# Sync to specific branch
.\scripts\update_pz_submodule.ps1 -Branch develop
```

#### Bash Script (Linux/macOS)

```bash
# Update to latest PZ code
./scripts/update_pz_submodule.sh

# Show current status
./scripts/update_pz_submodule.sh --status

# Sync to specific branch
./scripts/update_pz_submodule.sh --branch develop
```

#### Python Script (Cross-platform)

```bash
# Sync to latest
python scripts/sync_pz_code.py --sync

# Show status
python scripts/sync_pz_code.py --status

# Sync specific branch
python scripts/sync_pz_code.py --sync --branch develop
```

### 📁 Directory Structure

```
external/
├── __init__.py              # Package initialization
├── pz_integration.py        # PZ integration wrapper module
├── pz/                      # PZ Git Submodule (tracked by Git)
│   ├── .git                # Submodule Git metadata
│   └── microservices/      # 40+ microservices
│       ├── focus_server/
│       ├── analyzer/
│       └── ...
└── README.md               # This file
```

### 🔧 Usage in Code

#### Basic Import

```python
# Automatic integration via conftest.py
from external.pz_integration import get_pz_integration

# Get PZ integration instance
pz = get_pz_integration()

# List available microservices
print(pz.list_microservices())

# Get path to specific microservice
focus_server_path = pz.get_microservice_path('focus_server')

# Import PZ modules
module = pz.import_module('focus_server.api.endpoints')
```

#### Using Pytest Fixture

```python
@pytest.mark.pz
def test_with_pz_integration(pz_integration):
    """Test that uses PZ development code."""
    # PZ integration is already set up
    microservices = pz_integration.list_microservices()
    assert len(microservices) > 0
```

### 🔄 Keeping PZ Code Updated

The PZ submodule points to the latest commit from the remote repository. To stay synchronized:

#### Automatic Updates (Recommended)

Add to your CI/CD pipeline or pre-test script:

```bash
# Update PZ before running tests
git submodule update --remote --merge external/pz
```

#### Manual Updates

```bash
# Method 1: Using helper scripts
python scripts/sync_pz_code.py --sync

# Method 2: Manual Git commands
cd external/pz
git fetch origin
git pull origin master
cd ../..
```

### ⚙️ Git Submodule Commands

```bash
# Initialize submodule (first time)
git submodule update --init --recursive

# Update to latest remote commit
git submodule update --remote --merge external/pz

# Show submodule status
git submodule status

# Sync submodule URL (if changed)
git submodule sync

# Update and checkout specific branch
cd external/pz
git checkout master
git pull origin master
cd ../..
```

### 📊 Submodule Information

```bash
# Show current commit and branch
cd external/pz && git log -1 --oneline && git branch

# Show version info using Python
python -c "from external.pz_integration import get_pz_integration; print(get_pz_integration().get_version_info())"
```

### ⚠️ Important Notes

1. **Git Submodule** - The `pz/` directory is now **tracked as a Git Submodule**, not ignored
2. **Automatic PYTHONPATH** - PZ code is automatically added to Python path in `conftest.py`
3. **No Manual Cloning** - Don't manually clone PZ; use `git submodule` commands
4. **Commit Reference** - The parent repo tracks a specific commit hash of PZ
5. **Update Regularly** - Run update scripts before tests to get latest code

### 🐛 Troubleshooting

#### Submodule Not Initialized

```bash
git submodule update --init --recursive
```

#### Submodule Shows Modified Files

```bash
cd external/pz
git status
git restore .  # Discard local changes
cd ../..
```

#### Detached HEAD State

```bash
cd external/pz
git checkout master
git pull origin master
cd ../..
```

#### Permission Denied (Bitbucket)

Make sure you have access to the PZ repository and your SSH keys are configured:

```bash
ssh -T git@bitbucket.org
```

### 📚 Additional Resources

- [Git Submodules Documentation](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [PZ Integration Guide](../docs/PZ_INTEGRATION_GUIDE.md)
- [Bitbucket PZ Repository](https://bitbucket.org/prismaphotonics/pz/src/master/)

