"""
Focus Server Load Test (HTTP, no auth/TLS)
Targets:
  - GET /channels
  - GET /live_metadata
  - POST /configure + GET /metadata/{job_id}
  - POST /recordings_in_time_range
  - GET /get_recordings_timeline (HTML)

Run example (from load_tests/ dir):
  python -m locust -f locust_focus_server.py --headless -u 5 -r 2 -t 1 m --host http://localhost:8500
"""
from __future__ import annotations

import os
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import csv
from typing import Any, List, Optional, Tuple

from gevent import sleep as gevent_sleep
from gevent.lock import Semaphore
from locust import HttpUser, task, between, events
from locust import LoadTestShape


def parse_recordings_payload(raw_json: Any) -> List[Tuple[int, int]]:
    """Normalize recording payload into a list of (start, end) epochs.

    Expected structure: {"recordings": [[start_epoch, end_epoch], ...]}
    Any malformed entries are ignored gracefully.
    """
    out: List[Tuple[int, int]] = []
    if isinstance(raw_json, dict) and "recordings" in raw_json:
        for it in (raw_json.get("recordings") or []):
            if isinstance(it, list) and len(it) == 2:
                try:
                    start_epoch = int(it[0])
                    end_epoch = int(it[1])
                except (ValueError, TypeError):
                    continue
                out.append((start_epoch, end_epoch))
    return out


def pick_valid_window(client) -> Optional[Tuple[int, int]]:
    """Return a (start,end) window from ENV or by discovering via /recordings_in_time_range."""
    start_env = os.getenv("START_EPOCH")
    end_env = os.getenv("END_EPOCH")
    if start_env and end_env:
        try:
            return int(start_env), int(end_env)
        except ValueError:
            pass

    now = datetime.now(timezone.utc)
    start = int((now - timedelta(days=3)).timestamp())
    end = int((now + timedelta(days=1)).timestamp())
    payload = {"start_time": start, "end_time": end}
    with client.post(
        _url("/recordings_in_time_range"),
        json=payload,
        name="POST /recordings_in_time_range (discover)",
        catch_response=True,
        timeout=_req_timeout(),
    ) as resp:
        if resp.status_code >= 400:
            resp.failure(f"HTTP {resp.status_code}: {resp.text[:200]}")
            return None
        if not _is_json(resp):
            resp.failure(f"Non-JSON response (ct={resp.headers.get('Content-Type')!r}): {resp.text[:200]}")
            return None
        data = resp.json()
    recs = parse_recordings_payload(data)
    if not recs:
        return None
    recs.sort(key=lambda x: x[0])
    return recs[-1]


def make_configure_payload(start_epoch: Optional[int], end_epoch: Optional[int]) -> dict:
    """Build a valid ConfigureRequest payload."""
    live_mode = os.getenv("LIVE_MODE", "false").lower() in {"1", "true", "yes"}
    start_val = None if live_mode else start_epoch
    end_val = None if live_mode else end_epoch
    return {
        "displayTimeAxisDuration": int(os.getenv("DISPLAY_TIME_AXIS_DURATION", "60")),
        "nfftSelection": int(os.getenv("NFFT_SELECTION", "2048")),
        "displayInfo": {"height": int(os.getenv("DISPLAY_HEIGHT", "200"))},
        "channels": {
            "min": int(os.getenv("CHANNEL_MIN", "1")),
            "max": int(os.getenv("CHANNEL_MAX", "750")),
        },
        "frequencyRange": {
            "min": int(os.getenv("FREQ_MIN", "0")),
            "max": int(os.getenv("FREQ_MAX", "300")),
        },
        "start_time": start_val,
        "end_time": end_val,
        "view_type": os.getenv("VIEW_TYPE", "0"),
    }


def _req_timeout() -> Tuple[float, float]:
    """Return (connect, read) timeouts from env with sensible defaults."""
    connect = float(os.getenv("CONNECT_TIMEOUT", "3.0"))
    read = float(os.getenv("READ_TIMEOUT", "15.0"))
    return (connect, read)


API_BASE: str = os.getenv("API_BASE", "").rstrip("/")


def _url(path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    return f"{API_BASE}{path}" if API_BASE else path


def _is_json(resp) -> bool:
    try:
        ct = resp.headers.get("Content-Type", "")
    except Exception:
        return False
    return "application/json" in ct.lower()


def _verify_ssl() -> bool:
    """Return verify SSL flag from env VERIFY_SSL (default: false)."""
    val = os.getenv("VERIFY_SSL", "false").lower()
    return val in {"1", "true", "yes"}


def _parse_headers_string(raw: str) -> dict:
    """Parse a semicolon-separated header string: "Key: Value; K2: V2" -> dict.

    This is forgiving and ignores malformed entries. Values are trimmed.
    """
    headers: dict = {}
    for part in [p.strip() for p in raw.split(";") if p.strip()]:
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key:
            headers[key] = value
    return headers


def _load_default_headers() -> dict:
    """Load default headers from env AUTH_HEADERS or AUTH_HEADER.

    Supports:
      - AUTH_HEADERS as JSON mapping string: '{"Authorization": "Bearer ..."}'
      - AUTH_HEADERS as 'Key: Value; Key2: Value2'
      - AUTH_HEADER as single 'Key: Value'
    """
    raw_multi = os.getenv("AUTH_HEADERS")
    if raw_multi:
        raw_multi = raw_multi.strip()
        if raw_multi.startswith("{"):
            try:
                import json as _json

                parsed = _json.loads(raw_multi)
                if isinstance(parsed, dict):
                    return {str(k): str(v) for k, v in parsed.items()}
            except Exception:
                pass
        # Fallback to semicolon-separated parsing
        return _parse_headers_string(raw_multi)

    raw_single = os.getenv("AUTH_HEADER")
    if raw_single:
        return _parse_headers_string(raw_single)
    return {}


_CONFIG_SEM: Optional[Semaphore] = None


def init_config_semaphore(max_concurrent: int) -> Semaphore:
    """Initialize and return a module-level semaphore that limits concurrent /configure calls."""
    global _CONFIG_SEM
    if _CONFIG_SEM is None:
        _CONFIG_SEM = Semaphore(max_concurrent)
    return _CONFIG_SEM


_JOB_EVENTS: List[dict] = []
_STOP_REQUESTED: bool = False


def _results_dir() -> Path:
    d = Path(os.getenv("RESULTS_DIR", "results"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def append_job_event(
    event: str,
    job_id: str,
    attempt: int,
    start_epoch: Optional[int],
    end_epoch: Optional[int],
    duration_ms: Optional[int],
    user_tag: Optional[str],
) -> None:
    """Append a job lifecycle event for later reporting (CSV/JSON)."""
    rec = {
        "time": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "job_id": job_id,
        "attempt": attempt,
        "start_epoch": start_epoch,
        "end_epoch": end_epoch,
        "duration_ms": duration_ms,
        "user": user_tag,
    }
    _JOB_EVENTS.append(rec)


def write_job_events_summary() -> None:
    """Write collected job events into CSV and JSON under results/ directory."""
    out_dir = _results_dir()
    csv_path = out_dir / "jobs_created.csv"
    json_path = out_dir / "jobs_created.json"
    fields = [
        "time",
        "event",
        "job_id",
        "attempt",
        "user",
        "start_epoch",
        "end_epoch",
        "duration_ms",
    ]
    try:
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for rec in _JOB_EVENTS:
                w.writerow(rec)
    except (OSError, csv.Error):
        return

    # Write JSON as well for programmatic consumption
    try:
        import json as _json

        with json_path.open("w", encoding="utf-8") as jf:
            _json.dump(_JOB_EVENTS, jf, ensure_ascii=False, indent=2)
    except (OSError, TypeError, ValueError):
        pass


@events.test_start.add_listener
def _on_test_start(environment, **kwargs):
    # Ensure results dir exists and reset a stop flag
    global _STOP_REQUESTED
    _STOP_REQUESTED = False
    _results_dir()


@events.test_stop.add_listener
def _on_test_stop(environment, **kwargs):
    # Signal cooperative stop and write job events at the end of test
    global _STOP_REQUESTED
    _STOP_REQUESTED = True
    write_job_events_summary()


def validate_configure_response(data: Any) -> Optional[str]:
    """Validate ConfigureResponse shape and return job_id if valid, else None.

    Server sometimes returns inconsistent types; we only strictly validate fields we rely on.
    """
    if not isinstance(data, dict):
        return None
    job_id = data.get("job_id")
    if not isinstance(job_id, str):
        return None
    # Expect a pattern like "GPU_SLOT-JOB_NUMBER", e.g., "1-62703"
    if not re.match(r"^[0-9]+-[0-9]+$", job_id):
        # Accept anyway but flag as warning
        events.request.fire(
            request_type="VALIDATE",
            name="configure:job_id-format-warning",
            response_time=0,
            response_length=0,
            exception=None,
        )
    # Basic sanity checks for optional fields
    if "stream_url" not in data or "stream_port" not in data:
        events.request.fire(
            request_type="VALIDATE",
            name="configure:missing-stream-info",
            response_time=0,
            response_length=0,
            exception=None,
        )
    return job_id


def create_job(client, window: Optional[Tuple[int, int]], max_concurrent: int) -> Optional[str]:
    """Create a new job by calling POST /configure and return job_id if successful."""
    start_epoch, end_epoch = (None, None)
    if window:
        start_epoch, end_epoch = window
    payload = make_configure_payload(start_epoch, end_epoch)

    sem = init_config_semaphore(max_concurrent)
    with sem:
        with client.post(
            _url("/configure"),
            json=payload,
            name="POST /configure",
            catch_response=True,
            timeout=_req_timeout(),
        ) as resp:
            if resp.status_code >= 400:
                resp.failure(f"HTTP {resp.status_code}: {resp.text[:200]}")
                return None
            if not _is_json(resp):
                resp.failure(f"Non-JSON response (ct={resp.headers.get('Content-Type')!r}): {resp.text[:200]}")
                return None
            data = resp.json()
    job_id = validate_configure_response(data)
    if not job_id:
        events.request.fire(
            request_type="VALIDATE",
            name="configure:missing-job_id",
            response_time=0,
            response_length=0,
            exception=AssertionError("Missing job_id"),
        )
        return None
    return job_id


class FocusUser(HttpUser):
    """Simulated user issuing Focus Server HTTP requests under load_tests."""

    wait_time = between(0.1, 0.5)

    def __init__(self, environment):
        super().__init__(environment)
        # Predefine attributes for linters and readability
        self.window: Optional[Tuple[int, int]] = None
        self.last_job_id: Optional[str] = None
        self.last_job_ts: float = 0.0
        self.user_tag: str = ""
        # Optionally set default headers (auth, etc.) from env
        default_headers = _load_default_headers()
        if default_headers:
            try:
                self.client.headers.update(default_headers)
            except Exception:
                pass

    def on_start(self):
        self.window = pick_valid_window(self.client)
        # Cache a last known job id per user
        self.last_job_id = None
        self.last_job_ts = 0.0
        self.user_tag = f"user-{id(self) % 100000}"

        # Create a valid job_id up-front for tests that depend on real jobs
        create_on_start = os.getenv("CREATE_JOB_ON_START", "true").lower() in {"1", "true", "yes"}
        max_concurrent = int(os.getenv("MAX_CONCURRENT_CONFIG", "3"))
        if create_on_start:
            job_id = create_job(self.client, self.window, max_concurrent)
            if job_id:
                self.last_job_id = job_id
                self.last_job_ts = time.time()
                # Log creation event from on_start (attempt 0)
                start_epoch, end_epoch = (None, None)
                if self.window:
                    start_epoch, end_epoch = self.window
                append_job_event(
                    event="created",
                    job_id=job_id,
                    attempt=0,
                    start_epoch=start_epoch,
                    end_epoch=end_epoch,
                    duration_ms=None,
                    user_tag=self.user_tag,
                )
            else:
                # Surface a validation failure to Locust stats
                events.request.fire(
                    request_type="VALIDATE",
                    name="on_start:create-job-failed",
                    response_time=0,
                    response_length=0,
                    exception=AssertionError("Failed to create job on start"),
                )

    @task(3)
    def channels(self):
        with self.client.get(_url("/channels"), name="GET /channels", catch_response=True, timeout=_req_timeout(), verify=_verify_ssl()) as resp:
            if resp.status_code >= 400:
                resp.failure(f"HTTP {resp.status_code}: {resp.text[:200]}")
            elif not _is_json(resp):
                resp.failure(f"Non-JSON response (ct={resp.headers.get('Content-Type')!r}): {resp.text[:200]}")
            else:
                resp.success()

    @task(3)
    def live_meta(self):
        with self.client.get(_url("/live_metadata"), name="GET /live_metadata", catch_response=True, timeout=_req_timeout(), verify=_verify_ssl()) as resp:
            if resp.status_code >= 400:
                resp.failure(f"HTTP {resp.status_code}: {resp.text[:200]}")
            elif not _is_json(resp):
                resp.failure(f"Non-JSON response (ct={resp.headers.get('Content-Type')!r}): {resp.text[:200]}")
            else:
                resp.success()

    @task(1)
    def timeline(self):
        # This endpoint is expected to return HTML. Mark 2xx as success regardless of JSON.
        with self.client.get(
            _url("/get_recordings_timeline"),
            name="GET /get_recordings_timeline (html)",
            catch_response=True,
            timeout=_req_timeout(),
            verify=_verify_ssl(),
        ) as resp:
            if resp.status_code >= 400:
                resp.failure(f"HTTP {resp.status_code}: {resp.text[:200]}")
            else:
                resp.success()

    @task(2)
    def recs(self):
        now = datetime.now(timezone.utc)
        start = int((now - timedelta(days=1)).timestamp())
        end = int(now.timestamp())
        with self.client.post(
            _url("/recordings_in_time_range"),
            json={"start_time": start, "end_time": end},
            name="POST /recordings_in_time_range",
            catch_response=True,
            timeout=_req_timeout(),
            verify=_verify_ssl(),
        ) as resp:
            if resp.status_code >= 400:
                resp.failure(f"HTTP {resp.status_code}: {resp.text[:200]}")
            elif not _is_json(resp):
                resp.failure(f"Non-JSON response (ct={resp.headers.get('Content-Type')!r}): {resp.text[:200]}")
            else:
                resp.success()

    @task(1)
    def configure_and_poll(self):
        # Global controls
        max_concurrent = int(os.getenv("MAX_CONCURRENT_CONFIG", "3"))
        metadata_timeout = float(os.getenv("METADATA_POLL_TIMEOUT", "120"))
        base_interval = float(os.getenv("METADATA_POLL_INTERVAL", "0.2"))
        initial_delay = float(os.getenv("INITIAL_POLL_DELAY_SEC", "1.5"))

        # Ensure semaphore is initialized (for any later creations)
        init_config_semaphore(max_concurrent)

        retry_on_timeout = os.getenv("RETRY_ON_TIMEOUT", "true").lower() in {"1", "true", "yes"}
        max_attempts = 2 if retry_on_timeout else 1

        for attempt in range(max_attempts):
            if _STOP_REQUESTED:
                return
            # Create a fresh job for this attempt
            job_id = create_job(self.client, self.window, max_concurrent)
            if not job_id:
                return
            self.last_job_id = job_id
            self.last_job_ts = time.time()

            # Record creation event
            start_epoch, end_epoch = (None, None)
            if self.window:
                start_epoch, end_epoch = self.window
            append_job_event(
                event="created",
                job_id=job_id,
                attempt=attempt + 1,
                start_epoch=start_epoch,
                end_epoch=end_epoch,
                duration_ms=None,
                user_tag=self.user_tag,
            )

            # Initial grace before the first poll
            # Respect cooperative stop during initial delay
            slept = 0.0
            while slept < initial_delay:
                if _STOP_REQUESTED:
                    return
                gevent_sleep(min(0.1, initial_delay - slept))
                slept += 0.1

            # Poll with backoff; treat 404/5xx as temporary until deadline
            deadline = time.time() + metadata_timeout
            interval = base_interval
            start_poll = time.time()
            while time.time() < deadline and not _STOP_REQUESTED:
                with self.client.get(
                    _url(f"/metadata/{job_id}"),
                    name="GET /metadata/{job_id}",
                    catch_response=True,
                    timeout=_req_timeout(),
                    verify=_verify_ssl(),
                ) as mresp:
                    if 200 <= mresp.status_code < 300:
                        mresp.success()
                        # success for this job
                        append_job_event(
                            event="completed",
                            job_id=job_id,
                            attempt=attempt + 1,
                            start_epoch=start_epoch,
                            end_epoch=end_epoch,
                            duration_ms=int((time.time() - start_poll) * 1000),
                            user_tag=self.user_tag,
                        )
                        return
                    if mresp.status_code == 404:
                        # Treat 404 as temporary for the whole polling window; fail only on timeout
                        mresp.success()
                    elif mresp.status_code >= 500:
                        # Temporary server error: do not count as failure
                        mresp.success()
                    else:
                        # Other 4xx are likely permanent for this job
                        mresp.failure(f"HTTP {mresp.status_code}: {mresp.text[:200]}")
                        return
                # Sleep in small chunks to honor cooperative stop
                slept = 0.0
                while slept < interval:
                    if _STOP_REQUESTED:
                        return
                    step = min(0.1, interval - slept)
                    gevent_sleep(step)
                    slept += step
                interval = min(interval * 2, 2.0)

            # Timed out on this attempt; if we have another attempt, retry with a new job
            if _STOP_REQUESTED:
                return
            append_job_event(
                event="timeout",
                job_id=job_id,
                attempt=attempt + 1,
                start_epoch=start_epoch,
                end_epoch=end_epoch,
                duration_ms=int((time.time() - start_poll) * 1000),
                user_tag=self.user_tag,
            )
            events.request.fire(
                request_type="POLL",
                name="GET /metadata/{job_id}:timeout",
                response_time=int((time.time() - start_poll) * 1000),
                response_length=0,
                exception=TimeoutError("Timed out waiting for metadata"),
            )
            if attempt < max_attempts - 1:
                continue
            return


# ======================
# Load Shapes (profiles)
# ======================

class RampShape(LoadTestShape):
    """Gradual ramp-up and graceful ramp-down.

    Controlled via env:
      RAMP_USERS=20, RAMP_SPAWN_RATE=2, RAMP_STAGE_SECS=60
    """

    def __init__(self):
        super().__init__()
        self.target_users = int(os.getenv("RAMP_USERS", "20"))
        self.spawn_rate = float(os.getenv("RAMP_SPAWN_RATE", "2"))
        self.stage_secs = int(os.getenv("RAMP_STAGE_SECS", "60"))

    def tick(self):
        run_time = self.get_run_time()
        if run_time < self.stage_secs:
            # ramp up
            users = int((run_time / self.stage_secs) * self.target_users)
            return users, self.spawn_rate
        elif run_time < self.stage_secs * 2:
            # steady at peak
            return self.target_users, self.spawn_rate
        elif run_time < self.stage_secs * 3:
            # ramp down
            down_time = run_time - self.stage_secs * 2
            users = max(0, self.target_users - int((down_time / self.stage_secs) * self.target_users))
            return users, self.spawn_rate
        return None


class SteadyShape(LoadTestShape):
    """Flat steady-state for given duration.

    STEADY_USERS=20, STEADY_SPAWN_RATE=2, STEADY_DURATION=120
    """

    def __init__(self):
        super().__init__()
        self.users = int(os.getenv("STEADY_USERS", "20"))
        self.spawn_rate = float(os.getenv("STEADY_SPAWN_RATE", "2"))
        self.duration = int(os.getenv("STEADY_DURATION", "120"))

    def tick(self):
        if self.get_run_time() < self.duration:
            return self.users, self.spawn_rate
        return None


class SpikeShape(LoadTestShape):
    """Sudden spike then drop.

    SPIKE_BASE=5, SPIKE_PEAK=50, SPIKE_RISE_SECS=10, SPIKE_HOLD_SECS=20, SPIKE_FALL_SECS=10
    """

    def __init__(self):
        super().__init__()
        self.base = int(os.getenv("SPIKE_BASE", "5"))
        self.peak = int(os.getenv("SPIKE_PEAK", "50"))
        self.rise = int(os.getenv("SPIKE_RISE_SECS", "10"))
        self.hold = int(os.getenv("SPIKE_HOLD_SECS", "20"))
        self.fall = int(os.getenv("SPIKE_FALL_SECS", "10"))
        self.spawn_rate = float(os.getenv("SPIKE_SPAWN_RATE", "5"))

    def tick(self):
        t = self.get_run_time()
        if t < self.rise:
            users = self.base + int((t / self.rise) * (self.peak - self.base))
            return users, self.spawn_rate
        elif t < self.rise + self.hold:
            return self.peak, self.spawn_rate
        elif t < self.rise + self.hold + self.fall:
            dt = t - (self.rise + self.hold)
            users = max(self.base, self.peak - int((dt / self.fall) * (self.peak - self.base)))
            return users, self.spawn_rate
        return None


def select_shape() -> Optional[LoadTestShape]:
    name = os.getenv("LOAD_SHAPE", "").lower()
    if name == "ramp":
        return RampShape()
    if name == "steady":
        return SteadyShape()
    if name == "spike":
        return SpikeShape()
    return None


# If Locust imports this file, it will look for a "shape" global
shape = select_shape()
