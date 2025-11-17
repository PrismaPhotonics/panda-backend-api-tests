"""
Token Manager for Prisma API Authentication
===========================================

Automated token management for Prisma API authentication.
Handles token acquisition, storage, validation, and automatic renewal.

Author: QA Automation Architect
Date: 2025-11-06
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import base64
import requests
import urllib3
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class TokenManager:
    """
    Manages authentication tokens for Prisma API.
    
    Features:
    - Automatic token acquisition via login
    - Token storage in local file (encrypted or plain)
    - Token expiration checking
    - Automatic token renewal
    - Support for multiple environments
    """
    
    def __init__(
        self,
        base_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token_file: Optional[str] = None,
        verify_ssl: bool = False,
        token_ttl_seconds: int = 300  # Default 5 minutes
    ):
        """
        Initialize Token Manager.
        
        Args:
            base_url: Base URL of the API server
            username: Username for authentication
            password: Password for authentication
            token_file: Path to token storage file (default: .tokens/{env}.json)
            verify_ssl: Whether to verify SSL certificates
            token_ttl_seconds: Token TTL in seconds (default: 300 = 5 minutes)
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.token_ttl_seconds = token_ttl_seconds
        
        # Set token file path
        if token_file:
            self.token_file = Path(token_file)
        else:
            # Default: .tokens directory in project root
            project_root = Path(__file__).parent.parent.parent
            tokens_dir = project_root / '.tokens'
            tokens_dir.mkdir(exist_ok=True)
            # Extract environment from base_url or use 'default'
            env_name = 'default'
            if '10.10.10.100' in base_url:
                env_name = 'staging'
            elif '10.10.100.100' in base_url:
                env_name = 'production'
            self.token_file = tokens_dir / f'{env_name}_token.json'
        
        # Create session for login requests with connection pool configuration
        self.session = requests.Session()
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        # Configure connection pool for concurrent requests
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=50,   # Connection pool size for token requests
            pool_maxsize=50        # Max connections per pool
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.verify = verify_ssl
        
        logger.info(f"Token Manager initialized for {self.base_url}")
        logger.info(f"Token file: {self.token_file}")
    
    def _decode_jwt_payload(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode JWT token payload (without verification).
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload dictionary or None if invalid
        """
        try:
            # JWT format: header.payload.signature
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            # Decode payload (second part)
            payload_b64 = parts[1]
            # Add padding if needed
            padding = 4 - len(payload_b64) % 4
            if padding != 4:
                payload_b64 += '=' * padding
            
            payload_bytes = base64.urlsafe_b64decode(payload_b64)
            payload = json.loads(payload_bytes.decode('utf-8'))
            return payload
        except Exception as e:
            logger.debug(f"Failed to decode JWT: {e}")
            return None
    
    def _is_token_expired(self, token: str) -> bool:
        """
        Check if JWT token is expired.
        
        Args:
            token: JWT token string
            
        Returns:
            True if expired or invalid, False if valid
        """
        payload = self._decode_jwt_payload(token)
        if not payload:
            return True
        
        exp = payload.get('exp')
        if not exp:
            # No expiration claim - assume valid
            return False
        
        # Check if expired (with 30 second buffer)
        current_time = int(time.time())
        return exp < (current_time + 30)
    
    def _load_token_from_file(self) -> Optional[str]:
        """
        Load token from storage file.
        
        Returns:
            Token string if found and valid, None otherwise
        """
        if not self.token_file.exists():
            logger.debug(f"Token file not found: {self.token_file}")
            return None
        
        try:
            with open(self.token_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            token = data.get('token')
            if not token:
                logger.debug("No token in file")
                return None
            
            # Check expiration
            if self._is_token_expired(token):
                logger.info("Token in file is expired")
                return None
            
            logger.info("Loaded valid token from file")
            return token
            
        except Exception as e:
            logger.warning(f"Failed to load token from file: {e}")
            return None
    
    def _save_token_to_file(self, token: str):
        """
        Save token to storage file.
        
        Args:
            token: Token string to save
        """
        try:
            # Decode token to get expiration info
            payload = self._decode_jwt_payload(token)
            exp_timestamp = payload.get('exp') if payload else None
            exp_datetime = datetime.fromtimestamp(exp_timestamp) if exp_timestamp else None
            
            data = {
                'token': token,
                'acquired_at': datetime.now().isoformat(),
                'expires_at': exp_datetime.isoformat() if exp_datetime else None,
                'base_url': self.base_url,
                'username': self.username  # Store username for reference (not password!)
            }
            
            # Ensure directory exists
            self.token_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.token_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Token saved to {self.token_file}")
            
        except Exception as e:
            logger.error(f"Failed to save token to file: {e}")
    
    def _acquire_token(self) -> Optional[str]:
        """
        Acquire new token via login endpoint.
        
        Returns:
            Token string if successful, None otherwise
        """
        if not self.username or not self.password:
            logger.warning("No credentials provided for token acquisition")
            return None
        
        logger.info("=" * 80)
        logger.info("Acquiring new token via login")
        logger.info("=" * 80)
        
        # Try different login endpoints (order matters - try most specific first)
        login_endpoints = []
        
        # Add /prisma/api/auth/login first (this is the correct endpoint!)
        if '/prisma/api' in self.base_url:
            login_endpoints.append(f"{self.base_url}/auth/login")
        else:
            login_endpoints.append(f"{self.base_url}/prisma/api/auth/login")
        
        # Add other possible endpoints as fallback
        login_endpoints.extend([
            f"{self.base_url}/auth/login",
            f"{self.base_url}/api/auth/login",
            f"{self.base_url.rstrip('/prisma/api')}/auth/login",
        ])
        
        for login_url in login_endpoints:
            try:
                logger.info(f"Trying login endpoint: {login_url}")
                
                # Try OAuth2PasswordRequestForm format (application/x-www-form-urlencoded)
                response = self.session.post(
                    login_url,
                    data={
                        'username': self.username,
                        'password': self.password
                    },
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    timeout=10,
                    allow_redirects=True
                )
                
                # Check for success status codes (200, 201)
                if response.status_code in [200, 201]:
                    # Check for cookie first (this is how Prisma API works)
                    if 'access-token' in response.cookies:
                        token = response.cookies['access-token']
                        logger.info("[OK] Token acquired successfully (Cookie)")
                        return token
                    
                    # Check for access token in response body (fallback)
                    try:
                        response_data = response.json()
                        if 'access_token' in response_data:
                            token = response_data['access_token']
                            logger.info("[OK] Token acquired successfully (Bearer token)")
                            return token
                    except (ValueError, KeyError):
                        pass
                
                # Try JSON format
                response = self.session.post(
                    login_url,
                    json={
                        'username': self.username,
                        'password': self.password
                    },
                    timeout=10,
                    allow_redirects=True
                )
                
                # Check for success status codes (200, 201)
                if response.status_code in [200, 201]:
                    # Check for cookie first (this is how Prisma API works)
                    if 'access-token' in response.cookies:
                        token = response.cookies['access-token']
                        logger.info("[OK] Token acquired successfully (Cookie from JSON)")
                        return token
                    
                    # Check for access token in response body (fallback)
                    try:
                        response_data = response.json()
                        if 'access_token' in response_data:
                            token = response_data['access_token']
                            logger.info("[OK] Token acquired successfully (Bearer token from JSON)")
                            return token
                    except (ValueError, KeyError):
                        pass
                
            except requests.exceptions.RequestException as e:
                logger.debug(f"Login endpoint {login_url} failed: {e}")
                continue
        
        logger.error("[ERROR] Failed to acquire token - all login endpoints failed")
        return None
    
    def get_token(self, force_refresh: bool = False) -> Optional[str]:
        """
        Get valid token, loading from cache or acquiring new one.
        
        Args:
            force_refresh: If True, force token refresh even if cached token is valid
            
        Returns:
            Valid token string or None if failed
        """
        # Try to load from file first (unless forcing refresh)
        if not force_refresh:
            token = self._load_token_from_file()
            if token:
                return token
        
        # Acquire new token
        token = self._acquire_token()
        if token:
            # Save to file for future use
            self._save_token_to_file(token)
            return token
        
        return None
    
    def clear_token(self):
        """Clear stored token from file."""
        if self.token_file.exists():
            try:
                self.token_file.unlink()
                logger.info(f"Token file deleted: {self.token_file}")
            except Exception as e:
                logger.error(f"Failed to delete token file: {e}")


if __name__ == '__main__':
    # Test script
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example usage
    base_url = sys.argv[1] if len(sys.argv) > 1 else "https://10.10.10.100/prisma/api"
    username = os.getenv('PRISMA_API_USERNAME')
    password = os.getenv('PRISMA_API_PASSWORD')
    
    if not username or not password:
        print("Error: PRISMA_API_USERNAME and PRISMA_API_PASSWORD environment variables required")
        sys.exit(1)
    
    manager = TokenManager(
        base_url=base_url,
        username=username,
        password=password,
        verify_ssl=False
    )
    
    token = manager.get_token()
    if token:
        print(f"\n[OK] Token acquired: {token[:50]}...")
    else:
        print("\n[ERROR] Failed to acquire token")
        sys.exit(1)


