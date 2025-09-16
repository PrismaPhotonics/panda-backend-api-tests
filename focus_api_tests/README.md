# Focus API Tests

## Install
```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

## Configuration
- FOCUS_BASE_URL: Base URL of the Focus server (scheme + host + port). Default: `http://localhost:8500`
- FOCUS_API_PREFIX: API path prefix. Default: `/focus-server`. Example alternative: `/prisma/api`
- VERIFY_SSL: Set to `true` to verify server TLS certificate. Default: `false` (useful for self-signed certs)

## Run
```bash
# Linux/macOS (bash):
export FOCUS_BASE_URL="https://<host>:<port>"
export FOCUS_API_PREFIX="/focus-server"   # or "/prisma/api"
export VERIFY_SSL=false
pytest -q focus_api_tests/

# Windows (PowerShell):
$env:FOCUS_BASE_URL="https://<host>:<port>"; $env:FOCUS_API_PREFIX="/focus-server"; $env:VERIFY_SSL="false"; pytest -q focus_api_tests/
```

## Example for your environment
```bash
# Based on the provided Postman environment
$env:FOCUS_BASE_URL="https://10.10.10.150:30443"; $env:FOCUS_API_PREFIX="/prisma/api"; $env:VERIFY_SSL="false"; pytest -q focus_api_tests/
```
