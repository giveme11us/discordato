# Configuration System Migration

## Overview

The bot's configuration system has been redesigned to better separate core environment variables from user-configurable settings. This migration moves all user-configurable settings to JSON files, making it easier to manage and modify configurations.

## Changes

1. **New Configuration Structure**
   - **Environment Variables** (`.env`): Core settings like tokens and IDs
   - **Settings Files** (`data/settings/*.json`): User-configurable settings

2. **Centralized Settings Manager**
   - All configuration is now managed through a central `settings_manager.py` module
   - Each module has its own settings file (e.g., `keyword_filter.json`)
   - Settings are automatically loaded and saved

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
   - No more mix of environment variables and JSON files
   - Each module has a clearly defined set of settings
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

The following modules now have their own configuration files:

| Module | Settings File | Description |
|--------|---------------|-------------|
| Keyword Filter | `keyword_filter.json` | Message filtering settings |
| Link Reaction | `link_reaction.json` | Link reaction settings and store rules |
| Reaction Forward | `reaction_forward.json` | Message forwarding settings |
| Pinger | `pinger.json` | Mention monitoring settings |

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
- [x] Update keyword filter configuration
- [x] Update link reaction configuration
- [x] Update reaction forward configuration
- [x] Update pinger configuration
- [x] Create migration and management tools
- [x] Document new configuration system
- [ ] Clean up deprecated configuration files
- [ ] Test across all modules 