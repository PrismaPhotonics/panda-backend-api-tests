"""
Base API Client
===============

Base API client for the Focus Server automation framework.
"""

import requests
import time
import logging
from typing import Dict, Any, Optional, Union
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from src.core.exceptions import APIError, NetworkError, TimeoutError


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
    
    def __init__(self, base_url: str, timeout: int = 60, max_retries: int = 3):
        """
        Initialize the base API client.
        
        Args:
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Create session with retry strategy
        self.session = requests.Session()
        self._setup_retry_strategy()
        self._setup_headers()
        
        self.logger.info(f"API client initialized for {self.base_url}")
    
    def _setup_retry_strategy(self):
        """Set up retry strategy for HTTP requests."""
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
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
        Send HTTP request with error handling.
        
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
        
        # Log request
        self.logger.debug(f"Sending {method} request to {url}")
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Log response
            self.logger.debug(f"Received {response.status_code} response from {url}")
            
            # Handle HTTP errors
            if response.status_code >= 400:
                self._handle_http_error(response, url)
            
            return response
            
        except requests.exceptions.Timeout as e:
            self.logger.error(f"Request timeout for {method} {url}: {e}")
            raise TimeoutError(f"Request timed out after {self.timeout} seconds", self.timeout) from e
            
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error for {method} {url}: {e}")
            raise NetworkError(f"Connection failed: {e}") from e
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error for {method} {url}: {e}")
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
        except (ValueError, KeyError):
            error_message = response.text or f"HTTP {status_code} error"
        
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
