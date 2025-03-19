# Discord Bot Configuration System

This directory contains the configuration modules for the Discord bot.

## Configuration Architecture

The configuration system is designed with the following principles:

1. **Separation of Core Environment Variables and User Settings**
   - Core environment variables (tokens, IDs) remain in `.env`
   - User-configurable settings are stored in JSON files

2. **Centralized Settings Management**
   - All user-configurable settings are stored in `data/settings/*.json`
   - Each module has its own settings file (e.g., `keyword_filter.json`)

3. **Configuration Property System**
   - Settings are accessed through Python properties
   - Provides type checking and validation
   - Changes are automatically saved to storage

## Module Configuration Files

### Core Configuration Files

- `settings_manager.py` - Central settings management system
- `mod_config.py` - Shared configuration for moderation modules
- `environment.py` - Environment variable loading
- `settings.py` - Global settings and constants

### Module-Specific Configuration Files

- `keyword_filter_config.py` - Configuration for keyword filtering
- `link_reaction_config.py` - Configuration for link reaction
- `reaction_forward_config.py` - Configuration for message forwarding
- `pinger_config.py` - Configuration for mention monitoring
- `redeye_config.py` - Configuration for the redeye waitlist system

## Configuration Format

Each module's configuration is stored in a JSON file in the `data/settings` directory:

```
data/
  settings/
    keyword_filter.json
    link_reaction.json
    reaction_forward.json
    pinger.json
    redeye.json
```

## Management Tools

### `manage_settings.py`

A utility script for managing settings:

```bash
# List all settings
python manage_settings.py list

# List settings for a specific module
python manage_settings.py list --module keyword_filter

# Export all settings to a file
python manage_settings.py export settings_backup.json

# Import settings from a file
python manage_settings.py import settings_backup.json

# Reset settings to defaults
python manage_settings.py reset

# Validate settings structure
python manage_settings.py validate
```

## Using the Configuration System in Code

```python
# Import a module's configuration
import config.keyword_filter_config as keyword_filter_config

# Access configuration values through properties
if keyword_filter_config.ENABLED:
    # Do something with the configuration
    notification_channel_id = keyword_filter_config.NOTIFICATION_CHANNEL_ID
    
# Update configuration values
keyword_filter_config.ENABLED = True
keyword_filter_config.NOTIFICATION_CHANNEL_ID = 123456789

# Configuration is automatically saved when properties are updated
```

## Setting Manager API

The `settings_manager.py` module provides a central API for managing settings:

```python
from config.settings_manager import get_manager

# Get a settings manager for a module
manager = get_manager("my_module", default_settings={})

# Load settings
settings = manager.load_settings()

# Get a setting value
value = manager.get("key", default="default value")

# Set a setting value
manager.set("key", "value")

# Update multiple settings
manager.update({"key1": "value1", "key2": "value2"})

# Reset settings to defaults
manager.reset()
```

## Adding a New Configuration Module

To add configuration for a new module:

1. Create a new configuration file in the `config` directory
2. Define default settings as a dictionary
3. Use the settings manager to get/set values
4. Create properties for type-safe access

Example:

```python
from config.settings_manager import get_manager

# Default settings
DEFAULT_CONFIG = {
    "ENABLED": True,
    "SOME_SETTING": "default value"
}

# Initialize settings manager
settings_manager = get_manager("my_module", DEFAULT_CONFIG)

# Create properties
@property
def ENABLED() -> bool:
    return settings_manager.get("ENABLED", True)

@ENABLED.setter
def ENABLED(value: bool):
    settings_manager.set("ENABLED", bool(value))

# Save config function
def save_config() -> bool:
    return settings_manager.save_settings()
``` 