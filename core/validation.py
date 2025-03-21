"""
path: core/validation.py
purpose: Provides input validation and sanitization utilities
critical:
- Must validate all user inputs
- Must sanitize data before storage
- Must prevent injection attacks
- Must handle validation errors gracefully
"""

import re
import logging
import urllib.parse
from typing import Any, Dict, List, Optional, Union
from .error_handler import ValidationError

logger = logging.getLogger(__name__)

class InputValidator:
    """
    Validates and sanitizes user input.
    
    This class provides:
    1. Input validation for common data types
    2. Sanitization for user inputs
    3. URL and webhook validation
    4. Personal data validation
    5. Numeric range validation
    """
    
    # Regex patterns for validation
    PATTERNS = {
        'url': r'^https?:\/\/([\w\-]+(\.[\w\-]+)+)(:\d+)?([\/\w\-\.\?\=\&\%\#\+]*)*\/?$',
        'webhook': r'^https:\/\/(?:.*\.)?discord(?:app)?\.com\/api\/webhooks\/\d+\/[\w-]+$',
        'phone': r'^\+?[\d\-\(\)\s]{3,20}$',
        'name': r'^[\w\-\s\']{2,50}$',
        'address': r'^[\w\-\s\',\.\d\/]{1,100}$',
        'zipcode': r'^\d{5}(?:[-\s]\d{4})?$',
        'proxy_url': r'^https?:\/\/([\w\-]+(\.[\w\-]+)+)(:\d+)?([\/\w\-\.\?\=\&\%\#\+]*)*\/?$',
        'discord_id': r'^\d{17,20}$'
    }
    
    @classmethod
    def validate_url(cls, url: str, allow_http: bool = False) -> str:
        """
        Validate and sanitize a URL.
        
        Args:
            url: The URL to validate
            allow_http: Whether to allow non-HTTPS URLs
            
        Returns:
            str: The sanitized URL
            
        Raises:
            ValidationError: If URL is invalid
        """
        if not url:
            raise ValidationError("URL cannot be empty")
            
        # Basic URL sanitization
        url = url.strip()
        
        # Check URL format
        if not re.match(cls.PATTERNS['url'], url):
            raise ValidationError("Invalid URL format")
            
        # Ensure HTTPS unless explicitly allowed
        if not allow_http and not url.startswith('https://'):
            raise ValidationError("URL must use HTTPS")
            
        # Parse and validate URL components
        try:
            parsed = urllib.parse.urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                raise ValidationError("Invalid URL components")
        except Exception as e:
            raise ValidationError(f"URL parsing error: {str(e)}")
            
        return url
        
    @classmethod
    def validate_webhook(cls, webhook: str) -> str:
        """
        Validate a Discord webhook URL.
        
        Args:
            webhook: The webhook URL to validate
            
        Returns:
            str: The validated webhook URL
            
        Raises:
            ValidationError: If webhook URL is invalid
        """
        if not webhook:
            raise ValidationError("Webhook URL cannot be empty")
            
        webhook = webhook.strip()
        
        if not re.match(cls.PATTERNS['webhook'], webhook):
            raise ValidationError("Invalid Discord webhook URL format")
            
        return webhook
        
    @classmethod
    def validate_phone(cls, phone: str) -> str:
        """
        Validate and sanitize a phone number.
        
        Args:
            phone: The phone number to validate
            
        Returns:
            str: The sanitized phone number
            
        Raises:
            ValidationError: If phone number is invalid
        """
        if not phone:
            raise ValidationError("Phone number cannot be empty")
            
        # Remove all non-numeric characters except + for country code
        phone = re.sub(r'[^\d+]', '', phone)
        
        if not re.match(cls.PATTERNS['phone'], phone):
            raise ValidationError("Invalid phone number format")
            
        return phone
        
    @classmethod
    def validate_name(cls, name: str, field: str = "Name") -> str:
        """
        Validate a name field.
        
        Args:
            name: The name to validate
            field: The field name for error messages
            
        Returns:
            str: The sanitized name
            
        Raises:
            ValidationError: If name is invalid
        """
        if not name:
            raise ValidationError(f"{field} cannot be empty")
            
        name = name.strip()
        
        if not re.match(cls.PATTERNS['name'], name):
            raise ValidationError(f"Invalid {field.lower()} format")
            
        return name
        
    @classmethod
    def validate_address(cls, address: str) -> str:
        """
        Validate and sanitize an address.
        
        Args:
            address: The address to validate
            
        Returns:
            str: The sanitized address
            
        Raises:
            ValidationError: If address is invalid
        """
        if not address:
            raise ValidationError("Address cannot be empty")
            
        address = address.strip()
        
        if not re.match(cls.PATTERNS['address'], address):
            raise ValidationError("Invalid address format")
            
        return address
        
    @classmethod
    def validate_zipcode(cls, zipcode: str) -> str:
        """
        Validate a ZIP code.
        
        Args:
            zipcode: The ZIP code to validate
            
        Returns:
            str: The validated ZIP code
            
        Raises:
            ValidationError: If ZIP code is invalid
        """
        if not zipcode:
            raise ValidationError("ZIP code cannot be empty")
            
        zipcode = zipcode.strip()
        
        if not re.match(cls.PATTERNS['zipcode'], zipcode):
            raise ValidationError("Invalid ZIP code format")
            
        return zipcode
        
    @classmethod
    def validate_proxy_url(cls, url: str) -> str:
        """
        Validate a proxy URL.
        
        Args:
            url: The proxy URL to validate
            
        Returns:
            str: The validated proxy URL
            
        Raises:
            ValidationError: If proxy URL is invalid
        """
        if not url:
            return ""  # Proxy URL is optional
            
        url = url.strip()
        
        if not re.match(cls.PATTERNS['proxy_url'], url):
            raise ValidationError("Invalid proxy URL format")
            
        return url
        
    @classmethod
    def validate_discord_id(cls, discord_id: Union[str, int]) -> str:
        """
        Validate a Discord user ID.
        
        Args:
            discord_id: The Discord ID to validate
            
        Returns:
            str: The validated Discord ID
            
        Raises:
            ValidationError: If Discord ID is invalid
        """
        discord_id = str(discord_id).strip()
        
        if not re.match(cls.PATTERNS['discord_id'], discord_id):
            raise ValidationError("Invalid Discord user ID format")
            
        return discord_id
        
    @classmethod
    def validate_range(cls, value: Union[int, float], min_val: Union[int, float], 
                      max_val: Union[int, float], field: str) -> Union[int, float]:
        """
        Validate a numeric value within a range.
        
        Args:
            value: The value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            field: Field name for error messages
            
        Returns:
            Union[int, float]: The validated value
            
        Raises:
            ValidationError: If value is outside allowed range
        """
        try:
            value = float(value) if isinstance(value, str) else value
            if not min_val <= value <= max_val:
                raise ValidationError(
                    f"{field} must be between {min_val} and {max_val}"
                )
            return value
        except (TypeError, ValueError):
            raise ValidationError(f"Invalid {field.lower()} value")
            
    @classmethod
    def validate_profile(cls, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a complete redeye profile.
        
        Args:
            profile: The profile data to validate
            
        Returns:
            Dict[str, Any]: The validated profile data
            
        Raises:
            ValidationError: If any profile field is invalid
        """
        validated = {}
        
        try:
            # Validate Discord ID
            validated['Name'] = cls.validate_discord_id(profile['Name'])
            
            # Validate personal information
            validated['FirstName'] = cls.validate_name(profile['FirstName'], "First name")
            validated['LastName'] = cls.validate_name(profile['LastName'], "Last name")
            validated['Phone'] = cls.validate_phone(profile['Phone'])
            validated['Address'] = cls.validate_address(profile['Address'])
            validated['City'] = cls.validate_name(profile['City'], "City")
            validated['StateId'] = profile['StateId'].strip().upper()  # State/Province code
            validated['ZipCode'] = cls.validate_zipcode(profile['ZipCode'])
            validated['CountryId'] = profile['CountryId'].strip().upper()  # Country code
            
            # Validate timing settings
            validated['TimeoutUpperBound'] = cls.validate_range(
                profile['TimeoutUpperBound'], 1000, 300000, "Timeout upper bound"
            )
            validated['TimeoutLowerBound'] = cls.validate_range(
                profile['TimeoutLowerBound'], 1000, 300000, "Timeout lower bound"
            )
            validated['DelayUpperBound'] = cls.validate_range(
                profile['DelayUpperBound'], 0, 60000, "Delay upper bound"
            )
            validated['DelayLowerBound'] = cls.validate_range(
                profile['DelayLowerBound'], 0, 60000, "Delay lower bound"
            )
            
            # Validate that lower bounds are less than upper bounds
            if validated['TimeoutLowerBound'] > validated['TimeoutUpperBound']:
                raise ValidationError("Timeout lower bound must be less than upper bound")
            if validated['DelayLowerBound'] > validated['DelayUpperBound']:
                raise ValidationError("Delay lower bound must be less than upper bound")
            
            # Validate URLs
            validated['Webhook'] = cls.validate_webhook(profile['Webhook'])
            validated['UpstreamProxyURL'] = cls.validate_proxy_url(profile.get('UpstreamProxyURL', ''))
            validated['UpstreamAkmaiCookieURL'] = cls.validate_proxy_url(profile.get('UpstreamAkmaiCookieURL', ''))
            
            # Copy other fields
            validated['KeepConnectionsAlive'] = profile.get('KeepConnectionsAlive', 'NO').upper() in ['YES', 'TRUE', '1']
            validated['CodFisc'] = profile.get('CodFisc', '').strip()
            
        except KeyError as e:
            raise ValidationError(f"Missing required field: {str(e)}")
        except ValidationError as e:
            raise ValidationError(f"Profile validation error: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Unexpected error during profile validation: {str(e)}")
            
        return validated 