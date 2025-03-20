# Configuration System Migration

## Overview

The bot's configuration system has been redesigned to better separate core environment variables from user-configurable settings. This migration moves all user-configurable settings to a structured configuration system with clear separation between core and feature-specific settings.

## Changes

1. **New Configuration Structure**
   - **Environment Variables** (`.env`): Core settings like tokens and IDs
   - **Core Configuration** (`config/core/`): Essential bot settings
   - **Feature Configuration** (`config/features/`): Module-specific settings

2. **Configuration Organization**
   - Core settings in `config/core/`
     - `settings.py`: General configuration settings
     - `environment.py`: Environment variables loader
   - Feature settings in `config/features/`
     - `moderation.py`: Moderation settings
     - `reactions.py`: Reaction settings
     - `redeye_config.py`: Redeye module settings
     - `embed_config.py`: Embed settings
     - `global_whitelist.py`: Whitelist settings
     - `pinger_config.py`: Pinger settings

3. **Improved Type Safety**
   - Configuration values are accessed through Python properties
   - Type checking and validation is enforced
   - Changes are automatically persisted

4. **Settings Management Tools**
   - New `manage_settings.py` utility for managing settings
   - Export/import settings for backup and migration
   - Reset to defaults and validate settings structure

## Migration Benefits

1. **Cleaner Configuration**
   - Clear separation between core and feature settings
   - Each feature has its own configuration file
   - Settings are stored in a consistent format

2. **Easier to Manage**
   - Edit settings directly through commands
   - Better error handling and validation
   - Automatic type conversion

3. **Better Developer Experience**
   - Type hints for configuration values
   - Clear property-based API
   - Consistent patterns across modules

## Module Configurations

The following modules now have their own configuration files in `config/features/`:

| Module | Settings File | Description |
|--------|---------------|-------------|
| Moderation | `moderation.py` | Moderation settings and rules |
| Reactions | `reactions.py` | Reaction handling settings |
| Redeye | `redeye_config.py` | Redeye module settings |
| Embed | `embed_config.py` | Message embed settings |
| Whitelist | `global_whitelist.py` | Global whitelist settings |
| Pinger | `pinger_config.py` | Mention monitoring settings |

## Updating Commands

All Discord slash commands have been updated to use the new configuration system. No changes to command usage are required.

## Tools

### Settings Management Script

```bash
# List all settings
python manage_settings.py list

# Export settings to a backup file
python manage_settings.py export backup.json

# Import settings from a backup file
python manage_settings.py import backup.json

# Reset settings to defaults
python manage_settings.py reset

# Validate settings structure
python manage_settings.py validate
```

### Cleanup Script

```bash
# Cleanup unused files and directories
python cleanup.py
```

## Migration Checklist

- [x] Create centralized settings manager
- [x] Update core configuration structure
- [x] Update feature configuration structure
- [x] Create migration and management tools
- [x] Document new configuration system
- [ ] Clean up deprecated configuration files
- [ ] Test across all modules 