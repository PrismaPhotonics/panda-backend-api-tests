## Focus Server – Load & Stress (Locust)

Base URL: `http://localhost:8500` (אחרי port-forward)

Endpoints שנבדקים:
- GET `/channels`
- GET `/live_metadata`
- POST `/configure` + GET `/metadata/{job_id}` (פולינג)
- POST `/recordings_in_time_range`
- GET `/get_recordings_timeline` (HTML)

### התקנה
```
pip install -r requirements.txt
```

### הרצה – Smoke
```
locust -f load/focus_locustfile.py --headless -u 10 -r 5 -t 5m --host http://localhost:8500
```

### פרופיל Ramp → Steady → Spike → Soak
```
set TARGET_USERS=100 & set SPIKE_USERS=200 & set SOAK_USERS=60 & \
set RAMP_MINUTES=3 & set STEADY_MINUTES=7 & set SPIKE_MINUTES=2 & set SOAK_MINUTES=10 & \
locust -f load/focus_locustfile.py --headless --run-time 25m --host http://localhost:8500
```

### משתני סביבה שימושיים
- `START_EPOCH`, `END_EPOCH` – חלון היסטורי ידוע (אחרת מתבצע גילוי דרך `/recordings_in_time_range`).
- `LIVE_MODE=true` – להריץ `/configure` עם start/end = null.
- `CHANNEL_MIN`, `CHANNEL_MAX`, `VIEW_TYPE`, `NFFT_SELECTION`, `DISPLAY_HEIGHT`, `FREQ_MIN`, `FREQ_MAX`, `DISPLAY_TIME_AXIS_DURATION` – פרמטרי קונפיג.
- `METADATA_POLL_INTERVAL`, `METADATA_POLL_TIMEOUT` – פולינג ל-`/metadata/{job_id}`.

### תוצרים
- דוחות Locust (CLI). ניתן להוסיף `--csv results/focus --html results/focus_report.html` לשמירה.

### בטיחות
- אין TLS/אימות ב-port-forward. אל תריץ נגד production.
- אל תיצור מאות עבודות `/configure` בו-זמנית – התחל נמוך והעלה בהדרגה.


