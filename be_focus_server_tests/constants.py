"""
Production-aligned constants for Focus Server tests.
=====================================================

These values are derived from usersettings.new_production_client.json
and represent the actual production constraints and limits.

IMPORTANT: Update these values when production configuration changes.
           Always verify against the production usersettings file.

Source: config/usersettings.new_production_client.json

Author: QA Automation
Date: 2025-12-09
"""

# =============================================================================
# FREQUENCY CONSTRAINTS
# =============================================================================
FREQUENCY_MAX_HZ = 1000  # Production max (NOT 500 or 15000!)
FREQUENCY_MIN_HZ = 0
FREQUENCY_MIN_RANGE = 1  # Minimum difference between min and max

# =============================================================================
# CHANNEL/SENSOR CONSTRAINTS
# =============================================================================
SENSORS_RANGE = 2222  # Max channels (NOT 2500!)
DEFAULT_START_CHANNEL = 11
DEFAULT_END_CHANNEL = 109
DEFAULT_CHANNEL_COUNT = DEFAULT_END_CHANNEL - DEFAULT_START_CHANNEL + 1  # 99 channels

# =============================================================================
# WINDOW CONSTRAINTS
# =============================================================================
MAX_WINDOWS = 30

# =============================================================================
# NFFT OPTIONS (Power of 2 values)
# =============================================================================
NFFT_OPTIONS = [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
DEFAULT_NFFT = 1024
NFFT_MIN = min(NFFT_OPTIONS)  # 128
NFFT_MAX = max(NFFT_OPTIONS)  # 65536

# Invalid NFFT values for negative testing
INVALID_NFFT_VALUES = [
    0,      # Zero
    -1,     # Negative
    100,    # Not power of 2
    127,    # One less than valid
    129,    # One more than valid
    500,    # Not power of 2
    1000,   # Not power of 2 (common mistake)
    65537,  # One more than max
    131072, # Too large
]

# =============================================================================
# DISPLAY DEFAULTS
# =============================================================================
DEFAULT_DISPLAY_TIME_AXIS_DURATION = 10
DEFAULT_DISPLAY_INFO_HEIGHT = 1000

# =============================================================================
# TIMEOUTS (for gRPC and streaming)
# =============================================================================
GRPC_TIMEOUT_SECONDS = 500
STREAM_TIMEOUT_SECONDS = 600
MAX_RETRIES = 10

# =============================================================================
# VIEW TYPES
# =============================================================================
# These correspond to ViewType enum values
VIEW_TYPE_MULTICHANNEL = 0
VIEW_TYPE_SINGLECHANNEL = 1
VIEW_TYPE_SPECTROGRAM = 2

VALID_VIEW_TYPES = [VIEW_TYPE_MULTICHANNEL, VIEW_TYPE_SINGLECHANNEL, VIEW_TYPE_SPECTROGRAM]
INVALID_VIEW_TYPES = [-1, 3, 99, 100]

# =============================================================================
# DEFAULT PAYLOAD TEMPLATE
# =============================================================================
def get_default_configure_payload():
    """
    Returns a valid default payload for ConfigureRequest.
    All values aligned to production constraints.
    """
    return {
        "displayTimeAxisDuration": DEFAULT_DISPLAY_TIME_AXIS_DURATION,
        "nfftSelection": DEFAULT_NFFT,
        "displayInfo": {"height": DEFAULT_DISPLAY_INFO_HEIGHT},
        "channels": {"min": DEFAULT_START_CHANNEL, "max": DEFAULT_END_CHANNEL},
        "frequencyRange": {"min": FREQUENCY_MIN_HZ, "max": FREQUENCY_MAX_HZ},
        "start_time": None,
        "end_time": None,
    }
