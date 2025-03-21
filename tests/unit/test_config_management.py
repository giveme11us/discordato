"""
Unit tests for configuration management system.
"""
import os
import pytest
from core.config import Config, ConfigurationError

@pytest.mark.unit
class TestConfigManagement:
    """Test suite for configuration management functionality."""
    
    def test_config_loading(self, test_config):
        """Test that configuration loads correctly from environment."""
        # Test
        config = Config()
        
        # Verify
        assert config.bot_token == test_config['DISCORD_BOT_TOKEN']
        assert config.application_id == test_config['APPLICATION_ID']
        assert isinstance(config.guild_ids, list)
        assert len(config.guild_ids) == 2  # From test_config GUILD_IDS
        
    def test_required_config_validation(self):
        """Test that missing required configuration raises appropriate error."""
        # Setup
        required_vars = ['DISCORD_BOT_TOKEN', 'APPLICATION_ID']
        
        for var in required_vars:
            # Temporarily remove required variable
            original_value = os.environ.get(var)
            os.environ.pop(var, None)
            
            # Test
            with pytest.raises(ConfigurationError, match=f"Missing required configuration: {var}"):
                Config()
                
            # Restore environment
            if original_value:
                os.environ[var] = original_value
                
    def test_config_type_conversion(self, test_config):
        """Test that configuration values are converted to appropriate types."""
        # Setup
        os.environ['TEST_INT'] = '42'
        os.environ['TEST_FLOAT'] = '3.14'
        os.environ['TEST_BOOL'] = 'true'
        os.environ['TEST_LIST'] = 'item1,item2,item3'
        
        # Test
        config = Config()
        
        # Verify
        assert isinstance(config.get_int('TEST_INT'), int)
        assert config.get_int('TEST_INT') == 42
        
        assert isinstance(config.get_float('TEST_FLOAT'), float)
        assert config.get_float('TEST_FLOAT') == 3.14
        
        assert isinstance(config.get_bool('TEST_BOOL'), bool)
        assert config.get_bool('TEST_BOOL') is True
        
        assert isinstance(config.get_list('TEST_LIST'), list)
        assert config.get_list('TEST_LIST') == ['item1', 'item2', 'item3']
        
    def test_config_defaults(self):
        """Test that default values work correctly."""
        # Test
        config = Config()
        
        # Verify
        assert config.get('NON_EXISTENT', default='default') == 'default'
        assert config.get_int('NON_EXISTENT', default=42) == 42
        assert config.get_bool('NON_EXISTENT', default=True) is True
        assert config.get_list('NON_EXISTENT', default=['default']) == ['default']
        
    def test_config_validation(self):
        """Test configuration validation rules."""
        # Setup invalid configurations
        test_cases = [
            ('GUILD_IDS', 'invalid,ids', "Invalid guild ID format"),
            ('ENABLED_MODULES', '', "No modules enabled"),
            ('LOG_LEVEL', 'INVALID', "Invalid log level"),
        ]
        
        # Test each case
        for var, value, expected_error in test_cases:
            os.environ[var] = value
            
            with pytest.raises(ConfigurationError, match=expected_error):
                Config().validate()
                
    def test_sensitive_config_masking(self, test_config):
        """Test that sensitive configuration values are properly masked."""
        # Setup
        config = Config()
        
        # Test
        config_str = str(config)
        
        # Verify
        assert test_config['DISCORD_BOT_TOKEN'] not in config_str
        assert '***' in config_str  # Masked value
        assert test_config['APPLICATION_ID'] in config_str  # Non-sensitive value 