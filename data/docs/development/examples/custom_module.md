# Creating a Custom Module

This example demonstrates how to create a custom module for the Discord bot.

## Basic Module Structure

```python
from typing import Optional
from discord import app_commands, Interaction
from core.base_module import BaseModule
from config.base_config import BaseConfig

class CustomConfig(BaseConfig):
    """Configuration for custom module."""
    
    def __init__(self):
        super().__init__()
        self._config = {
            "ENABLED": False,
            "NOTIFICATION_CHANNEL_ID": None,
            "CUSTOM_SETTING": "default"
        }
        
    @property
    def CUSTOM_SETTING(self) -> str:
        return self._config["CUSTOM_SETTING"]
        
    @CUSTOM_SETTING.setter
    def CUSTOM_SETTING(self, value: str):
        self._config["CUSTOM_SETTING"] = value
        
    def validate_config(self) -> bool:
        if not super().validate_config():
            return False
            
        if not isinstance(self.CUSTOM_SETTING, str):
            self._logger.error("CUSTOM_SETTING must be a string")
            return False
            
        return True

class CustomModule(BaseModule):
    """A custom module example."""
    
    def __init__(self, bot):
        super().__init__(bot)
        self.config = CustomConfig()
        
    async def setup(self):
        """Set up the module."""
        if not self.config.validate_config():
            self._logger.error("Invalid configuration")
            return
            
        self.enabled = self.config.ENABLED
        if not self.enabled:
            return
            
        # Register commands
        self._register_commands()
        
    def _register_commands(self):
        """Register module commands."""
        @app_commands.command(name="custom")
        async def custom_command(interaction: Interaction):
            """Example custom command."""
            await interaction.response.send_message(
                f"Custom setting: {self.config.CUSTOM_SETTING}"
            )
            
        self.bot.tree.add_command(custom_command)
        
    async def cleanup(self):
        """Clean up module resources."""
        self.enabled = False
```

## Usage Example

```python
# In discord_bot.py
from modules.custom_module import CustomModule

async def setup_custom_module(bot):
    module = CustomModule(bot)
    await module.setup()
    return module

# In main setup
custom_module = await setup_custom_module(bot)
```

## Configuration Example

```python
# In config/features/custom_config.py
from modules.custom_module import CustomConfig

custom_config = CustomConfig()
custom_config.ENABLED = True
custom_config.CUSTOM_SETTING = "custom value"

# Export instance
__all__ = ["custom_config"]
```

## Environment Variables

```env
# Custom Module Settings
CUSTOM_WHITELIST_ROLE_IDS=role_id1,role_id2
CUSTOM_NOTIFICATION_CHANNEL_ID=channel_id
```

## Best Practices

1. Always inherit from BaseModule
2. Create a dedicated config class
3. Validate all configuration
4. Use type hints
5. Add proper documentation
6. Include error handling
7. Clean up resources

## Testing

```python
# In tests/test_custom_module.py
import pytest
from modules.custom_module import CustomModule, CustomConfig

@pytest.fixture
def config():
    return CustomConfig()

def test_custom_config_validation(config):
    config.CUSTOM_SETTING = "test"
    assert config.validate_config() is True
    
    config.CUSTOM_SETTING = 123  # Should fail
    assert config.validate_config() is False
``` 