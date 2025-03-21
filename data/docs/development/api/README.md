# Development API Guide

## Overview

This guide covers the core APIs and development patterns for extending the Discord bot.

## Core APIs

### Module System

The module system provides a flexible architecture for extending bot functionality:

```python
from core.module import ModuleBase

class CustomModule(ModuleBase):
    def __init__(self):
        super().__init__()
        self.name = "custom"
        self.description = "Custom module"

    async def setup(self):
        # Initialize module
        pass

    async def cleanup(self):
        # Cleanup resources
        pass
```

### Configuration System

Configuration management for modules:

```python
from config.core import ConfigBase

class ModuleConfig(ConfigBase):
    def __init__(self):
        self.enabled = True
        self.settings = {}

    @property
    def is_enabled(self) -> bool:
        return self.enabled

    def validate(self) -> bool:
        return True
```

### Command System

Creating and registering commands:

```python
from discord import app_commands
from core.commands import CommandBase

class CustomCommand(CommandBase):
    def __init__(self):
        super().__init__()
        self.name = "custom"
        self.description = "Custom command"

    @app_commands.command()
    async def execute(self, interaction):
        await interaction.response.send_message("Command executed!")
```

## Development Guidelines

### Creating New Features

1. Plan the feature
   - Define requirements
   - Design interfaces
   - Plan configuration

2. Implement core functionality
   - Create module class
   - Implement commands
   - Add configuration

3. Add documentation
   - Update API docs
   - Add usage examples
   - Document configuration

4. Write tests
   - Unit tests
   - Integration tests
   - Command tests

### Best Practices

1. Code Organization
   - Keep modules focused
   - Use clear naming
   - Follow project structure

2. Error Handling
   - Use custom exceptions
   - Add error messages
   - Log errors properly

3. Configuration
   - Validate inputs
   - Use type hints
   - Document options

4. Testing
   - Test edge cases
   - Mock dependencies
   - Check performance

## Example Implementation

### Custom Module

```python
# modules/custom/module.py
from core.module import ModuleBase
from core.commands import CommandBase
from config.core import ConfigBase

class CustomConfig(ConfigBase):
    def __init__(self):
        self.enabled = True
        self.channel_id = None

    def validate(self):
        return self.channel_id is not None

class CustomCommand(CommandBase):
    def __init__(self, config):
        super().__init__()
        self.config = config

    async def execute(self, interaction):
        if not self.config.is_enabled:
            return
        await interaction.response.send_message("Success!")

class CustomModule(ModuleBase):
    def __init__(self):
        super().__init__()
        self.config = CustomConfig()
        self.command = CustomCommand(self.config)

    async def setup(self):
        await self.register_command(self.command)
```

## Testing

### Unit Tests

```python
# tests/test_custom.py
import pytest
from modules.custom.module import CustomModule

def test_custom_module():
    module = CustomModule()
    assert module.name == "custom"
    assert module.config.is_enabled
```

### Integration Tests

```python
# tests/integration/test_custom.py
import pytest
from tests.helpers import TestBot

async def test_custom_command():
    bot = TestBot()
    module = CustomModule()
    await module.setup(bot)
    
    # Test command
    result = await bot.simulate_command("custom")
    assert result.content == "Success!"
```

## Deployment

1. Update version
2. Run tests
3. Update docs
4. Deploy changes

## Maintenance

1. Monitor logs
2. Check performance
3. Update dependencies
4. Review feedback 