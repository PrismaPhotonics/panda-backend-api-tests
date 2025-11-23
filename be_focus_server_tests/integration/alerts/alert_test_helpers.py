"""
Helper functions for alert integration tests.

This module provides reusable functions for sending alerts via the Prisma Web App API.
"""

import logging
import requests
import time
from typing import Dict, Any, Optional, List, Set
from datetime import datetime

logger = logging.getLogger(__name__)

# Module-level set to track alert IDs for cleanup (set by conftest fixture)
_alert_ids_created: Set[str] = set()


def authenticate_session(base_url: str, username: str = "prisma", password: str = "prisma") -> requests.Session:
    """
    Authenticate and return a session with access-token cookie.
    
    Args:
        base_url: Base URL for Prisma Web App API (e.g., "https://10.10.10.100/prisma/api/")
        username: Username for authentication
        password: Password for authentication
    
    Returns:
        Authenticated requests.Session
    
    Raises:
        requests.HTTPError: If authentication fails
    """
    session = requests.Session()
    session.verify = False  # Self-signed certificate
    
    # Ensure base_url ends with /
    if not base_url.endswith("/"):
        base_url += "/"
    
    login_url = base_url + "auth/login"
    logger.debug(f"Authenticating at: {login_url}")
    
    login_resp = session.post(
        login_url,
        json={"username": username, "password": password},
        timeout=15
    )
    login_resp.raise_for_status()
    
    logger.debug("Authentication successful")
    return session


def send_alert_via_api(
    config_manager,
    alert_payload: Dict[str, Any],
    base_url: Optional[str] = None,
    site_id: Optional[str] = None,
    session: Optional[requests.Session] = None,
    track_for_cleanup: bool = True,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> requests.Response:
    """
    Send an alert via the Prisma Web App API push-to-rabbit endpoint.
    
    Args:
        config_manager: Configuration manager instance
        alert_payload: Alert payload dictionary with keys:
            - alertsAmount: int
            - dofM: int (Distance on fiber in meters)
            - classId: int (103=SC, 104=SD)
            - severity: int (1, 2, or 3)
            - alertIds: List[str]
        base_url: Optional base URL override
        site_id: Optional site ID override
        session: Optional authenticated session (if provided, will reuse it instead of creating new one)
        track_for_cleanup: If True, track alert IDs for automatic cleanup (default: True)
        max_retries: Maximum number of retries for 429 errors (default: 3)
        retry_delay: Initial delay between retries in seconds (default: 1.0)
    
    Returns:
        requests.Response: HTTP response from the API
    
    Raises:
        requests.HTTPError: If the request fails after all retries
    """
    # Get configuration
    if not base_url:
        api_config = config_manager.get("focus_server", {})
        base_url = api_config.get("frontend_api_url", "https://10.10.10.100/prisma/api/")
    
    if not site_id:
        site_id = config_manager.get("site_id", "prisma-210-1000")
    
    # Clean up base URL if needed
    if "/internal/sites/" in base_url:
        base_url = base_url.split("/internal/sites/")[0]
    if not base_url.endswith("/"):
        base_url += "/"
    
    # Authenticate if no session provided
    if session is None:
        session = authenticate_session(base_url)
    
    # Send alert with retry logic for 429 (Rate Limiting)
    alert_url = base_url + f"{site_id}/api/push-to-rabbit"
    logger.debug(f"Sending alert to: {alert_url}")
    logger.debug(f"Alert payload: {alert_payload}")
    
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            response = session.post(alert_url, json=alert_payload, timeout=15)
            
            # If rate limited (429), retry with exponential backoff
            if response.status_code == 429:
                if attempt < max_retries:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Rate limited (429). Retrying in {wait_time:.2f}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    # Last attempt, raise the error
                    response.raise_for_status()
            
            # For other errors, raise immediately
            response.raise_for_status()
            
            logger.debug(f"Alert sent successfully. Status: {response.status_code}")
            
            # Track alert IDs for cleanup if requested
            if track_for_cleanup and 'alertIds' in alert_payload:
                alert_ids = alert_payload['alertIds']
                if isinstance(alert_ids, list) and alert_ids:
                    # Add to module-level set for cleanup (set by conftest fixture)
                    try:
                        # Import the module to access the set
                        import be_focus_server_tests.integration.alerts.alert_test_helpers as helpers_module
                        if hasattr(helpers_module, '_alert_ids_created'):
                            helpers_module._alert_ids_created.update(alert_ids)
                            logger.debug(f"Tracked {len(alert_ids)} alert IDs for cleanup")
                    except Exception:
                        # If tracking not available, silently skip
                        pass
            
            return response
            
        except requests.exceptions.HTTPError as e:
            last_error = e
            if e.response.status_code != 429 or attempt >= max_retries:
                raise
        except Exception as e:
            last_error = e
            raise
    
    # Should not reach here, but just in case
    if last_error:
        raise last_error
    raise RuntimeError("Unexpected error in send_alert_via_api")


def create_alert_payload(
    class_id: int,
    dof_m: int,
    severity: int,
    alert_id: Optional[str] = None,
    alerts_amount: int = 1
) -> Dict[str, Any]:
    """
    Create a standard alert payload.
    
    Args:
        class_id: Alert class ID (103=SC, 104=SD)
        dof_m: Distance on fiber in meters
        severity: Severity level (1, 2, or 3)
        alert_id: Optional alert ID (defaults to timestamp-based)
        alerts_amount: Number of alerts (default: 1)
    
    Returns:
        Alert payload dictionary
    """
    if alert_id is None:
        alert_id = f"test-alert-{int(time.time())}"
    
    return {
        "alertsAmount": alerts_amount,
        "dofM": dof_m,
        "classId": class_id,
        "severity": severity,
        "alertIds": [alert_id]
    }


def get_alerts_by_time_range(
    config_manager,
    start_time: datetime,
    end_time: datetime,
    base_url: Optional[str] = None,
    site_id: Optional[str] = None,
    session: Optional[requests.Session] = None
) -> List[Dict[str, Any]]:
    """
    Get alerts created within a time range.
    
    Args:
        config_manager: Configuration manager instance
        start_time: Start time (datetime object)
        end_time: End time (datetime object)
        base_url: Optional base URL override
        site_id: Optional site ID override
        session: Optional authenticated session
    
    Returns:
        List of alert dictionaries
    """
    # Get configuration
    if not base_url:
        api_config = config_manager.get("focus_server", {})
        base_url = api_config.get("frontend_api_url", "https://10.10.10.100/prisma/api/")
    
    if not site_id:
        site_id = config_manager.get("site_id", "prisma-210-1000")
    
    # Clean up base URL if needed
    if "/internal/sites/" in base_url:
        base_url = base_url.split("/internal/sites/")[0]
    if not base_url.endswith("/"):
        base_url += "/"
    
    # Authenticate if no session provided
    if session is None:
        session = authenticate_session(base_url)
    
    # Convert datetime to ISO format strings
    start_time_str = start_time.isoformat()
    end_time_str = end_time.isoformat()
    
    # Get alerts
    alerts_url = base_url + f"{site_id}/api/alert"
    params = {
        "startTime": start_time_str,
        "endTime": end_time_str,
        "getAlertCount": False
    }
    
    logger.debug(f"Fetching alerts from {alerts_url} with params: {params}")
    
    response = session.get(alerts_url, params=params, timeout=30)
    response.raise_for_status()
    
    alerts_data = response.json()
    
    # Handle different response formats
    if isinstance(alerts_data, list):
        alerts = alerts_data
    elif isinstance(alerts_data, dict) and "alerts" in alerts_data:
        alerts = alerts_data["alerts"]
    elif isinstance(alerts_data, dict) and "data" in alerts_data:
        alerts = alerts_data["data"]
    else:
        alerts = []
    
    logger.info(f"Found {len(alerts)} alerts in time range {start_time_str} to {end_time_str}")
    return alerts


def delete_alerts(
    config_manager,
    alert_ids: List[str],
    base_url: Optional[str] = None,
    site_id: Optional[str] = None,
    session: Optional[requests.Session] = None
) -> Optional[requests.Response]:
    """
    Delete alerts by their IDs.
    
    Args:
        config_manager: Configuration manager instance
        alert_ids: List of alert IDs to delete
        base_url: Optional base URL override
        site_id: Optional site ID override
        session: Optional authenticated session
    
    Returns:
        requests.Response: HTTP response from the API, or None if no alerts to delete
    
    Raises:
        requests.HTTPError: If the request fails
    """
    if not alert_ids:
        logger.debug("No alert IDs provided, skipping deletion")
        return None
    
    # Get configuration
    if not base_url:
        api_config = config_manager.get("focus_server", {})
        base_url = api_config.get("frontend_api_url", "https://10.10.10.100/prisma/api/")
    
    if not site_id:
        site_id = config_manager.get("site_id", "prisma-210-1000")
    
    # Clean up base URL if needed
    if "/internal/sites/" in base_url:
        base_url = base_url.split("/internal/sites/")[0]
    if not base_url.endswith("/"):
        base_url += "/"
    
    # Authenticate if no session provided
    if session is None:
        session = authenticate_session(base_url)
    
    # Delete alerts
    delete_url = base_url + f"{site_id}/api/alert/delete"
    payload = {"alertIds": alert_ids}
    
    logger.info(f"Deleting {len(alert_ids)} alerts: {alert_ids[:5]}{'...' if len(alert_ids) > 5 else ''}")
    
    response = session.delete(delete_url, json=payload, timeout=30)
    response.raise_for_status()
    
    logger.info(f"Successfully deleted {len(alert_ids)} alerts")
    return response


def cleanup_test_alerts(
    config_manager,
    start_time: datetime,
    end_time: Optional[datetime] = None,
    base_url: Optional[str] = None,
    site_id: Optional[str] = None,
    session: Optional[requests.Session] = None
) -> int:
    """
    Cleanup all alerts created during test execution.
    
    This function:
    1. Fetches all alerts created between start_time and end_time
    2. Deletes them using the DELETE API endpoint
    
    Args:
        config_manager: Configuration manager instance
        start_time: Start time of test execution
        end_time: End time of test execution (defaults to now)
        base_url: Optional base URL override
        site_id: Optional site ID override
        session: Optional authenticated session
    
    Returns:
        Number of alerts deleted
    """
    if end_time is None:
        end_time = datetime.now()
    
    try:
        # Get alerts created during test execution
        alerts = get_alerts_by_time_range(
            config_manager=config_manager,
            start_time=start_time,
            end_time=end_time,
            base_url=base_url,
            site_id=site_id,
            session=session
        )
        
        if not alerts:
            logger.info("No alerts found to cleanup")
            return 0
        
        # Extract alert IDs
        alert_ids = []
        for alert in alerts:
            # Handle different alert formats
            if isinstance(alert, dict):
                if "id" in alert:
                    alert_ids.append(str(alert["id"]))
                elif "alertId" in alert:
                    alert_ids.append(str(alert["alertId"]))
                elif "_id" in alert:
                    alert_ids.append(str(alert["_id"]))
        
        if not alert_ids:
            logger.warning(f"Found {len(alerts)} alerts but could not extract IDs")
            return 0
        
        # Delete alerts in batches (to avoid URL length issues)
        batch_size = 100
        deleted_count = 0
        
        for i in range(0, len(alert_ids), batch_size):
            batch = alert_ids[i:i + batch_size]
            try:
                delete_alerts(
                    config_manager=config_manager,
                    alert_ids=batch,
                    base_url=base_url,
                    site_id=site_id,
                    session=session
                )
                deleted_count += len(batch)
            except Exception as e:
                logger.error(f"Failed to delete alert batch {i//batch_size + 1}: {e}")
        
        logger.info(f"Cleanup completed: {deleted_count}/{len(alert_ids)} alerts deleted")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Failed to cleanup test alerts: {e}")
        return 0

