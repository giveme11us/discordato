# Modules Documentation

This document describes the available modules and their functionality.

## Core Modules

### Moderation (`mod`)
The moderation module provides tools for server management:
- Role-based access control
- Command restrictions
- Logging of moderation actions
- Auto-moderation features

### Link Reaction (`link_reaction`)
Handles link detection and reactions:
- Detects posted links
- Adds configurable reactions
- Forwards links to notification channels
- Logs link activity

### Pinger (`pinger`)
Monitors and notifies about mentions:
- Tracks @everyone, @here, and role mentions
- Configurable notification channels
- Mention statistics and logging
- Role-based monitoring settings

### RedEye (`redeye`)
Manages late-night notifications:
- Configurable quiet hours
- Role-based notifications
- Custom message formatting
- Time zone support

## Module Development

To create a new module:

1. Create a new directory in `modules/`
2. Implement the required interfaces:
   - `ModuleBase` for core functionality
   - `ConfigurableModule` for configuration support
3. Register the module in `modules/__init__.py`
4. Add configuration in `config/features/`
5. Create documentation in `data/docs/`

Example module structure:
```
modules/
  └── new_module/
      ├── __init__.py
      ├── module.py
      ├── config.py
      └── utils.py
```

## Configuration

Each module can define its configuration in `config/features/`:
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
        # Implement validation logic
        return True
```

## Testing

Modules should include comprehensive tests:
```python
def test_module():
    module = NewModule()
    assert module.is_enabled()
    # Add more test cases
```

## Best Practices

1. Keep modules focused and single-purpose
2. Document all public interfaces
3. Include error handling
4. Add logging for important events
5. Make configuration flexible
6. Write comprehensive tests
