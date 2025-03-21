# Configuration System

This directory contains the configuration system for the Discord bot.

## Structure

- `core/` - Core configuration functionality
- `features/` - Feature-specific configuration
- `data/` - Configuration data files

## Configuration Files

Each module has its own settings file (e.g., `link_reaction.json`, `pinger.json`) stored in the `data/` directory.

## Configuration Classes

### Core

- `base_config.py` - Base configuration class with common functionality
- `environment.py` - Environment variable handling
- `validation.py` - Configuration validation utilities

### Features

- `moderation.py` - Configuration for moderation features
- `pinger_config.py` - Configuration for ping monitoring
- `link_reaction_config.py` - Configuration for link reactions
- `reaction_forward_config.py` - Configuration for message forwarding

## Usage

### Loading Configuration

```python
from config.features.moderation import mod_config

if mod_config.ENABLED:
    # Initialize moderation features
    notification_channel_id = mod_config.NOTIFICATION_CHANNEL_ID
```

### Modifying Configuration

```python
from config.features.link_reaction import link_reaction_config

link_reaction_config.ENABLED = True
link_reaction_config.NOTIFICATION_CHANNEL_ID = 123456789
```

### Managing Settings

Use the `manage_settings.py` script to:
- Export settings to a file
- Import settings from a file
- Reset settings to defaults
- Validate settings structure

Example:
```bash
python manage_settings.py list --module link_reaction
python manage_settings.py reset --module pinger
python manage_settings.py validate
```

## Development

When adding new configuration options:

1. Create a new configuration class in the appropriate module
2. Inherit from `BaseConfig`
3. Define properties with validation
4. Add default values
5. Update documentation

Example:
```python
from config.core.base_config import BaseConfig

class MyFeatureConfig(BaseConfig):
    def __init__(self):
        super().__init__('my_feature.json', DEFAULT_CONFIG)
        
    @property
    def ENABLED(self) -> bool:
        return self.get('enabled', False)
``` 