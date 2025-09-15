## Focus Server – Load & Stress Testing (Locust)

Base URL: `http://localhost:8500` (after Kubernetes port-forward)

Endpoints covered:
- GET `/channels`
- GET `/live_metadata`
- POST `/configure` + GET `/metadata/{job_id}` (polling)
- POST `/recordings_in_time_range`
- GET `/get_recordings_timeline` (HTML)

### Installation
```
pip install -r requirements.txt
```

### Smoke run
```
locust -f load/focus_locustfile.py --headless -u 10 -r 5 -t 5m --host http://localhost:8500
```

### Ramp → Steady → Spike → Soak profile
```
set TARGET_USERS=100 & set SPIKE_USERS=200 & set SOAK_USERS=60 & ^
set RAMP_MINUTES=3 & set STEADY_MINUTES=7 & set SPIKE_MINUTES=2 & set SOAK_MINUTES=10 & ^
locust -f load/focus_locustfile.py --headless --run-time 25m --host http://localhost:8500
```

### Useful environment variables
- `START_EPOCH`, `END_EPOCH` – known historical window (otherwise discovered via `/recordings_in_time_range`).
- `LIVE_MODE=true` – run `/configure` with start/end = null.
- `CHANNEL_MIN`, `CHANNEL_MAX`, `VIEW_TYPE`, `NFFT_SELECTION`, `DISPLAY_HEIGHT`, `FREQ_MIN`, `FREQ_MAX`, `DISPLAY_TIME_AXIS_DURATION` – configuration parameters.
- `METADATA_POLL_INTERVAL`, `METADATA_POLL_TIMEOUT` – polling for `
metadata/{job_id}`.

### Reports
- Locust CLI reports. Add `--csv results/focus --html results/focus_report.html` to persist.

### Safety
- No TLS/auth over port-forward. Do not run against production.
- Avoid creating hundreds of `/configure` jobs at once – start low and ramp gradually.

