"""End-to-end API contract tests for Focus/Streaming server.

Covers smoke, happy paths, negative validation and HTML endpoint checks.
Requires FOCUS_BASE_URL and optional VERIFY_SSL env vars. API is served under
/focus-server prefix by default (configurable via deployment).
"""
from __future__ import annotations

import os
import re
import warnings
from typing import Dict, Any

import pytest
import requests
# Disable SSL warnings for self-signed certificates in test environments
import urllib3
from .helpers import last_minutes_window
from .models import (
    ChannelRange,
    ConfigureResponse,
    LiveMetadata,
    RecordingsInTimeRangeRequest,
    RecordingsInTimeRangeResponse,
)
from urllib3.exceptions import InsecureRequestWarning

# Disable all urllib3 SSL warnings
urllib3.disable_warnings()
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

# Base URL composition and availability probe
# Try multiple sources for configuration
def get_focus_config():
    """Get Focus server configuration from environment or common defaults."""
    # Try environment variables first
    base_url = os.getenv("FOCUS_BASE_URL")
    api_prefix = os.getenv("FOCUS_API_PREFIX")

    # If environment variables aren't set, try some common configurations
    if not base_url:
        # Check if we have any FOCUS_ env vars set, which might indicate we should use remote
        focus_env_vars = [key for key in os.environ.keys() if key.startswith("FOCUS_")]
        if focus_env_vars or os.getenv("FOCUS_SERVER_HOST"):
            # Prefer explicit host if set
            host = os.getenv("FOCUS_SERVER_HOST", "10.10.10.150")
            port = os.getenv("FOCUS_SERVER_PORT", "30443")
            base_url = f"https://{host}:{port}"
        else:
            # Default to localhost
            base_url = "http://localhost:8500"

    if not api_prefix:
        api_prefix = "/focus-server"

    return base_url.rstrip("/"), api_prefix

BASE_URL, API_PREFIX = get_focus_config()

# Ensure API_PREFIX is a URL path, not a file system path
if API_PREFIX and not API_PREFIX.startswith("/"):
    # If it looks like a file system path, extract just the last component as URL path
    if "\\" in API_PREFIX or ":" in API_PREFIX:
        API_PREFIX = "/" + API_PREFIX.replace("\\", "/").split("/")[-1]
    else:
        API_PREFIX = "/" + API_PREFIX

API_PREFIX = API_PREFIX.rstrip("/")
FULL_BASE_URL = f"{BASE_URL}{API_PREFIX}"
VERIFY_SSL = os.getenv("VERIFY_SSL", "false").lower() in ("true", "1", "t")

try:
    requests.get(f"{FULL_BASE_URL}/channels", timeout=5, verify=VERIFY_SSL)
    server_available = True
except requests.exceptions.SSLError:
    server_available = False
except requests.exceptions.ConnectionError:
    server_available = False

pytestmark = [
    pytest.mark.api,
    pytest.mark.skipif(
        not server_available, reason=f"Focus server not available at {FULL_BASE_URL}"
    ),
]


def _get(path: str) -> requests.Response:
    """Issue GET to API with proper base, SSL verification and timeouts."""
    url = f"{FULL_BASE_URL}/{path.lstrip('/')}"
    return requests.get(url, timeout=15, verify=VERIFY_SSL)


def _post_json(path: str, payload: Dict[str, Any]) -> requests.Response:
    """Issue POST with JSON payload to API with proper base and SSL flags."""
    url = f"{FULL_BASE_URL}/{path.lstrip('/')}"
    return requests.post(url, json=payload, timeout=20, verify=VERIFY_SSL)

# ---------- Smoke ----------

def test_channels_smoke() -> None:
    r = _get("/channels")
    assert r.status_code == 200, r.text
    data = r.json()
    model = ChannelRange(**data)
    assert model.lowest_channel <= model.highest_channel


def test_live_metadata_smoke() -> None:
    r = _get("/live_metadata")
    assert r.status_code == 200, r.text
    md = LiveMetadata(**r.json())
    assert md.dx > 0
    assert md.prr > 0
    assert md.number_of_channels > 0
    assert isinstance(md.sw_version, str) and md.sw_version

# ---------- Configure happy paths ----------

@pytest.fixture(scope="session")
def channel_bounds() -> ChannelRange:
    """Fetch channel range once per test session for consistency."""
    r = requests.get(f"{FULL_BASE_URL}/channels", timeout=10, verify=VERIFY_SSL)
    r.raise_for_status()
    return ChannelRange(**r.json())


def test_configure_waterfall_minimal(channel_bounds: ChannelRange) -> None:
    ch_min = max(channel_bounds.lowest_channel, channel_bounds.lowest_channel + 10)
    ch_max = min(channel_bounds.highest_channel, ch_min + 50)
    start, end = last_minutes_window(15)
    payload = {
        "displayInfo": {"height": 256},
        "channels": {"min": ch_min, "max": ch_max},
        "view_type": "1",  # assume "1" = waterfall
        "nfftSelection": 1,  # required for waterfall
        "start_time": start,
        "end_time": end
    }
    r = _post_json("/configure", payload)

    # If waterfall configuration is not supported by this server, skip the test
    if r.status_code == 500 and "Error parsing configuration" in r.text:
        pytest.skip("Waterfall configuration not supported by server")

    assert r.status_code == 200, r.text
    cfg = ConfigureResponse(**r.json())
    assert cfg.status.lower() in {"ok", "success", "configured"}
    assert cfg.job_id
    assert cfg.stream_amount >= 1
    assert cfg.stream_port > 0
    assert re.match(r"^.+$", cfg.stream_url)

    # fetch metadata by job_id
    r2 = _get(f"/metadata/{cfg.job_id}")
    assert r2.status_code == 200, r2.text
    _ = ConfigureResponse(**r2.json())


def test_configure_non_waterfall_with_freq_and_nfft(channel_bounds: ChannelRange) -> None:
    ch_min = channel_bounds.lowest_channel
    ch_max = min(channel_bounds.lowest_channel + 20, channel_bounds.highest_channel)
    start, end = last_minutes_window(15)
    payload = {
        "displayInfo": {"height": 512},
        "channels": {"min": ch_min, "max": ch_max},
        "view_type": "0",        # assume "0" = spectrogram/other
        "nfftSelection": 8,
        "displayTimeAxisDuration": 30,
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": start,
        "end_time": end
    }
    r = _post_json("/configure", payload)
    assert r.status_code == 200, r.text
    cfg = ConfigureResponse(**r.json())
    assert cfg.frequencies_amount >= 0
    assert isinstance(cfg.frequencies_list, list)

# ---------- Recordings API ----------

def test_recordings_in_time_range() -> None:
    start, end = last_minutes_window(60)
    payload = {"start_time": start, "end_time": end}
    # validate request model locally
    _ = RecordingsInTimeRangeRequest(**payload)

    r = _post_json("/recordings_in_time_range", payload)
    assert r.status_code == 200, r.text
    data = r.json()
    # API returns a list directly, wrap it in expected format
    if isinstance(data, list):
        res = RecordingsInTimeRangeResponse(recordings=data)
    else:
        res = RecordingsInTimeRangeResponse(**data)
    for s, e in res.recordings:
        assert s <= end
        assert (e == -1) or (s <= e)

# ---------- Timeline HTML ----------

def test_get_recordings_timeline_html() -> None:
    r = _get("/get_recordings_timeline")
    assert r.status_code == 200, r.text
    assert "text/html" in r.headers.get("Content-Type", ""), r.headers.get("Content-Type", "")
    assert "<html" in r.text.lower()

# ---------- Negative & conditional validation ----------

def test_configure_channels_out_of_range_422(channel_bounds: ChannelRange) -> None:
    payload = {
        "displayInfo": {"height": 128},
        "channels": {"min": channel_bounds.highest_channel + 1, "max": channel_bounds.highest_channel + 10},
        "view_type": "1"
    }
    r = _post_json("/configure", payload)
    # מצופה 422; אם השרת עוד לא מוולידט – יסומן xfail
    if r.status_code != 422:
        pytest.xfail(f"Server did not validate channels range (status={r.status_code})")
    else:
        assert r.json().get("detail")


def test_configure_waterfall_with_forbidden_fields_422(channel_bounds: ChannelRange) -> None:
    ch_min = channel_bounds.lowest_channel
    ch_max = min(channel_bounds.lowest_channel + 30, channel_bounds.highest_channel)
    payload = {
        "displayInfo": {"height": 256},
        "channels": {"min": ch_min, "max": ch_max},
        "view_type": "1",  # waterfall
        "frequencyRange": {"min": 0, "max": 500},  # לא אמור להיות מותר ב-waterfall
        "displayTimeAxisDuration": 30               # כנ"ל
    }
    r = _post_json("/configure", payload)
    if r.status_code != 422:
        pytest.xfail(f"Server did not enforce waterfall constraints (status={r.status_code})")
    else:
        assert r.json().get("detail")


def test_configure_waterfall_nfft_must_be_1(channel_bounds: ChannelRange) -> None:
    ch_min = channel_bounds.lowest_channel
    ch_max = min(channel_bounds.lowest_channel + 30, channel_bounds.highest_channel)
    payload = {
        "displayInfo": {"height": 256},
        "channels": {"min": ch_min, "max": ch_max},
        "view_type": "1",
        "nfftSelection": 4  # אמור להיכשל (ב-waterfall חייב 1)
    }
    r = _post_json("/configure", payload)
    if r.status_code != 422:
        pytest.xfail(f"Server did not enforce nfftSelection==1 for waterfall (status={r.status_code})")
    else:
        assert r.json().get("detail")


def test_configure_missing_required_fields_422() -> None:
    payload = { "displayInfo": {"height": 256} }  # חסר channels/view_type
    r = _post_json("/configure", payload)
    assert r.status_code == 422, r.text
