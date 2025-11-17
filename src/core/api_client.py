"""
Base API Client
===============

Base API client for the Focus Server automation framework.
"""

import requests
import time
import logging
import json
from typing import Dict, Any, Optional, Union
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from src.core.exceptions import APIError, NetworkError, TimeoutError
from src.core.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError


class BaseAPIClient:
    """
    Base API client with common functionality for all API clients.
    
    Provides:
    - HTTP session management
    - Retry logic
    - Error handling
    - Logging
    - Response validation
    """
    
    def __init__(self, base_url: str, timeout: int = 60, max_retries: int = 3, verify_ssl: bool = False):
        """
        Initialize the base API client.
        
        Args:
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            verify_ssl: Whether to verify SSL certificates (default: False for self-signed certs)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Suppress SSL warnings if verification is disabled
        if not self.verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Create session with retry strategy
        self.session = requests.Session()
        self._setup_retry_strategy()
        self._setup_headers()
        
        # Initialize circuit breaker to prevent cascading failures
        # Opens after 5 consecutive failures, stays open for 60 seconds
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60,
            expected_exception=(requests.exceptions.ConnectionError, requests.exceptions.Timeout)
        )
        
        self.logger.info(f"API client initialized for {self.base_url} (SSL verify: {self.verify_ssl})")
    
    def _setup_retry_strategy(self):
        """
        Set up retry strategy for HTTP requests with exponential backoff.
        
        Configuration:
        - Exponential backoff: 1s, 2s, 4s (backoff_factor=2.0)
        - Retry on connection errors (connect=3)
        - Retry on read errors (read=3)
        - Retry on HTTP status codes: 429, 500, 502, 503, 504
        """
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=2.0,  # Exponential backoff: 1s, 2s, 4s
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
            connect=3,  # Retry on connection errors
            read=3      # Retry on read errors
        )
        
        # Increased connection pool size for concurrent requests
        # pool_connections: number of connection pools to cache (one per host)
        # pool_maxsize: maximum number of connections to save in the pool per host
        # Set to 200 to support 200+ concurrent requests
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=200,  # Increased from 50 to support 200+ concurrent requests
            pool_maxsize=200       # Increased from 50 to support 200+ concurrent requests
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _setup_headers(self):
        """Set up default headers for requests."""
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Focus-Server-Automation/1.0.0"
        })
    
    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL from endpoint.
        
        Args:
            endpoint: API endpoint (with or without leading slash)
            
        Returns:
            Full URL
        """
        endpoint = endpoint.lstrip('/')
        return f"{self.base_url}/{endpoint}"
    
    def _send_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Send HTTP request with error handling and detailed logging.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
            
        Raises:
            APIError: If request fails
            NetworkError: If network error occurs
            TimeoutError: If request times out
        """
        url = self._build_url(endpoint)
        
        # Set timeout
        kwargs.setdefault('timeout', self.timeout)
        
        # Set SSL verification
        kwargs.setdefault('verify', self.verify_ssl)
        
        # Log detailed request information
        self.logger.info(f"{'='*80}")
        self.logger.info(f">> {method} {url}")
        
        # Log request headers
        if 'headers' in kwargs:
            self.logger.debug("Request Headers:")
            for key, value in kwargs['headers'].items():
                self.logger.debug(f"  {key}: {value}")
        
        # Log request body (JSON)
        if 'json' in kwargs:
            self.logger.info("Request Body (JSON):")
            try:
                pretty_json = json.dumps(kwargs['json'], indent=2)
                for line in pretty_json.split('\n'):
                    self.logger.info(f"  {line}")
            except Exception:
                self.logger.info(f"  {kwargs['json']}")
        
        # Log query parameters
        if 'params' in kwargs:
            self.logger.debug(f"Query Parameters: {kwargs['params']}")
        
        # Start timing
        start_time = time.time()
        
        # Execute request with circuit breaker protection
        try:
            response = self.circuit_breaker.call(
                self.session.request,
                method, url, **kwargs
            )
            elapsed = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Log response details
            self.logger.info(f"<< {response.status_code} {response.reason} ({elapsed:.2f}ms)")
            
            # Log response headers (only important ones)
            self.logger.debug("Response Headers:")
            important_headers = ['content-type', 'content-length', 'date', 'server']
            for key in important_headers:
                if key in response.headers:
                    self.logger.debug(f"  {key}: {response.headers[key]}")
            
            # Log response body
            if response.text:
                try:
                    # Try to parse as JSON for pretty printing
                    response_json = response.json()
                    self.logger.info("Response Body (JSON):")
                    pretty_json = json.dumps(response_json, indent=2)
                    # Limit output to first 50 lines for very large responses
                    lines = pretty_json.split('\n')
                    for i, line in enumerate(lines[:50]):
                        self.logger.info(f"  {line}")
                    if len(lines) > 50:
                        self.logger.info(f"  ... ({len(lines) - 50} more lines)")
                except json.JSONDecodeError:
                    # Not JSON, log as text (truncated)
                    self.logger.info(f"Response Body (Text): {response.text[:500]}")
                    if len(response.text) > 500:
                        self.logger.info("  ... (truncated)")
            
            self.logger.info(f"{'='*80}")
            
            # Handle HTTP errors
            if response.status_code >= 400:
                # Check if 503 is due to "waiting for fiber" - don't retry in that case
                if response.status_code == 503:
                    try:
                        error_data = response.json()
                        error_message = str(error_data.get('error', '') or error_data.get('message', '')).lower()
                        # Check if error indicates "waiting for fiber"
                        if 'waiting for fiber' in error_message or 'waiting_for_fiber' in error_message:
                            self.logger.warning("503 error due to 'waiting for fiber' - skipping retry")
                            # Raise error immediately without retry
                            raise APIError(
                                message="System is waiting for fiber - cannot configure",
                                status_code=503,
                                response_body=error_data
                            )
                    except (ValueError, KeyError, json.JSONDecodeError):
                        # If we can't parse the error, continue with normal handling
                        pass
                
                self._handle_http_error(response, url)
            
            return response
            
        except requests.exceptions.Timeout as e:
            elapsed = (time.time() - start_time) * 1000
            self.logger.error(f"[TIMEOUT] Request timeout after {elapsed:.2f}ms for {method} {url}: {e}")
            self.logger.error(f"{'='*80}")
            raise TimeoutError(f"Request timed out after {self.timeout} seconds", self.timeout) from e
            
        except CircuitBreakerOpenError as e:
            elapsed = (time.time() - start_time) * 1000
            self.logger.error(f"[CIRCUIT_BREAKER] Circuit breaker is OPEN after {elapsed:.2f}ms for {method} {url}: {e}")
            self.logger.error(f"{'='*80}")
            raise NetworkError(f"Circuit breaker is open - server appears down: {e}") from e
        except requests.exceptions.ConnectionError as e:
            elapsed = (time.time() - start_time) * 1000
            self.logger.error(f"[CONNECTION_ERROR] Connection error after {elapsed:.2f}ms for {method} {url}: {e}")
            self.logger.error(f"{'='*80}")
            raise NetworkError(f"Connection failed: {e}") from e
            
        except requests.exceptions.RequestException as e:
            elapsed = (time.time() - start_time) * 1000
            self.logger.error(f"[REQUEST_ERROR] Request error after {elapsed:.2f}ms for {method} {url}: {e}")
            self.logger.error(f"{'='*80}")
            raise APIError(f"Request failed: {e}") from e
    
    def _handle_http_error(self, response: requests.Response, url: str):
        """
        Handle HTTP error responses.
        
        Args:
            response: HTTP response object
            url: Request URL
            
        Raises:
            APIError: With appropriate error message
        """
        status_code = response.status_code
        
        try:
            error_data = response.json()
            error_message = error_data.get('error', error_data.get('message', 'Unknown error'))
            # Log the full response for debugging
            self.logger.error(f"Full error response: {error_data}")
        except (ValueError, KeyError):
            error_message = response.text or f"HTTP {status_code} error"
            self.logger.error(f"Raw error response: {response.text}")
        
        self.logger.error(f"HTTP {status_code} error for {url}: {error_message}")
        
        raise APIError(
            message=f"API call failed: {error_message}",
            status_code=status_code,
            response_body=response.text
        )
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Send GET request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
        """
        return self._send_request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Send POST request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
        """
        return self._send_request("POST", endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Send PUT request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
        """
        return self._send_request("PUT", endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Send DELETE request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
        """
        return self._send_request("DELETE", endpoint, **kwargs)
    
    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Send PATCH request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
        """
        return self._send_request("PATCH", endpoint, **kwargs)
    
    def health_check(self) -> bool:
        """
        Perform health check on the API.
        
        Returns:
            True if API is healthy
        """
        try:
            response = self.get("/health", timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    def close(self):
        """Close the HTTP session."""
        if self.session:
            self.session.close()
            self.logger.debug("HTTP session closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
