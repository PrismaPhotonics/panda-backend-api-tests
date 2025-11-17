"""
Circuit Breaker Pattern for API calls.

Prevents cascading failures by stopping requests when server is down.
This helps avoid wasting time on requests that are likely to fail.

Author: QA Automation Team
Date: November 7, 2025
"""

import time
import logging
from typing import Callable, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """
    Circuit breaker implementation to prevent cascading failures.
    
    States:
    - CLOSED: Normal operation - requests are allowed
    - OPEN: Circuit is open - requests fail immediately without trying
    - HALF_OPEN: Testing if server recovered - allows one request to test
    
    The circuit breaker opens after a threshold of failures and stays open
    for a timeout period before moving to HALF_OPEN state.
    
    Example:
        ```python
        breaker = CircuitBreaker(failure_threshold=5, timeout=60)
        
        try:
            result = breaker.call(api_client.get, "/endpoint")
        except CircuitBreakerOpenError:
            logger.warning("Circuit breaker is open - server appears down")
        ```
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of consecutive failures before opening circuit
            timeout: Time in seconds before trying again (half-open state)
            expected_exception: Exception type that triggers circuit breaker
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
        logger.debug(
            f"Circuit breaker initialized: "
            f"threshold={failure_threshold}, timeout={timeout}s"
        )
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Original exception if function fails
        """
        # Check if circuit should transition from OPEN to HALF_OPEN
        if self.state == "OPEN":
            if self.last_failure_time and (time.time() - self.last_failure_time) > self.timeout:
                self.state = "HALF_OPEN"
                logger.info(
                    f"Circuit breaker: Moving to HALF_OPEN state "
                    f"(timeout {self.timeout}s expired)"
                )
            else:
                remaining_time = self.timeout - (time.time() - self.last_failure_time) if self.last_failure_time else self.timeout
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN. "
                    f"Will retry after {remaining_time:.0f}s. "
                    f"Failure count: {self.failure_count}/{self.failure_threshold}"
                )
        
        # Execute function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call."""
        if self.state == "HALF_OPEN":
            # Server recovered - close circuit
            self.state = "CLOSED"
            self.failure_count = 0
            logger.info("Circuit breaker: Moving to CLOSED state (server recovered)")
        elif self.state == "CLOSED":
            # Reset failure count on success
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(
                f"Circuit breaker: OPENED after {self.failure_count} consecutive failures. "
                f"Will retry after {self.timeout}s"
            )
        else:
            logger.debug(
                f"Circuit breaker: Failure count {self.failure_count}/{self.failure_threshold}"
            )
    
    def reset(self):
        """Manually reset circuit breaker to CLOSED state."""
        self.state = "CLOSED"
        self.failure_count = 0
        self.last_failure_time = None
        logger.info("Circuit breaker: Manually reset to CLOSED state")
    
    def get_state(self) -> str:
        """Get current circuit breaker state."""
        return self.state
    
    def get_failure_count(self) -> int:
        """Get current failure count."""
        return self.failure_count

