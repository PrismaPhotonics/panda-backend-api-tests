## Locust – Safe Load Testing for Prisma Web APIs

### Scope & Safety
- Allowed origin: `https://10.10.10.150:30443`
- Site: `prisma-210-1000`
- Non-destructive only (GET calls). Authentication for setup only.
- Start with low RPS; increase gradually with approval.

### Install
```
pip install -r requirements.txt
```

### Run (headless)
```
locust -f load/locustfile.py --headless \
  --host https://10.10.10.150:30443 \
  -u 25 -r 5 -t 10m
```

### Web UI (optional)
```
locust -f load/locustfile.py --host https://10.10.10.150:30443
```
Then open http://localhost:8089 and set Users/Spawn rate/Test duration.

### Mix (weights)
- alerts_live: 5
- map_geochannel: 3
- map_reportline: 3
- geofence_live: 2
- region_with_general: 2
- point_map_setup: 2
- feature_flags: 1
- system_status: 1
- live_metadata: 1
- map_tiles_sample: 1

### Notes
- SSL in lab is self-signed; this harness sets verify=False for tests only.
- Avoid stressing `/socket.io` or `/configure` without explicit approval.
- Monitor 429/5xx and p95/p99; stop on persistent degradation.


