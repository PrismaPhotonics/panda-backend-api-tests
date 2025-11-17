"""
API Endpoints Validation Script
================================

Automated script to validate that all API endpoints documented in Swagger spec
are actually available and working in the target environment.

This script:
1. Reads the Swagger spec JSON file
2. Extracts all endpoints with their HTTP methods
3. Tests each endpoint against the target environment
4. Generates a detailed report with recommendations

Author: QA Automation Architect
Date: 2025-11-06
"""

import json
import logging
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager
from src.utils.token_manager import TokenManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api_endpoints_validation.log')
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class EndpointResult:
    """Result of endpoint validation."""
    method: str
    path: str
    operation_id: str
    status: str  # 'available', 'not_found', 'error', 'auth_required', 'deprecated'
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    requires_auth: bool = False
    requires_params: bool = False
    is_deprecated: bool = False


@dataclass
class ValidationReport:
    """Complete validation report."""
    total_endpoints: int = 0
    available_endpoints: int = 0
    not_found_endpoints: int = 0
    error_endpoints: int = 0
    auth_required_endpoints: int = 0
    deprecated_endpoints: int = 0
    results: List[EndpointResult] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class APIEndpointValidator:
    """
    Validates API endpoints against actual server.
    
    This class reads Swagger spec, extracts endpoints, and tests them
    against the configured environment.
    """
    
    def __init__(self, swagger_spec_path: str, base_url: str, site_id: str, verify_ssl: bool = False,
                 username: Optional[str] = None, password: Optional[str] = None, access_token: Optional[str] = None):
        """
        Initialize the validator.
        
        Args:
            swagger_spec_path: Path to Swagger spec JSON file
            base_url: Base URL of the API server
            site_id: Site ID to use in path parameters
            verify_ssl: Whether to verify SSL certificates
            username: Username for authentication (optional)
            password: Password for authentication (optional)
            access_token: Access token/cookie value (optional, if provided, login will be skipped)
        """
        self.swagger_spec_path = Path(swagger_spec_path)
        self.base_url = base_url.rstrip('/')
        self.site_id = site_id
        self.verify_ssl = verify_ssl
        self.username = username
        self.password = password
        self.access_token = access_token
        self.is_authenticated = False
        
        # Create session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set SSL verification
        self.session.verify = verify_ssl
        
        # Set default headers
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "API-Endpoint-Validator/1.0.0"
        })
        
        logger.info(f"Initialized validator for {self.base_url}")
        logger.info(f"Swagger spec: {self.swagger_spec_path}")
        logger.info(f"Site ID: {self.site_id}")
        
        # Attempt authentication if credentials provided
        if access_token:
            # Check if it's a JWT token (starts with eyJ)
            if access_token.startswith('eyJ'):
                # Try both Bearer token and cookie (API might use either)
                self._set_bearer_token(access_token)
                self._set_access_token(access_token)
            else:
                self._set_access_token(access_token)
        elif username and password:
            self.authenticate()
    
    def load_swagger_spec(self) -> Dict[str, Any]:
        """Load and parse Swagger spec JSON file."""
        logger.info(f"Loading Swagger spec from {self.swagger_spec_path}")
        
        if not self.swagger_spec_path.exists():
            raise FileNotFoundError(f"Swagger spec not found: {self.swagger_spec_path}")
        
        with open(self.swagger_spec_path, 'r', encoding='utf-8') as f:
            spec = json.load(f)
        
        logger.info(f"Loaded Swagger spec version {spec.get('info', {}).get('version', 'unknown')}")
        return spec
    
    def authenticate(self) -> bool:
        """
        Authenticate with the API using username/password.
        
        Tries multiple authentication endpoints:
        1. POST /auth/login (common pattern)
        2. POST /api/auth/login
        3. POST /prisma/api/auth/login
        4. Cookie-based authentication via Microsoft OAuth flow
        
        Returns:
            True if authentication successful, False otherwise
        """
        if self.is_authenticated:
            logger.info("Already authenticated")
            return True
        
        if not self.username or not self.password:
            logger.warning("No credentials provided for authentication")
            return False
        
        logger.info("=" * 80)
        logger.info("Attempting authentication")
        logger.info("=" * 80)
        
        # Try different login endpoints
        login_endpoints = [
            f"{self.base_url}/auth/login",
            f"{self.base_url}/api/auth/login",
            f"{self.base_url.rstrip('/prisma/api')}/auth/login",
        ]
        
        # Also try if base_url doesn't include /prisma/api
        if '/prisma/api' not in self.base_url:
            login_endpoints.insert(0, f"{self.base_url}/prisma/api/auth/login")
        
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
                
                if response.status_code == 200:
                    # Check for access token in response
                    try:
                        response_data = response.json()
                        if 'access_token' in response_data:
                            token = response_data['access_token']
                            self._set_bearer_token(token)
                            logger.info("[OK] Authentication successful (Bearer token)")
                            return True
                    except (ValueError, KeyError):
                        pass
                    
                    # Check for cookie
                    if 'access-token' in response.cookies:
                        token = response.cookies['access-token']
                        self._set_access_token(token)
                        logger.info("[OK] Authentication successful (Cookie)")
                        return True
                
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
                
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        if 'access_token' in response_data:
                            token = response_data['access_token']
                            self._set_bearer_token(token)
                            logger.info("[OK] Authentication successful (Bearer token from JSON)")
                            return True
                    except (ValueError, KeyError):
                        pass
                    
                    # Check for cookie
                    if 'access-token' in response.cookies:
                        token = response.cookies['access-token']
                        self._set_access_token(token)
                        logger.info("[OK] Authentication successful (Cookie from JSON)")
                        return True
                
            except requests.exceptions.RequestException as e:
                logger.debug(f"Login endpoint {login_url} failed: {e}")
                continue
        
        logger.warning("[WARN] Authentication failed - all login endpoints failed")
        logger.warning("Note: Some APIs may use cookie-based authentication via browser login")
        logger.warning("You may need to:")
        logger.warning("  1. Login via browser and copy the 'access-token' cookie")
        logger.warning("  2. Use --access-token option to provide the cookie value")
        logger.warning("  3. Or check API documentation for correct login endpoint")
        return False
    
    def _set_access_token(self, token: str):
        """Set access token as cookie."""
        # Extract domain from base_url if possible
        try:
            from urllib.parse import urlparse
            parsed = urlparse(self.base_url)
            domain = parsed.netloc.split(':')[0]  # Remove port if present
            self.session.cookies.set('access-token', token, domain=domain)
        except Exception:
            # Fallback: set cookie without domain
            self.session.cookies.set('access-token', token)
        self.is_authenticated = True
        logger.info("Access token cookie set")
    
    def _set_bearer_token(self, token: str):
        """Set Bearer token in Authorization header."""
        self.session.headers['Authorization'] = f'Bearer {token}'
        self.is_authenticated = True
        logger.info("Bearer token set in Authorization header")
    
    def extract_endpoints(self, spec: Dict[str, Any]) -> List[Tuple[str, str, Dict[str, Any]]]:
        """
        Extract all endpoints from Swagger spec.
        
        Filters out endpoints that require special permissions (403 Forbidden)
        and are not relevant for basic API validation.
        
        Returns:
            List of tuples: (method, path, operation_data)
        """
        # List of endpoints to exclude (require special permissions - 403 Forbidden)
        excluded_endpoints = [
            # DELETE endpoints (require delete permissions)
            ('DELETE', '/{siteId}/api/alert/delete'),
            ('DELETE', '/{siteId}/api/region/{id}'),
            
            # GET endpoints that require special permissions
            ('GET', '/{siteId}/api/role'),  # Requires update_users permission
            ('GET', '/{siteId}/api/user/get-all-users'),  # Requires user management permissions
            
            # POST endpoints (require write permissions)
            ('POST', '/sites/{siteId}/geo-channel-collections!generate'),
            ('POST', '/sites/{siteId}/geo-channel-collections!infer-from-fiber'),
            ('POST', '/users/{userId}!toggle-login'),
            ('POST', '/{siteId}/api/region/add'),
            ('POST', '/{siteId}/api/region/update'),
            ('POST', '/{siteId}/api/user/add-permission-to-role'),
            ('POST', '/{siteId}/api/user/delete'),
            ('POST', '/{siteId}/api/user/sign-up'),
            ('POST', '/{siteId}/api/user/update-other-user'),
            ('POST', '/{siteId}/api/user/validate-email'),
            ('POST', '/{siteId}/api/user/validate-username'),
            ('POST', '/users/{userId}!delete-external-identities'),
            ('POST', '/{siteId}/api/user/update'),
        ]
        
        endpoints = []
        paths = spec.get('paths', {})
        
        for path, methods in paths.items():
            for method, operation in methods.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                    method_upper = method.upper()
                    
                    # Check if this endpoint should be excluded
                    should_exclude = False
                    for excluded_method, excluded_path in excluded_endpoints:
                        if method_upper == excluded_method and path == excluded_path:
                            should_exclude = True
                            logger.debug(f"Excluding endpoint: {method_upper} {path} (requires special permissions)")
                            break
                    
                    if not should_exclude:
                        endpoints.append((method_upper, path, operation))
        
        logger.info(f"Extracted {len(endpoints)} endpoints from Swagger spec (excluded {len(excluded_endpoints)} endpoints that require special permissions)")
        return endpoints
    
    def build_full_url(self, path: str) -> str:
        """
        Build full URL from path template.
        
        Replaces path parameters with actual values:
        - {siteId} -> actual site_id
        - {userId} -> placeholder value
        - {id} -> placeholder value
        """
        # Replace path parameters
        url_path = path.replace('{siteId}', self.site_id)
        url_path = url_path.replace('{userId}', '1')  # Placeholder user ID
        url_path = url_path.replace('{id}', '1')  # Placeholder ID
        
        # Build full URL
        # base_url should already include /prisma/api (e.g., https://10.10.10.100/prisma/api)
        # Paths in Swagger spec are relative to /prisma/api
        
        if url_path.startswith('/'):
            # Path already starts with /, just append to base_url
            full_url = f"{self.base_url}{url_path}"
        else:
            # Path doesn't start with /, add it
            full_url = f"{self.base_url}/{url_path}"
        
        return full_url
    
    def validate_endpoint(self, method: str, path: str, operation: Dict[str, Any]) -> EndpointResult:
        """
        Validate a single endpoint.
        
        Args:
            method: HTTP method
            path: API path
            operation: Operation data from Swagger spec
            
        Returns:
            EndpointResult with validation status
        """
        operation_id = operation.get('operationId', 'unknown')
        is_deprecated = operation.get('deprecated', False)
        
        logger.info(f"Validating {method} {path} ({operation_id})")
        
        # Build URL
        full_url = self.build_full_url(path)
        
        # Check if endpoint requires authentication
        requires_auth = False
        security = operation.get('security', [])
        if security:
            requires_auth = True
        
        # Check if endpoint requires path parameters
        requires_params = '{' in path
        
        # Check if endpoint requires request body
        requires_body = 'requestBody' in operation
        
        # For GET/HEAD requests, try without body
        # For POST/PUT/PATCH/DELETE, skip if requires body (we can't test without proper data)
        if method in ['POST', 'PUT', 'PATCH', 'DELETE'] and requires_body:
            # Try with empty body or minimal body
            try:
                start_time = datetime.now()
                response = self.session.request(
                    method,
                    full_url,
                    json={} if requires_body else None,
                    timeout=10,
                    allow_redirects=False
                )
                elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
                
                status_code = response.status_code
                
                # Interpret status codes
                if status_code == 200 or status_code == 201:
                    status = 'available'
                elif status_code == 401 or status_code == 403:
                    status = 'auth_required'
                elif status_code == 404:
                    status = 'not_found'
                elif status_code == 400 or status_code == 422:
                    # 400/422 usually means endpoint exists but validation failed
                    status = 'available'
                elif status_code >= 500:
                    status = 'error'
                else:
                    status = 'available'  # Other 2xx/3xx codes indicate endpoint exists
                
                return EndpointResult(
                    method=method,
                    path=path,
                    operation_id=operation_id,
                    status=status,
                    status_code=status_code,
                    response_time_ms=elapsed_ms,
                    requires_auth=requires_auth,
                    requires_params=requires_params,
                    is_deprecated=is_deprecated
                )
                
            except requests.exceptions.Timeout:
                return EndpointResult(
                    method=method,
                    path=path,
                    operation_id=operation_id,
                    status='error',
                    error_message='Request timeout',
                    requires_auth=requires_auth,
                    requires_params=requires_params,
                    is_deprecated=is_deprecated
                )
            except requests.exceptions.ConnectionError as e:
                return EndpointResult(
                    method=method,
                    path=path,
                    operation_id=operation_id,
                    status='error',
                    error_message=f'Connection error: {str(e)}',
                    requires_auth=requires_auth,
                    requires_params=requires_params,
                    is_deprecated=is_deprecated
                )
            except Exception as e:
                return EndpointResult(
                    method=method,
                    path=path,
                    operation_id=operation_id,
                    status='error',
                    error_message=f'Unexpected error: {str(e)}',
                    requires_auth=requires_auth,
                    requires_params=requires_params,
                    is_deprecated=is_deprecated
                )
        else:
            # GET/HEAD request - simple check
            try:
                start_time = datetime.now()
                response = self.session.request(
                    method,
                    full_url,
                    timeout=10,
                    allow_redirects=False
                )
                elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
                
                status_code = response.status_code
                
                # Interpret status codes
                if status_code == 200 or status_code == 201:
                    status = 'available'
                elif status_code == 401 or status_code == 403:
                    status = 'auth_required'
                elif status_code == 404:
                    status = 'not_found'
                elif status_code >= 500:
                    status = 'error'
                else:
                    status = 'available'
                
                return EndpointResult(
                    method=method,
                    path=path,
                    operation_id=operation_id,
                    status=status,
                    status_code=status_code,
                    response_time_ms=elapsed_ms,
                    requires_auth=requires_auth,
                    requires_params=requires_params,
                    is_deprecated=is_deprecated
                )
                
            except requests.exceptions.Timeout:
                return EndpointResult(
                    method=method,
                    path=path,
                    operation_id=operation_id,
                    status='error',
                    error_message='Request timeout',
                    requires_auth=requires_auth,
                    requires_params=requires_params,
                    is_deprecated=is_deprecated
                )
            except requests.exceptions.ConnectionError as e:
                return EndpointResult(
                    method=method,
                    path=path,
                    operation_id=operation_id,
                    status='error',
                    error_message=f'Connection error: {str(e)}',
                    requires_auth=requires_auth,
                    requires_params=requires_params,
                    is_deprecated=is_deprecated
                )
            except Exception as e:
                return EndpointResult(
                    method=method,
                    path=path,
                    operation_id=operation_id,
                    status='error',
                    error_message=f'Unexpected error: {str(e)}',
                    requires_auth=requires_auth,
                    requires_params=requires_params,
                    is_deprecated=is_deprecated
                )
    
    def check_login_configuration(self) -> Optional[EndpointResult]:
        """
        Check /login-configuration endpoint first (prerequisite for other endpoints).
        
        IMPORTANT: This endpoint MUST be called before any other API requests.
        It initializes the session and prepares the API for subsequent calls.
        
        Returns:
            EndpointResult if found in spec, None otherwise
        """
        logger.info("=" * 80)
        logger.info("PREREQUISITE: Checking /login-configuration endpoint FIRST")
        logger.info("This endpoint MUST run before any other API requests")
        logger.info("=" * 80)
        
        spec = self.load_swagger_spec()
        paths = spec.get('paths', {})
        
        if '/login-configuration' in paths:
            login_config = paths['/login-configuration']
            if 'get' in login_config:
                operation = login_config['get']
                result = self.validate_endpoint('GET', '/login-configuration', operation)
                
                if result.status == 'available':
                    logger.info("[OK] /login-configuration is available - API is accessible")
                    # Try to get login configuration details
                    try:
                        full_url = self.build_full_url('/login-configuration')
                        response = self.session.get(full_url, timeout=10)
                        if response.status_code == 200:
                            config_data = response.json()
                            logger.info(f"Login configuration: {json.dumps(config_data, indent=2)}")
                    except Exception as e:
                        logger.warning(f"Could not fetch login configuration details: {e}")
                else:
                    logger.warning(f"[WARN] /login-configuration returned status: {result.status}")
                    if result.status_code:
                        logger.warning(f"   Status code: {result.status_code}")
                    if result.error_message:
                        logger.warning(f"   Error: {result.error_message}")
                
                return result
        
        logger.warning("[WARN] /login-configuration endpoint not found in Swagger spec")
        return None
    
    def validate_all(self) -> ValidationReport:
        """
        Validate all endpoints from Swagger spec.
        
        Returns:
            ValidationReport with all results
        """
        logger.info("=" * 80)
        logger.info("Starting API Endpoints Validation")
        logger.info("=" * 80)
        
        # CRITICAL: Step 1 - Check /login-configuration FIRST (prerequisite)
        # This endpoint MUST run before any other API requests
        logger.info("")
        logger.info("=" * 80)
        logger.info("CRITICAL STEP: Running /login-configuration FIRST")
        logger.info("This is a prerequisite - all other API calls depend on this")
        logger.info("=" * 80)
        login_config_result = self.check_login_configuration()
        
        # Verify /login-configuration succeeded before proceeding
        if login_config_result and login_config_result.status != 'available':
            logger.warning("=" * 80)
            logger.warning("WARNING: /login-configuration check failed!")
            logger.warning("Status: %s", login_config_result.status)
            logger.warning("Other API calls may fail without this prerequisite")
            logger.warning("=" * 80)
        elif login_config_result and login_config_result.status == 'available':
            logger.info("=" * 80)
            logger.info("[OK] /login-configuration prerequisite satisfied")
            logger.info("Proceeding with other API endpoint validations...")
            logger.info("=" * 80)
        
        # Load Swagger spec
        spec = self.load_swagger_spec()
        
        # Extract endpoints
        endpoints = self.extract_endpoints(spec)
        
        # Validate each endpoint
        report = ValidationReport(total_endpoints=len(endpoints))
        
        # Add login-configuration result if available
        if login_config_result:
            report.results.append(login_config_result)
            if login_config_result.status == 'available':
                report.available_endpoints += 1
            elif login_config_result.status == 'not_found':
                report.not_found_endpoints += 1
            elif login_config_result.status == 'error':
                report.error_endpoints += 1
            elif login_config_result.status == 'auth_required':
                report.auth_required_endpoints += 1
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("Step 2: Validating all other endpoints")
        logger.info("(After /login-configuration prerequisite)")
        logger.info("=" * 80)
        
        for method, path, operation in endpoints:
            # Skip /login-configuration as we already checked it
            if path == '/login-configuration':
                continue
                
            result = self.validate_endpoint(method, path, operation)
            report.results.append(result)
            
            # Update counters
            if result.status == 'available':
                report.available_endpoints += 1
            elif result.status == 'not_found':
                report.not_found_endpoints += 1
            elif result.status == 'error':
                report.error_endpoints += 1
            elif result.status == 'auth_required':
                report.auth_required_endpoints += 1
            
            if result.is_deprecated:
                report.deprecated_endpoints += 1
        
        # Generate recommendations
        report.recommendations = self._generate_recommendations(report, login_config_result)
        
        logger.info("=" * 80)
        logger.info("Validation Complete")
        logger.info("=" * 80)
        
        return report
    
    def _generate_recommendations(self, report: ValidationReport, login_config_result: Optional[EndpointResult] = None) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Check login-configuration status
        if login_config_result:
            if login_config_result.status == 'available':
                recommendations.append(
                    "[OK] /login-configuration endpoint is accessible - this is the prerequisite endpoint."
                )
            elif login_config_result.status == 'error':
                recommendations.append(
                    "[CRITICAL] /login-configuration endpoint failed. "
                    "This is a prerequisite endpoint - fix this first before testing other endpoints."
                )
            elif login_config_result.status == 'not_found':
                recommendations.append(
                    "[CRITICAL] /login-configuration endpoint not found (404). "
                    "This is a prerequisite endpoint - verify the API base URL is correct."
                )
            elif login_config_result.status == 'auth_required':
                recommendations.append(
                    "[WARN] /login-configuration requires authentication - this is unusual. "
                    "Verify if this endpoint should be public."
                )
        
        # Check for missing endpoints
        if report.not_found_endpoints > 0:
            recommendations.append(
                f"[WARN] Found {report.not_found_endpoints} endpoints that return 404. "
                "These endpoints may not be implemented or may have incorrect paths."
            )
        
        # Check for authentication issues
        if report.auth_required_endpoints > 0:
            recommendations.append(
                f"[INFO] Found {report.auth_required_endpoints} endpoints that require authentication. "
                "Consider adding authentication to the validator for complete testing. "
                "Note: Most endpoints require authentication after checking /login-configuration."
            )
        
        # Check for errors
        if report.error_endpoints > 0:
            recommendations.append(
                f"[ERROR] Found {report.error_endpoints} endpoints with errors. "
                "Check server logs and network connectivity. "
                "If /login-configuration works but other endpoints fail, they likely require authentication."
            )
        
        # Check for deprecated endpoints
        if report.deprecated_endpoints > 0:
            recommendations.append(
                f"[WARN] Found {report.deprecated_endpoints} deprecated endpoints. "
                "Consider removing them from documentation or updating clients."
            )
        
        # Overall status
        success_rate = (report.available_endpoints / report.total_endpoints * 100) if report.total_endpoints > 0 else 0
        if success_rate >= 80:
            recommendations.append(
                f"[OK] Good coverage: {success_rate:.1f}% of endpoints are available."
            )
        elif success_rate >= 50:
            recommendations.append(
                f"[WARN] Moderate coverage: {success_rate:.1f}% of endpoints are available. "
                "Review missing endpoints."
            )
        else:
            recommendations.append(
                f"[ERROR] Low coverage: {success_rate:.1f}% of endpoints are available. "
                "Significant issues detected - review immediately. "
                "Note: If /login-configuration works, other endpoints likely require authentication."
            )
        
        return recommendations
    
    def generate_report(self, report: ValidationReport, output_file: Optional[str] = None) -> str:
        """
        Generate human-readable report.
        
        Args:
            report: Validation report
            output_file: Optional file path to save report
            
        Returns:
            Report as string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("API Endpoints Validation Report")
        lines.append("=" * 80)
        lines.append(f"Generated: {report.timestamp}")
        lines.append(f"Base URL: {self.base_url}")
        lines.append(f"Site ID: {self.site_id}")
        lines.append("")
        lines.append("Summary:")
        lines.append(f"  Total Endpoints: {report.total_endpoints}")
        lines.append(f"  [OK] Available: {report.available_endpoints}")
        lines.append(f"  [AUTH] Auth Required: {report.auth_required_endpoints}")
        lines.append(f"  [404] Not Found (404): {report.not_found_endpoints}")
        lines.append(f"  [ERROR] Errors: {report.error_endpoints}")
        lines.append(f"  [DEPRECATED] Deprecated: {report.deprecated_endpoints}")
        lines.append("")
        
        # Detailed results
        lines.append("=" * 80)
        lines.append("Detailed Results")
        lines.append("=" * 80)
        lines.append("")
        
        # Group by status
        by_status = {}
        for result in report.results:
            if result.status not in by_status:
                by_status[result.status] = []
            by_status[result.status].append(result)
        
        # Available endpoints
        if 'available' in by_status:
            lines.append("[OK] Available Endpoints:")
            for result in sorted(by_status['available'], key=lambda x: (x.method, x.path)):
                lines.append(f"  {result.method:6} {result.path:50} ({result.operation_id})")
                if result.response_time_ms:
                    lines.append(f"    Response time: {result.response_time_ms:.2f}ms")
            lines.append("")
        
        # Auth required endpoints
        if 'auth_required' in by_status:
            lines.append("[AUTH] Authentication Required:")
            for result in sorted(by_status['auth_required'], key=lambda x: (x.method, x.path)):
                lines.append(f"  {result.method:6} {result.path:50} ({result.operation_id})")
                if result.status_code:
                    lines.append(f"    Status: {result.status_code}")
            lines.append("")
        
        # Not found endpoints
        if 'not_found' in by_status:
            lines.append("[404] Not Found (404):")
            for result in sorted(by_status['not_found'], key=lambda x: (x.method, x.path)):
                lines.append(f"  {result.method:6} {result.path:50} ({result.operation_id})")
                if result.is_deprecated:
                    lines.append(f"    [DEPRECATED]")
            lines.append("")
        
        # Error endpoints
        if 'error' in by_status:
            lines.append("[ERROR] Errors:")
            for result in sorted(by_status['error'], key=lambda x: (x.method, x.path)):
                lines.append(f"  {result.method:6} {result.path:50} ({result.operation_id})")
                if result.error_message:
                    lines.append(f"    Error: {result.error_message}")
                if result.status_code:
                    lines.append(f"    Status: {result.status_code}")
            lines.append("")
        
        # Recommendations
        lines.append("=" * 80)
        lines.append("Recommendations")
        lines.append("=" * 80)
        for i, rec in enumerate(report.recommendations, 1):
            lines.append(f"{i}. {rec}")
        lines.append("")
        
        # Missing endpoints list
        if report.not_found_endpoints > 0:
            lines.append("=" * 80)
            lines.append("Missing Endpoints - Action Required")
            lines.append("=" * 80)
            for result in sorted(by_status.get('not_found', []), key=lambda x: (x.method, x.path)):
                lines.append(f"  {result.method} {result.path}")
                lines.append(f"    Operation ID: {result.operation_id}")
                lines.append(f"    Full URL: {self.build_full_url(result.path)}")
                lines.append("")
        
        report_text = "\n".join(lines)
        
        # Save to file if specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            logger.info(f"Report saved to {output_path}")
        
        return report_text


class FocusServerAPIValidator:
    """
    Validates Focus Server API endpoints (Yoshi REST API).
    
    This class tests the Focus Server API endpoints documented in YOSHI_REST_API_DOCUMENTATION.md:
    - GET /channels
    - GET /live_metadata
    - POST /configure
    - GET /metadata/{job_id}
    
    IMPORTANT: Focus Server API does NOT require authentication.
    No username/password, no tokens, no cookies needed.
    All requests work without authentication.
    """
    
    # Focus Server API endpoints based on YOSHI_REST_API_DOCUMENTATION.md
    FOCUS_SERVER_ENDPOINTS = [
        {
            'method': 'GET',
            'path': '/channels',
            'operation_id': 'get_channels',
            'description': 'Get available channels (lowest and highest channel numbers)',
            'requires_body': False,
            'requires_params': False
        },
        {
            'method': 'GET',
            'path': '/live_metadata',
            'operation_id': 'get_live_metadata',
            'description': 'Get live fiber metadata (dx, prr, fiber info, etc.)',
            'requires_body': False,
            'requires_params': False
        },
        {
            'method': 'POST',
            'path': '/configure',
            'operation_id': 'configure_streaming_job',
            'description': 'Configure a new streaming job for spectrogram/heatmap display',
            'requires_body': True,
            'requires_params': False,
            'sample_body': {
                "displayTimeAxisDuration": 300,
                "nfftSelection": 256,
                "displayInfo": {"height": 600},
                "channels": {"min": 1, "max": 10},
                "frequencyRange": {"min": 0, "max": 1000},
                "start_time": 0,
                "end_time": 0,
                "view_type": "multichannel"
            }
        },
        {
            'method': 'GET',
            'path': '/metadata/{job_id}',
            'operation_id': 'get_job_metadata',
            'description': 'Get job metadata by job_id',
            'requires_body': False,
            'requires_params': True,
            'param_placeholder': 'test-job-id-12345'
        }
    ]
    
    def __init__(self, base_url: str, verify_ssl: bool = False):
        """
        Initialize the Focus Server API validator.
        
        Args:
            base_url: Base URL of the Focus Server (e.g., https://10.10.10.100/focus-server)
            verify_ssl: Whether to verify SSL certificates
        
        Note:
            Focus Server API does NOT require authentication.
            No username/password or tokens are needed.
        """
        self.base_url = base_url.rstrip('/')
        self.verify_ssl = verify_ssl
        
        # Create session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set SSL verification
        self.session.verify = verify_ssl
        
        # Set default headers
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Focus-Server-API-Validator/1.0.0"
        })
        
        logger.info(f"Initialized Focus Server API validator for {self.base_url}")
    
    def build_full_url(self, path: str, param_value: Optional[str] = None) -> str:
        """
        Build full URL from path template.
        
        Args:
            path: API path (may contain {job_id} placeholder)
            param_value: Value to replace {job_id} with
            
        Returns:
            Full URL
        """
        # Replace path parameters
        url_path = path
        if '{job_id}' in url_path:
            if param_value:
                url_path = url_path.replace('{job_id}', param_value)
            else:
                url_path = url_path.replace('{job_id}', 'test-job-id-12345')
        
        # Build full URL
        if url_path.startswith('/'):
            full_url = f"{self.base_url}{url_path}"
        else:
            full_url = f"{self.base_url}/{url_path}"
        
        return full_url
    
    def validate_endpoint(self, endpoint_def: Dict[str, Any]) -> EndpointResult:
        """
        Validate a single Focus Server API endpoint.
        
        Args:
            endpoint_def: Endpoint definition dictionary
            
        Returns:
            EndpointResult with validation status
        """
        method = endpoint_def['method']
        path = endpoint_def['path']
        operation_id = endpoint_def['operation_id']
        requires_body = endpoint_def.get('requires_body', False)
        requires_params = endpoint_def.get('requires_params', False)
        
        logger.info(f"Validating Focus Server API: {method} {path} ({operation_id})")
        
        # Build URL
        param_value = endpoint_def.get('param_placeholder')
        full_url = self.build_full_url(path, param_value)
        
        try:
            start_time = datetime.now()
            
            # Prepare request
            request_kwargs = {
                'timeout': 10,
                'allow_redirects': False
            }
            
            # Add body for POST requests
            if method == 'POST' and requires_body:
                sample_body = endpoint_def.get('sample_body', {})
                request_kwargs['json'] = sample_body
            
            # Make request
            response = self.session.request(method, full_url, **request_kwargs)
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            status_code = response.status_code
            
            # Interpret status codes
            if status_code == 200 or status_code == 201:
                status = 'available'
            elif status_code == 401 or status_code == 403:
                status = 'auth_required'
            elif status_code == 404:
                status = 'not_found'
            elif status_code == 400 or status_code == 422:
                # 400/422 usually means endpoint exists but validation failed
                status = 'available'
            elif status_code >= 500:
                status = 'error'
            else:
                status = 'available'  # Other 2xx/3xx codes indicate endpoint exists
            
            return EndpointResult(
                method=method,
                path=path,
                operation_id=operation_id,
                status=status,
                status_code=status_code,
                response_time_ms=elapsed_ms,
                requires_auth=(status_code == 401 or status_code == 403),
                requires_params=requires_params,
                is_deprecated=False
            )
            
        except requests.exceptions.Timeout:
            return EndpointResult(
                method=method,
                path=path,
                operation_id=operation_id,
                status='error',
                error_message='Request timeout',
                requires_params=requires_params,
                is_deprecated=False
            )
        except requests.exceptions.ConnectionError as e:
            return EndpointResult(
                method=method,
                path=path,
                operation_id=operation_id,
                status='error',
                error_message=f'Connection error: {str(e)}',
                requires_params=requires_params,
                is_deprecated=False
            )
        except Exception as e:
            return EndpointResult(
                method=method,
                path=path,
                operation_id=operation_id,
                status='error',
                error_message=f'Unexpected error: {str(e)}',
                requires_params=requires_params,
                is_deprecated=False
            )
    
    def validate_all(self) -> ValidationReport:
        """
        Validate all Focus Server API endpoints.
        
        Returns:
            ValidationReport with all results
        """
        logger.info("=" * 80)
        logger.info("Starting Focus Server API Endpoints Validation")
        logger.info("=" * 80)
        
        report = ValidationReport(total_endpoints=len(self.FOCUS_SERVER_ENDPOINTS))
        
        # Validate each endpoint
        for endpoint_def in self.FOCUS_SERVER_ENDPOINTS:
            result = self.validate_endpoint(endpoint_def)
            report.results.append(result)
            
            # Update counters
            if result.status == 'available':
                report.available_endpoints += 1
            elif result.status == 'not_found':
                report.not_found_endpoints += 1
            elif result.status == 'error':
                report.error_endpoints += 1
            elif result.status == 'auth_required':
                report.auth_required_endpoints += 1
        
        # Generate recommendations
        report.recommendations = self._generate_recommendations(report)
        
        logger.info("=" * 80)
        logger.info("Focus Server API Validation Complete")
        logger.info(f"Total: {report.total_endpoints}, Available: {report.available_endpoints}, "
                   f"Errors: {report.error_endpoints}, Not Found: {report.not_found_endpoints}")
        logger.info("=" * 80)
        
        return report
    
    def _generate_recommendations(self, report: ValidationReport) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if report.not_found_endpoints > 0:
            recommendations.append(
                f"{report.not_found_endpoints} Focus Server API endpoint(s) returned 404. "
                "Verify that the Focus Server is running and the base URL is correct."
            )
        
        if report.error_endpoints > 0:
            recommendations.append(
                f"{report.error_endpoints} Focus Server API endpoint(s) encountered errors. "
                "Check server logs and network connectivity."
            )
        
        if report.auth_required_endpoints > 0:
            recommendations.append(
                f"{report.auth_required_endpoints} Focus Server API endpoint(s) require authentication. "
                "Consider adding authentication support to the validation script."
            )
        
        if report.available_endpoints == report.total_endpoints:
            recommendations.append(
                "All Focus Server API endpoints are available and responding correctly."
            )
        
        return recommendations


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Validate API endpoints from Swagger spec and Focus Server API'
    )
    parser.add_argument(
        '--swagger-spec',
        default='docs/03_architecture/api/swagger_spec.json',
        help='Path to Swagger spec JSON file'
    )
    parser.add_argument(
        '--env',
        default='staging',
        choices=['staging', 'production', 'local'],
        help='Environment to test against'
    )
    parser.add_argument(
        '--output',
        default='docs/04_testing/api_endpoints_validation_report.txt',
        help='Output file for report'
    )
    parser.add_argument(
        '--focus-server-only',
        action='store_true',
        help='Only validate Focus Server API endpoints (skip Prisma Web App API)'
    )
    parser.add_argument(
        '--prisma-only',
        action='store_true',
        help='Only validate Prisma Web App API endpoints (skip Focus Server API)'
    )
    parser.add_argument(
        '--username',
        help='Username for authentication (optional)'
    )
    parser.add_argument(
        '--password',
        help='Password for authentication (optional)'
    )
    parser.add_argument(
        '--access-token',
        help='Access token/cookie value (alternative to username/password)'
    )
    
    args = parser.parse_args()
    
    # Get credentials from environment variables if not provided via command line
    username = args.username or os.getenv('PRISMA_API_USERNAME')
    password = args.password or os.getenv('PRISMA_API_PASSWORD')
    access_token = args.access_token or os.getenv('PRISMA_API_ACCESS_TOKEN')
    
    # Load configuration
    config_manager = ConfigManager(env=args.env)
    env_config = config_manager.get_api_config()  # Get focus_server config
    
    # Get API base URL for token management
    base_url = env_config['frontend_api_url']
    if '/internal/sites/' in base_url:
        base_url = base_url.split('/internal/sites/')[0]
    
    # Try to load saved token first (even without credentials)
    if not access_token:
        try:
            from src.utils.token_manager import TokenManager
            token_manager = TokenManager(
                base_url=base_url,
                username=username or '',  # Can be empty for loading saved token
                password=password or '',   # Can be empty for loading saved token
                verify_ssl=env_config.get('verify_ssl', False)
            )
            # Try to load saved token (this won't acquire new token if username/password missing)
            saved_token = token_manager._load_token_from_file()
            if saved_token:
                access_token = saved_token
                logger.info("[OK] Loaded saved token from file")
        except Exception as e:
            logger.debug(f"Could not load saved token: {e}")
    
    # If we have username/password but no token, try to get token automatically
    if username and password and not access_token:
        logger.info("=" * 80)
        logger.info("AUTO-TOKEN ACQUISITION")
        logger.info("=" * 80)
        logger.info("Username/password provided but no token - attempting automatic token acquisition")
        
        token_manager = TokenManager(
            base_url=base_url,
            username=username,
            password=password,
            verify_ssl=env_config.get('verify_ssl', False)
        )
        
        token = token_manager.get_token()
        if token:
            access_token = token
            logger.info("[OK] Token acquired automatically and will be reused")
        else:
            logger.warning("[WARN] Failed to acquire token automatically - will try without authentication")
    
    # Get Focus Server base URL
    focus_server_base_url = env_config.get('base_url', '').rstrip('/')
    if not focus_server_base_url:
        focus_server_base_url = env_config.get('frontend_url', '').replace('/liveView', '/focus-server')
    
    verify_ssl = env_config.get('verify_ssl', False)
    
    logger.info(f"Environment: {args.env}")
    logger.info(f"Focus Server Base URL: {focus_server_base_url}")
    logger.info(f"SSL Verify: {verify_ssl}")
    
    all_reports = []
    combined_report_text = []
    
    # Validate Focus Server API (unless --prisma-only is set)
    if not args.prisma_only:
        logger.info("\n" + "=" * 80)
        logger.info("FOCUS SERVER API VALIDATION")
        logger.info("=" * 80)
        
        focus_validator = FocusServerAPIValidator(
            base_url=focus_server_base_url,
            verify_ssl=verify_ssl
        )
        focus_report = focus_validator.validate_all()
        all_reports.append(('Focus Server API', focus_report, focus_validator))
    
    # Validate Prisma Web App API (unless --focus-server-only is set)
    if not args.focus_server_only:
        logger.info("\n" + "=" * 80)
        logger.info("PRISMA WEB APP API VALIDATION")
        logger.info("=" * 80)
        
        # Get API base URL
        base_url = env_config['frontend_api_url']
        # Extract base URL without the site-specific path
        if '/internal/sites/' in base_url:
            base_url = base_url.split('/internal/sites/')[0]
        
        site_id = env_config['site_id']
        
        logger.info(f"Prisma API Base URL: {base_url}")
        logger.info(f"Site ID: {site_id}")
        
        # Create validator
        prisma_validator = APIEndpointValidator(
            swagger_spec_path=args.swagger_spec,
            base_url=base_url,
            site_id=site_id,
            verify_ssl=verify_ssl,
            username=username,
            password=password,
            access_token=access_token
        )
        
        # Run validation
        prisma_report = prisma_validator.validate_all()
        all_reports.append(('Prisma Web App API', prisma_report, prisma_validator))
    
    # Generate combined report
    combined_report_text.append("=" * 80)
    combined_report_text.append("COMBINED API ENDPOINTS VALIDATION REPORT")
    combined_report_text.append("=" * 80)
    combined_report_text.append(f"Generated: {datetime.now().isoformat()}")
    combined_report_text.append(f"Environment: {args.env}")
    combined_report_text.append("")
    
    total_available = 0
    total_not_found = 0
    total_errors = 0
    total_auth_required = 0
    total_endpoints = 0
    
    for api_name, report, validator in all_reports:
        combined_report_text.append("=" * 80)
        combined_report_text.append(f"{api_name.upper()} - SUMMARY")
        combined_report_text.append("=" * 80)
        combined_report_text.append(f"Total Endpoints: {report.total_endpoints}")
        combined_report_text.append(f"Available: {report.available_endpoints}")
        combined_report_text.append(f"Not Found (404): {report.not_found_endpoints}")
        combined_report_text.append(f"Errors: {report.error_endpoints}")
        combined_report_text.append(f"Auth Required: {report.auth_required_endpoints}")
        combined_report_text.append("")
        
        # Generate detailed report for this API
        if isinstance(validator, APIEndpointValidator):
            # Prisma Web App API - use existing report generation
            api_report_text = validator.generate_report(report, output_file=None)
            combined_report_text.append(api_report_text)
        else:
            # Focus Server API - generate simple report
            combined_report_text.append(f"{api_name} - DETAILED RESULTS:")
            combined_report_text.append("-" * 80)
            for result in report.results:
                status_icon = {
                    'available': '[OK]',
                    'not_found': '[404]',
                    'error': '[ERROR]',
                    'auth_required': '[AUTH]'
                }.get(result.status, '[?]')
                
                combined_report_text.append(
                    f"{status_icon} {result.method:6} {result.path:50} ({result.operation_id})"
                )
                if result.status_code:
                    combined_report_text.append(f"    Status Code: {result.status_code}")
                if result.response_time_ms:
                    combined_report_text.append(f"    Response Time: {result.response_time_ms:.2f}ms")
                if result.error_message:
                    combined_report_text.append(f"    Error: {result.error_message}")
            combined_report_text.append("")
            
            # Recommendations
            if report.recommendations:
                combined_report_text.append("Recommendations:")
                for rec in report.recommendations:
                    combined_report_text.append(f"  - {rec}")
                combined_report_text.append("")
        
        total_available += report.available_endpoints
        total_not_found += report.not_found_endpoints
        total_errors += report.error_endpoints
        total_auth_required += report.auth_required_endpoints
        total_endpoints += report.total_endpoints
    
    # Overall summary
    combined_report_text.append("=" * 80)
    combined_report_text.append("OVERALL SUMMARY")
    combined_report_text.append("=" * 80)
    combined_report_text.append(f"Total Endpoints Tested: {total_endpoints}")
    combined_report_text.append(f"Available: {total_available} ({total_available/total_endpoints*100:.1f}%)")
    combined_report_text.append(f"Not Found: {total_not_found}")
    combined_report_text.append(f"Errors: {total_errors}")
    combined_report_text.append(f"Auth Required: {total_auth_required}")
    combined_report_text.append("")
    
    # Save combined report
    report_text = "\n".join(combined_report_text)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        logger.info(f"Combined report saved to {output_path}")
    
    # Print report
    print("\n" + report_text)
    
    # Exit with appropriate code
    if total_not_found > 0 or total_errors > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()

