# Modules API Documentation

## Overview

The module system provides a flexible architecture for extending bot functionality through independent modules. Each module must implement a standard interface for setup and teardown.

### Module Types

1. **Core Modules**
   - Essential bot functionality
   - System-level operations
   - Framework services

2. **Feature Modules**
   - User-facing functionality
   - Command implementations
   - Specific bot features

## Core Modules

### Command Router (`core/command_router.py`)

Manages command registration and routing.

```python
from core.command_router import CommandRouter

router = CommandRouter(bot)
router.register_command(command)
router.register_group("group_name", "description")
```

#### Key Methods
- `register_command(command)`: Register a new command
- `register_group(name, description)`: Create command group
- `get_command(name)`: Retrieve registered command
- `get_group(name)`: Retrieve command group

### Command Sync (`core/command_sync.py`)

Handles Discord slash command synchronization.

```python
from core.command_sync import CommandSync

sync = CommandSync()
sync.register_module_commands(bot)
```

#### Key Methods
- `register_module_commands(bot)`: Register all module commands
- `sync_commands(bot, bot_name)`: Sync commands with Discord

### Error Handler (`core/error_handler.py`)

Provides centralized error handling.

```python
from core.error_handler import ErrorHandler, BotError

class CustomError(BotError):
    pass

handler = ErrorHandler(bot)
```

#### Key Classes
- `BotError`: Base exception class
- `CommandError`: Command execution errors
- `PermissionError`: Permission-related errors
- `ConfigurationError`: Configuration errors
- `ValidationError`: Input validation errors
- `DatabaseError`: Database operation errors

### Logging System (`core/logging.py`)

Implements structured logging with JSON formatting.

```python
from core.logging import BotLogger

logger = BotLogger()
logger.get_logger("module_name")
```

#### Key Features
- Structured JSON log output
- Log file rotation
- Multiple log levels
- Command and error tracking

## Feature Modules

### Mod Module (`modules/mod/`)

Moderation and configuration management.

#### Commands
- `/keyword-filter-config`: Configure keyword filtering
  - View/modify filter settings
  - Manage categories and blacklists
  - Configure notifications
  - Toggle dry run mode

- `/mod-config`: Module-wide settings
  - Manage whitelist roles
  - View current settings
  - Add/remove roles
  - Clear configurations

- `/purge`: Message deletion
  - Delete specified number of messages
  - Requires manage messages permission

### Redeye Module (`modules/redeye/`)

Profile and task management.

#### Commands
- `/redeye-profiles`: Profile management
- `/redeye_help`: Module help information

## Module Development

### Creating New Modules

1. **Module Structure**
   ```
   modules/
   └── new_module/
       ├── __init__.py
       ├── module.py
       └── commands/
   ```

2. **Module Interface**
   ```python
   def setup(bot, registered_commands=None):
       """Initialize module and register commands."""
       if registered_commands is None:
           registered_commands = set()
       # Register commands
       return registered_commands

   def teardown(bot):
       """Cleanup module resources."""
       pass
   ```

### Best Practices

1. **Command Registration**
   - Check for existing commands
   - Use descriptive names
   - Implement permission checks
   - Handle errors properly

2. **Resource Management**
   - Clean initialization
   - Proper cleanup
   - Resource tracking
   - Error recovery

## Configuration

### Environment Variables
```env
# Module Settings
MOD_ENABLED=True
REDEYE_ENABLED=True
```

### Module Settings
```python
# Module-specific settings
MOD_SETTINGS = {
    'whitelist_roles': [],
    'filters': {}
}
```

## Error Handling

### Module Errors
```python
class ModuleError(Exception):
    """Base module error."""
    pass

try:
    await module.process()
except ModuleError as e:
    await handle_module_error(e)
```

## Notes

- Modules must implement setup/teardown
- Use proper error handling
- Document public interfaces
- Follow command registration pattern
