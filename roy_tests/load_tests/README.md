# Focus Server – Load Testing (Locust)

## Requirements

* Python **3.10+**
* Install dependencies:

  ```bash
  pip install -r requirements.txt
  ```
* Service connection:

  * In-cluster:

    ```bash
    kubectl -n default port-forward svc/focus-server-service 8500:5000
    ```
  * Base URL: `http://localhost:8500`

## Optional Environment Variables

* `VERIFY_TLS=false`  → port-forward uses HTTP
* `AUTH_TOKEN=<token-if-needed>`
* `START_EPOCH=1757752339` `END_EPOCH=1757773293` → known window with data
* `CHANNEL_MIN=1` `CHANNEL_MAX=750` `VIEW_TYPE=0` `NFFT_SELECTION=2048`
* `FREQ_MIN=0` `FREQ_MAX=300` `DISPLAY_HEIGHT=200` `DISPLAY_TIME_AXIS_DURATION=60`
* `LIVE_MODE=false`

  * If `true` → `start_time`/`end_time` = `null`

### Load Shape Controls

* `RAMP_MINUTES=3`
* `STEADY_MINUTES=7`
* `SPIKE_MINUTES=2`
* `SOAK_MINUTES=10`
* `TARGET_USERS=100`
* `SOAK_USERS=60`
* `SPIKE_USERS=200`
* `SPAWN_RATE=20`

## Basic Run (Headless)

```bash
cd focus-load
locust -f locustfile.py
```
