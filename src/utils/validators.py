"""
Validation utilities
"""

from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def validate_credentials(username: str, password: str) -> bool:
    """Validate credentials"""
    return bool(username and password and len(username) > 0 and len(password) > 0)



