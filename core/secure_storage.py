"""
path: core/secure_storage.py
purpose: Provides secure storage for sensitive data
critical:
- Must encrypt sensitive data
- Must handle key management
- Must provide secure access methods
- Must prevent data leaks
"""

import os
import json
import base64
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from .error_handler import ConfigurationError

logger = logging.getLogger(__name__)

class SecureStorage:
    """
    Secure storage system for sensitive data.
    
    This class:
    1. Encrypts sensitive data
    2. Manages encryption keys
    3. Provides secure access methods
    4. Handles key rotation
    
    Attributes:
        storage_path (Path): Path to encrypted storage
        key_file (Path): Path to key file
        salt_file (Path): Path to salt file
    """
    
    def __init__(self, storage_dir: str = 'data/secure'):
        """
        Initialize secure storage.
        
        Args:
            storage_dir: Directory for secure storage
        """
        self.storage_path = Path(storage_dir) / 'secure_data.enc'
        self.key_file = Path(storage_dir) / 'key.enc'
        self.salt_file = Path(storage_dir) / 'salt'
        
        # Create storage directory
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize storage system
        self._initialize_storage()
        
    def _initialize_storage(self) -> None:
        """Initialize the storage system and key files."""
        try:
            # Generate or load salt
            if not self.salt_file.exists():
                self.salt = os.urandom(16)
                with open(self.salt_file, 'wb') as f:
                    f.write(self.salt)
            else:
                with open(self.salt_file, 'rb') as f:
                    self.salt = f.read()
                    
            # Generate or load key
            if not self.key_file.exists():
                self._generate_key()
            else:
                self._load_key()
                
            # Create empty storage if it doesn't exist
            if not self.storage_path.exists():
                self.save({})
                
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize secure storage: {e}")
            
    def _generate_key(self) -> None:
        """Generate a new encryption key."""
        try:
            # Use environment variable as base for key generation
            base_key = os.getenv('DISCORD_TOKEN', '').encode()
            if not base_key:
                raise ConfigurationError("DISCORD_TOKEN environment variable is required")
                
            # Generate key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(base_key))
            
            # Save encrypted key
            with open(self.key_file, 'wb') as f:
                f.write(key)
                
            self.fernet = Fernet(key)
            
        except Exception as e:
            raise ConfigurationError(f"Failed to generate encryption key: {e}")
            
    def _load_key(self) -> None:
        """Load the encryption key."""
        try:
            with open(self.key_file, 'rb') as f:
                key = f.read()
            self.fernet = Fernet(key)
        except Exception as e:
            raise ConfigurationError(f"Failed to load encryption key: {e}")
            
    def _encrypt(self, data: str) -> bytes:
        """
        Encrypt data.
        
        Args:
            data: Data to encrypt
            
        Returns:
            bytes: Encrypted data
        """
        return self.fernet.encrypt(data.encode())
        
    def _decrypt(self, data: bytes) -> str:
        """
        Decrypt data.
        
        Args:
            data: Data to decrypt
            
        Returns:
            str: Decrypted data
        """
        return self.fernet.decrypt(data).decode()
        
    def save(self, data: Dict[str, Any]) -> None:
        """
        Save data to secure storage.
        
        Args:
            data: Data to save
        """
        try:
            # Convert to JSON and encrypt
            json_data = json.dumps(data)
            encrypted = self._encrypt(json_data)
            
            # Write to file
            with open(self.storage_path, 'wb') as f:
                f.write(encrypted)
                
        except Exception as e:
            raise ConfigurationError(f"Failed to save to secure storage: {e}")
            
    def load(self) -> Dict[str, Any]:
        """
        Load data from secure storage.
        
        Returns:
            Dict[str, Any]: Decrypted data
        """
        try:
            # Read and decrypt data
            with open(self.storage_path, 'rb') as f:
                encrypted = f.read()
                
            decrypted = self._decrypt(encrypted)
            return json.loads(decrypted)
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load from secure storage: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from secure storage.
        
        Args:
            key: Key to retrieve
            default: Default value if key not found
            
        Returns:
            Any: Retrieved value or default
        """
        try:
            data = self.load()
            return data.get(key, default)
        except Exception:
            return default
            
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in secure storage.
        
        Args:
            key: Key to set
            value: Value to store
        """
        try:
            data = self.load()
            data[key] = value
            self.save(data)
        except Exception as e:
            raise ConfigurationError(f"Failed to set value in secure storage: {e}")
            
    def delete(self, key: str) -> None:
        """
        Delete a value from secure storage.
        
        Args:
            key: Key to delete
        """
        try:
            data = self.load()
            if key in data:
                del data[key]
                self.save(data)
        except Exception as e:
            raise ConfigurationError(f"Failed to delete from secure storage: {e}")
            
    def rotate_key(self) -> None:
        """Rotate the encryption key."""
        try:
            # Load current data
            current_data = self.load()
            
            # Generate new key
            os.remove(self.key_file)
            self._generate_key()
            
            # Re-encrypt data with new key
            self.save(current_data)
            
            logger.info("Successfully rotated encryption key")
        except Exception as e:
            raise ConfigurationError(f"Failed to rotate encryption key: {e}")

# Global secure storage instance
secure_storage = SecureStorage() 