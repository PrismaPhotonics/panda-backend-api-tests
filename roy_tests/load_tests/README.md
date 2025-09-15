# Focus Server – Load Testing (Locust)

## דרישות
- Python 3.10+
- `pip install -r requirements.txt`
- חיבור לשרות:
  - בקלאסטר: `kubectl -n default port-forward svc/focus-server-service 8500:5000`
  - Base URL: `http://localhost:8500`

## משתני סביבה (אופציונלי)
- `VERIFY_TLS=false`  # port-forward הוא HTTP
- `AUTH_TOKEN=<token-if-needed>`
- `START_EPOCH=1757752339` `END_EPOCH=1757773293`  # חלון ידוע עם נתונים
- `CHANNEL_MIN=1` `CHANNEL_MAX=750` `VIEW_TYPE=0` `NFFT_SELECTION=2048`
- `FREQ_MIN=0` `FREQ_MAX=300` `DISPLAY_HEIGHT=200` `DISPLAY_TIME_AXIS_DURATION=60`
- `LIVE_MODE=false`  # אם true → start_time/end_time = null
- Load shape:
  - `RAMP_MINUTES=3` `STEADY_MINUTES=7` `SPIKE_MINUTES=2` `SOAK_MINUTES=10`
  - `TARGET_USERS=100` `SOAK_USERS=60` `SPIKE_USERS=200` `SPAWN_RATE=20`

## הרצה בסיסית (Headless)
```bash
cd focus-load
locust -f locustfile.py
