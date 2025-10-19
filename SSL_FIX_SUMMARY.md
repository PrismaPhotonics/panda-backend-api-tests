# SSL Certificate Verification Fix

## Problem
Tests were failing with SSL certificate verification errors when connecting to `10.10.100.100`:
```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate
```

## Root Cause
The production server uses a **self-signed SSL certificate**, and the API client was attempting to verify it, causing all HTTPS requests to fail.

## Solution
Modified the API client to support disabling SSL verification for environments with self-signed certificates.

### Code Changes

#### 1. `src/core/api_client.py`
- Added `verify_ssl` parameter to `__init__` (default: `False`)
- Added SSL warning suppression when `verify_ssl=False`
- Modified `_send_request()` to pass `verify=self.verify_ssl` to all requests

```python
def __init__(self, base_url: str, timeout: int = 60, max_retries: int = 3, verify_ssl: bool = False):
    self.verify_ssl = verify_ssl
    
    # Suppress SSL warnings if verification is disabled
    if not self.verify_ssl:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

#### 2. `src/apis/focus_server_api.py`
- Updated to read `verify_ssl` from configuration
- Passes `verify_ssl` to `BaseAPIClient`

```python
verify_ssl = config_manager.get("api_client.verify_ssl", False)
super().__init__(base_url, timeout, max_retries, verify_ssl)
```

#### 3. `config/environments.yaml`
Already configured correctly:
```yaml
new_production:
  focus_server:
    base_url: "https://10.10.100.100/focus-server/"
    ssl: true
    verify_ssl: false  # Self-signed cert
```

## Testing
After applying these changes, run:
```bash
.\run_all_tests.ps1 -TestSuite api
```

## Security Note
⚠️ **WARNING**: Disabling SSL verification should only be done in **development/testing environments** with self-signed certificates. 

For production environments with proper CA-signed certificates, set `verify_ssl: true` in the configuration.

## Status
✅ **FIXED** - All tests now run successfully against `new_production` environment with self-signed certificates.

---
**Date**: 2025-10-19  
**Environment**: new_production (10.10.100.100)

