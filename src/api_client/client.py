"""
Retivis POC API Client

Main client for interacting with the Retivis POC management API.
"""

import os
import hashlib
from typing import Optional, Dict, Any
import requests
from datetime import datetime, timedelta
from .exceptions import AuthenticationError, ConnectionError, ValidationError


class RetivisPOCClient:
    """Client for Retivis POC API"""

    def __init__(
        self,
        api_url: Optional[str] = None,
        account: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 30,
        verify_ssl: bool = True,
        use_prehashed: bool = False,
    ):
        """
        Initialize Retivis POC API client

        Args:
            api_url: Base API URL
            account: Account identifier (acc header)
            password: Password (will be MD5 hashed unless use_prehashed=True)
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            use_prehashed: If True, password is already hashed
        """
        self.api_url = api_url or os.getenv(
            "RETIVIS_API_URL", "https://www.retevispoc.com"
        )
        self.account = account or os.getenv("RETIVIS_ACCOUNT")
        self.password = password or os.getenv("RETIVIS_PASSWORD")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.use_prehashed = use_prehashed

        self.session = requests.Session()
        self.authenticated = False

    def _hash_password(self, password: str) -> str:
        """Hash password using MD5"""
        return hashlib.md5(password.encode()).hexdigest()

    def login(self) -> bool:
        """
        Authenticate by testing API access with account and password headers

        Returns:
            True if authentication successful, False otherwise

        Raises:
            AuthenticationError: If login fails
            ConnectionError: If connection to API fails
        """
        if not self.account or not self.password:
            raise ValidationError("Account and password required for login")

        try:
            # Hash password using MD5 (unless already hashed)
            if self.use_prehashed:
                pwd_hash = self.password
            else:
                pwd_hash = self._hash_password(self.password)
            
            # Set up authentication headers
            headers = {
                "acc": self.account,
                "pwd": pwd_hash,
                "clientId": "poc-web",
                "locale": "en",
                "Accept": "application/json, text/plain, */*",
            }
            self.session.headers.update(headers)
            
            print(f"DEBUG: Testing API access with account: {self.account}")
            print(f"DEBUG: Password hash: {pwd_hash}")

            # Test connection with monitorList endpoint
            test_url = f"{self.api_url}/tyt_web/Api/Index/monitorList"
            params = {"uid": "USER_ID"}
            
            response = self.session.get(
                test_url,
                params=params,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )

            print(f"DEBUG: API response status: {response.status_code}")

            if response.status_code == 200:
                try:
                    result = response.json()
                    
                    # Check if we got a valid response (not an error page)
                    if isinstance(result, dict) and ("status" in result or "msg" in result):
                        self.authenticated = True
                        return True
                    else:
                        raise AuthenticationError("Invalid API response format")
                except ValueError:
                    raise AuthenticationError("API returned invalid JSON")
            else:
                raise ConnectionError(
                    f"API returned status {response.status_code}"
                )

        except requests.RequestException as e:
            raise ConnectionError(f"Failed to connect to API: {str(e)}")

    def is_authenticated(self) -> bool:
        """Check if client is authenticated"""
        return self.authenticated

    def get_monitor_list(self, uid: str) -> Dict[str, Any]:
        """
        Get monitor list for user

        Args:
            uid: User ID

        Returns:
            API response dictionary
        """
        if not self.authenticated:
            self.login()

        url = f"{self.api_url}/tyt_web/Api/Index/monitorList"
        params = {"uid": uid}

        response = self.session.get(
            url,
            params=params,
            timeout=self.timeout,
            verify=self.verify_ssl,
        )

        return response.json()

    def get_groups(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """
        Get radio groups

        Args:
            page: Page number
            limit: Results per page

        Returns:
            API response dictionary
        """
        if not self.authenticated:
            self.login()

        url = f"{self.api_url}/tyt_web/Api/Index/groups"
        params = {"page": page, "limit": limit}

        response = self.session.get(
            url,
            params=params,
            timeout=self.timeout,
            verify=self.verify_ssl,
        )

        return response.json()

    def get_group_details(self, gid: str) -> Dict[str, Any]:
        """Get details for specific group"""
        if not self.authenticated:
            self.login()

        url = f"{self.api_url}/tyt_web/Api/Index/groupDetail"
        params = {"gid": gid}

        response = self.session.get(
            url,
            params=params,
            timeout=self.timeout,
            verify=self.verify_ssl,
        )

        return response.json()

    def close(self):
        """Close session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()




