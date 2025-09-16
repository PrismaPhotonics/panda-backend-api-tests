Perfect 👍 Here’s your README in **clean, professional English (Left-to-Right)** formatted for GitHub:

````markdown
# Locust Load & Stress Testing

This repository provides **Locust-based load and stress test harnesses** for:

- **Prisma Web APIs** (safe, non-destructive GET scenarios)  
- **Focus Server API** (functional and lifecycle flows such as configured and poll)  

Both harnesses support **headless execution** for CI/CD pipelines and an optional **Web UI** for local exploration.

---

## 1. Prisma Web APIs — Safe Load Testing

### Scope & Safety
- Base URL: `https://10.10.10.150:30443`  
- Site: `prisma-210-1000`  
- Only **safe GET calls** (non-destructive).  
- Authentication may be required for initial setup.  
- Begin with **low RPS** and ramp up gradually (with approval).

### Prerequisites
- Python 3.12+  
- Network access to target environment  
- For TLS with self-signed certificates:
— Configure OS trust,  
  - Or set `REQUESTS_CA_BUNDLE`,  
  - Or disable verification in client code (only for non-production).

### Installation
```bash
pip install -r requirements.txt
````

### Run — Headless

```bash
locust -f load/locustfile.py --headless \
  --host https://10.10.10.150:30443 \
  -u 25 -r 5 -t 10m
```

### Run — Web UI

```bash
locust -f load/locustfile.py --host https://10.10.10.150:30443
```

Then open [http://localhost:8089](http://localhost:8089) and configure:

* Users (concurrent)
* Spawn rate (users/sec)
* Test duration

### Task Mix (Weights)

* `alerts_live`: 5
* `map_geochannel`: 3
* `map_reportline`: 3
* `geofence_live`: 2
* `region_with_general`: 2
* `point_map_setup`: 2
* `feature_flags`: 1
* `system_status`: 1
* `live_metadata`: 1
* `map_tiles_sample`: 1

---

## 2. Focus Server — Load & Stress Testing

### Base URL

* After port-forward: `http://localhost:8500`

### Endpoints

* `GET /channels`
* `GET /live_metadata`
* `POST /configure` + `GET /metadata/{job_id}` (polling)
* `POST /recordings_in_time_range`
* `GET /get_recordings_timeline` (HTML)

### Prerequisites

* Python 3.8+
* Focus Server reachable via base URL (`kubectl port-forward` or local run).

### Installation

```bash
pip install -r requirements.txt
```

### Run — Smoke Test

```bash
locust -f load/focus_locustfile.py --headless \
  -u 10 -r 5 -t 5m \
  --host http://localhost:8500
```

### Run — Profile: Ramp → Steady → Spike → Soak

**Windows (cmd):**

```bat
set TARGET_USERS=100 ^
set SPIKE_USERS=200 ^
set SOAK_USERS=60 ^
set RAMP_MINUTES=3 ^
set STEADY_MINUTES=7 ^
set SPIKE_MINUTES=2 ^
set SOAK_MINUTES=10 ^
locust -f load/focus_locustfile.py --headless --run-time 25m --host http://localhost:8500
```

**Linux/macOS (bash):**

```bash
export TARGET_USERS=100 SPIKE_USERS=200 SOAK_USERS=60
export RAMP_MINUTES=3 STEADY_MINUTES=7 SPIKE_MINUTES=2 SOAK_MINUTES=10
locust -f load/focus_locustfile.py --headless --run-time 25m --host http://localhost:8500
```

### Useful Environment Variables

* `START_EPOCH`, `END_EPOCH` — historical window (otherwise discovered via `/recordings_in_time_range`).
* `LIVE_MODE=true` — run `/configure` with `start_time`/`end_time=null`.
* Config parameters for `/configure`:
  `CHANNEL_MIN`, `CHANNEL_MAX`, `VIEW_TYPE`, `NFFT_SELECTION`, `DISPLAY_HEIGHT`, `FREQ_MIN`, `FREQ_MAX`, `DISPLAY_TIME_AXIS_DURATION`
* Polling behavior:
  `METADATA_POLL_INTERVAL`, `METADATA_POLL_TIMEOUT`

### Artifacts & Reporting

```bash
locust ... --csv results/focus --html results/focus_report.html
```

Generates CSV time series and HTML report.

### Safety & Best Practices

* Avoid production runs without proper auth/TLS.
* Do **not** create hundreds of `/configure` jobs simultaneously.
* Ramp up gradually.
* Monitor `429/5xx` rates and latency (`p95/p99`). Stop if persistent.

---

## 3. Troubleshooting

* **100% failures with \~30s durations** → likely connection timeout.
  Test manually:

  ```bash
  curl -v http://localhost:8500/channels
  ```

* **Wrong content type** (HTML instead of JSON, etc.):
  → Verify endpoint correctness and task configs.

* **Env vars aren't applied**:
  → Validate with `printenv` (Linux/macOS) or `set` (Windows).

---

## License & Responsible Use

* Use only in approved environments.
* Follow organizational guidelines for performance testing, security, and data privacy.
* Never run destructive tests without explicit authorization.

```

---

רוצה שאבנה גם גרסה **מקוצרת (one-page quickstart)** במקביל ל־README המלא הזה?
```
