"""
Helper Functions
================

Utility functions for the Focus Server automation framework.
"""

import os
import time
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path


def format_timestamp(timestamp: Optional[float] = None, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format timestamp to human-readable string.
    
    Args:
        timestamp: Unix timestamp (defaults to current time)
        format_string: Format string for datetime
        
    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = time.time()
    
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime(format_string)


def validate_time_range(start_time: float, end_time: float) -> bool:
    """
    Validate that time range is valid.
    
    Args:
        start_time: Start timestamp
        end_time: End timestamp
        
    Returns:
        True if time range is valid
    """
    if start_time < 0 or end_time < 0:
        return False
    
    if end_time <= start_time:
        return False
    
    # Check if times are reasonable (not too far in the future)
    current_time = time.time()
    if start_time > current_time + 86400:  # 24 hours in the future
        return False
    
    return True


def calculate_response_time(start_time: float, end_time: Optional[float] = None) -> float:
    """
    Calculate response time in seconds.
    
    Args:
        start_time: Start timestamp
        end_time: End timestamp (defaults to current time)
        
    Returns:
        Response time in seconds
    """
    if end_time is None:
        end_time = time.time()
    
    return end_time - start_time


def generate_test_id(prefix: str = "test") -> str:
    """
    Generate a unique test ID.
    
    Args:
        prefix: Prefix for the test ID
        
    Returns:
        Unique test ID
    """
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}_{timestamp}_{unique_id}"


def cleanup_temp_files(temp_dir: str, pattern: str = "*", max_age_hours: int = 24) -> int:
    """
    Clean up temporary files older than specified age.
    
    Args:
        temp_dir: Directory to clean up
        pattern: File pattern to match
        max_age_hours: Maximum age of files to keep (in hours)
        
    Returns:
        Number of files cleaned up
    """
    temp_path = Path(temp_dir)
    if not temp_path.exists():
        return 0
    
    cutoff_time = time.time() - (max_age_hours * 3600)
    cleaned_count = 0
    
    try:
        for file_path in temp_path.glob(pattern):
            if file_path.is_file():
                file_mtime = file_path.stat().st_mtime
                if file_mtime < cutoff_time:
                    file_path.unlink()
                    cleaned_count += 1
        
        logging.getLogger(__name__).info(f"Cleaned up {cleaned_count} temporary files from {temp_dir}")
        return cleaned_count
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Error cleaning up temporary files: {e}")
        return 0


def create_test_summary(test_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a comprehensive test summary.
    
    Args:
        test_results: Dictionary of test results
        
    Returns:
        Test summary dictionary
    """
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(test_results),
        "passed": sum(1 for result in test_results.values() if result.get("status") == "passed"),
        "failed": sum(1 for result in test_results.values() if result.get("status") == "failed"),
        "skipped": sum(1 for result in test_results.values() if result.get("status") == "skipped"),
        "results": test_results
    }
    
    # Calculate success rate
    if summary["total_tests"] > 0:
        summary["success_rate"] = (summary["passed"] / summary["total_tests"]) * 100
    else:
        summary["success_rate"] = 0
    
    return summary


def validate_environment_variables(required_vars: List[str]) -> Dict[str, bool]:
    """
    Validate that required environment variables are set.
    
    Args:
        required_vars: List of required environment variable names
        
    Returns:
        Dictionary mapping variable names to their availability
    """
    validation_results = {}
    
    for var_name in required_vars:
        value = os.environ.get(var_name)
        validation_results[var_name] = value is not None and value.strip() != ""
    
    return validation_results


def get_system_info() -> Dict[str, Any]:
    """
    Get system information for test reporting.
    
    Returns:
        Dictionary containing system information
    """
    import platform
    import sys
    
    return {
        "platform": platform.platform(),
        "python_version": sys.version,
        "architecture": platform.architecture(),
        "processor": platform.processor(),
        "hostname": platform.node(),
        "timestamp": datetime.now().isoformat()
    }


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def create_directory_structure(base_path: str, structure: Dict[str, Any]) -> bool:
    """
    Create directory structure recursively.
    
    Args:
        base_path: Base path for the structure
        structure: Dictionary defining the directory structure
        
    Returns:
        True if structure was created successfully
    """
    try:
        base_path_obj = Path(base_path)
        base_path_obj.mkdir(parents=True, exist_ok=True)
        
        for name, content in structure.items():
            item_path = base_path_obj / name
            
            if isinstance(content, dict):
                # Recursive directory creation
                item_path.mkdir(exist_ok=True)
                create_directory_structure(str(item_path), content)
            else:
                # File creation
                if isinstance(content, str):
                    item_path.write_text(content)
                else:
                    item_path.write_bytes(content)
        
        return True
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Error creating directory structure: {e}")
        return False


def validate_file_exists(file_path: str) -> bool:
    """
    Validate that a file exists and is readable.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file exists and is readable
    """
    try:
        path_obj = Path(file_path)
        return path_obj.exists() and path_obj.is_file() and path_obj.stat().st_size > 0
    except Exception:
        return False


def validate_directory_exists(dir_path: str) -> bool:
    """
    Validate that a directory exists and is accessible.
    
    Args:
        dir_path: Path to the directory
        
    Returns:
        True if directory exists and is accessible
    """
    try:
        path_obj = Path(dir_path)
        return path_obj.exists() and path_obj.is_dir()
    except Exception:
        return False


def get_file_size(file_path: str) -> Optional[int]:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes or None if error
    """
    try:
        return Path(file_path).stat().st_size
    except Exception:
        return None


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable string.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted file size string
    """
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f}MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f}GB"


def retry_on_exception(func, max_retries: int = 3, delay: float = 1.0, 
                      exceptions: tuple = (Exception,)):
    """
    Decorator to retry function on exception.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        delay: Delay between retries in seconds
        exceptions: Tuple of exceptions to catch
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                if attempt < max_retries:
                    logging.getLogger(__name__).warning(
                        f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds..."
                    )
                    time.sleep(delay)
                else:
                    logging.getLogger(__name__).error(f"All {max_retries + 1} attempts failed")
        
        raise last_exception
    
    return wrapper


def mask_sensitive_data(data: str, sensitive_keys: List[str] = None) -> str:
    """
    Mask sensitive data in strings.
    
    Args:
        data: String containing potentially sensitive data
        sensitive_keys: List of keys to mask
        
    Returns:
        String with sensitive data masked
    """
    if sensitive_keys is None:
        sensitive_keys = ["password", "token", "key", "secret", "credential"]
    
    masked_data = data
    
    for key in sensitive_keys:
        # Simple masking - replace with asterisks
        masked_data = masked_data.replace(key, "*" * len(key))
    
    return masked_data


# ===================================================================
# Additional Utilities for Focus Server API Testing
# ===================================================================

def datetime_to_yymmddHHMMSS(dt: datetime) -> str:
    """
    Convert datetime to yymmddHHMMSS format string.
    
    Args:
        dt: Datetime object to convert
        
    Returns:
        Time string in yymmddHHMMSS format
    
    Example:
        >>> dt = datetime(2025, 10, 7, 14, 30, 45)
        >>> datetime_to_yymmddHHMMSS(dt)
        '251007143045'
    """
    return dt.strftime("%y%m%d%H%M%S")


def yymmddHHMMSS_to_datetime(time_str: str) -> datetime:
    """
    Convert yymmddHHMMSS format string to datetime.
    
    Args:
        time_str: Time string in yymmddHHMMSS format
        
    Returns:
        Datetime object
        
    Raises:
        ValueError: If time_str format is invalid
    
    Example:
        >>> yymmddHHMMSS_to_datetime('251007143045')
        datetime.datetime(2025, 10, 7, 14, 30, 45)
    """
    if len(time_str) != 12:
        raise ValueError(f"Invalid time format: {time_str}. Expected: yymmddHHMMSS")
    
    return datetime.strptime(time_str, "%y%m%d%H%M%S")


def generate_time_range(
    start_time: Optional[datetime] = None,
    duration_minutes: int = 10
) -> tuple[str, str]:
    """
    Generate time range in yymmddHHMMSS format.
    
    Args:
        start_time: Start datetime (default: now - duration_minutes)
        duration_minutes: Duration in minutes (default: 10)
        
    Returns:
        Tuple of (start_time_str, end_time_str) in yymmddHHMMSS format
    
    Example:
        >>> start, end = generate_time_range(duration_minutes=5)
        >>> # Returns 5-minute range ending at current time
    """
    if start_time is None:
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=duration_minutes)
    else:
        end_time = start_time + timedelta(minutes=duration_minutes)
    
    return (
        datetime_to_yymmddHHMMSS(start_time),
        datetime_to_yymmddHHMMSS(end_time)
    )


def generate_task_id(prefix: str = "task") -> str:
    """
    Generate unique task ID.
    
    Args:
        prefix: ID prefix (default: "task")
        
    Returns:
        Unique task ID in format: {prefix}_{timestamp}_{uuid}
    
    Example:
        >>> generate_task_id("test")
        'test_20251007143045_a1b2c3d4'
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"{prefix}_{timestamp}_{unique_id}"


def poll_until(condition_func, timeout_seconds: int = 60, poll_interval: float = 1.0):
    """
    Poll until condition is met or timeout.
    
    Args:
        condition_func: Function that returns True when condition met
        timeout_seconds: Maximum wait time in seconds
        poll_interval: Time between polls in seconds
        
    Returns:
        True if condition met
        
    Raises:
        TimeoutError: If timeout reached before condition met
    """
    start_time = time.time()
    logger = logging.getLogger(__name__)
    
    while time.time() - start_time < timeout_seconds:
        try:
            if condition_func():
                elapsed = time.time() - start_time
                logger.debug(f"Condition met after {elapsed:.2f}s")
                return True
        except Exception as e:
            logger.debug(f"Poll attempt failed: {e}")
        
        time.sleep(poll_interval)
    
    elapsed = time.time() - start_time
    raise TimeoutError(f"Condition not met after {elapsed:.2f}s")


def generate_config_payload(
    sensors_min: int = 0,
    sensors_max: int = 100,
    freq_min: int = 0,
    freq_max: int = 500,
    nfft: int = 1024,
    canvas_height: int = 1000,
    live: bool = True,
    duration_minutes: int = 10
) -> Dict[str, Any]:
    """
    Generate configuration task payload for testing.
    
    Args:
        sensors_min: Minimum sensor index
        sensors_max: Maximum sensor index
        freq_min: Minimum frequency Hz
        freq_max: Maximum frequency Hz
        nfft: NFFT selection
        canvas_height: Canvas height pixels
        live: Live mode flag
        duration_minutes: Duration for historic mode
        
    Returns:
        Configuration payload dictionary
    """
    payload = {
        "displayTimeAxisDuration": 10.0,
        "nfftSelection": nfft,
        "canvasInfo": {"height": canvas_height},
        "sensors": {"min": sensors_min, "max": sensors_max},
        "frequencyRange": {"min": freq_min, "max": freq_max}
    }
    
    if live:
        payload["start_time"] = None
        payload["end_time"] = None
    else:
        start_str, end_str = generate_time_range(duration_minutes=duration_minutes)
        payload["start_time"] = start_str
        payload["end_time"] = end_str
    
    return payload