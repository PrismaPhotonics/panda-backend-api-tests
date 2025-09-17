# Panda Backend API Tests
## CI Usage (Focus API)

### Secrets / Env
Define the following in GitHub → Settings → Secrets and variables → Actions:
- `FOCUS_BASE_URL` (e.g., `https://10.10.10.150:30443`)
- `FOCUS_API_PREFIX` (e.g., `/focus-server` or `/prisma/api/focus-server`)
- `VERIFY_SSL` (`false` for self-signed certs; `true` otherwise)
- Optional: `REQUIRE_SERVER` (`true|false`) to enforce preflight during push/PR

### Workflows
Two workflows use a shared composite action:
- `.github/workflows/focus-contract-tests.yml`
- `.github/workflows/ci.yml`

Both leverage `.github/actions/focus-preflight-run/action.yml` which performs:
1. Preflight with retries (curl to `$BASE/channels`)
2. Diagnostic `curl -vk` when unreachable
3. Optional pytest run with JUnit output

### Self-Hosted Runner (internal networks)
If the Focus server is internal-only, register a self-hosted runner (label example: `focus-ci`) and update `runs-on` accordingly. Set `REQUIRE_SERVER=true` to fail-fast when unavailable.


