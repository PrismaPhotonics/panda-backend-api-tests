# Focus Server – Load & Stress Testing (Locust)

This README consolidates load-testing guidance into a single canonical document in English for Focus Server.

## Requirements
- Python 3.10+
- Install dependencies:
```bash
pip install -r requirements.txt
```
- Connectivity to Focus Server:
  - Kubernetes port-forward:
    ```bash
    kubectl -n default port-forward svc/focus-server-service 8500:5000
    ```
  - Base URL: `http://localhost:8500`

## Endpoints covered
- GET `/channels`
- GET `/live_metadata`
- POST `/configure` + GET `/metadata/{job_id}` (polling)
- POST `/recordings_in_time_range`
- GET `/get_recordings_timeline` (HTML)

## Useful environment variables
- `VERIFY_TLS=false`  # port-forward is HTTP
- `AUTH_TOKEN=<token-if-needed>`
- `START_EPOCH`, `END_EPOCH` – known historical window (otherwise discovered via `/recordings_in_time_range`).
- `LIVE_MODE=false` – when true, `start_time`/`end_time` = null.
- `CHANNEL_MIN=1`, `CHANNEL_MAX=750`, `VIEW_TYPE=0`, `NFFT_SELECTION=2048`
- `FREQ_MIN=0`, `FREQ_MAX=300`, `DISPLAY_HEIGHT=200`, `DISPLAY_TIME_AXIS_DURATION=60`
- Load shape parameters:
  - `RAMP_MINUTES=3` `STEADY_MINUTES=7` `SPIKE_MINUTES=2` `SOAK_MINUTES=10`
  - `TARGET_USERS=100` `SOAK_USERS=60` `SPIKE_USERS=200` `SPAWN_RATE=20`

## Basic run (headless)
```bash
locust -f locust_focus_server.py --host http://localhost:8500
```

## Profile: Ramp → Steady → Spike → Soak
Windows CMD:
```cmd
set TARGET_USERS=100 & set SPIKE_USERS=200 & set SOAK_USERS=60 & ^
set RAMP_MINUTES=3 & set STEADY_MINUTES=7 & set SPIKE_MINUTES=2 & set SOAK_MINUTES=10 & ^
locust -f locust_focus_server.py --headless --run-time 25m --host http://localhost:8500
```

Bash (Linux/macOS):
```bash
export TARGET_USERS=100 SPIKE_USERS=200 SOAK_USERS=60 \
       RAMP_MINUTES=3 STEADY_MINUTES=7 SPIKE_MINUTES=2 SOAK_MINUTES=10
locust -f locust_focus_server.py --headless --run-time 25m --host http://localhost:8500
```

## Reports
- Locust prints CLI reports during execution.
- To persist reports, add flags:
  - `--csv results/focus`
  - `--html results/focus_report.html`

## Safety notes
- Port-forward typically runs over HTTP without TLS/auth; do not run against production.
- Avoid creating hundreds of `/configure` jobs at once — start small and ramp gradually.
