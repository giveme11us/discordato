# Discord Bot Project Documentation

## Overview

This project implements a modular Discord bot system capable of managing multiple functional modules with different configurations. The bot can operate in three different scenarios based on Discord token configuration:

1. **Single Bot Mode**: One token for all modules
2. **Multi-Bot Mode**: Different tokens for each module
3. **Partial Mode**: Only modules with valid tokens are activated

The system is designed to be highly modular, allowing for easy addition of new modules and commands without modifying the core bot framework.

## Project Structure

```
discord_bot_project/
│
├── discord_bot.py            # Main entry point
├── .env                      # Environment variables file
├── config/
│   ├── __init__.py
│   ├── core/                # Core configuration
│   │   ├── __init__.py
│   │   ├── settings.py      # General configuration settings
│   │   └── environment.py   # Environment variables loader
│   └── features/            # Feature-specific configuration
│       ├── __init__.py
│       ├── moderation.py    # Moderation settings
│       ├── reactions.py     # Reaction settings
│       ├── redeye_config.py # Redeye module settings
│       ├── embed_config.py  # Embed settings
│       ├── global_whitelist.py # Whitelist settings
│       └── pinger_config.py # Pinger settings
│
├── modules/
│   ├── __init__.py
│   ├── core/               # Core functionality
│   │   ├── __init__.py
│   │   ├── bot_manager.py  # Bot initialization and lifecycle manager
│   │   ├── command_sync.py # Handles Discord slash command registration
│   │   ├── command_router.py # Routes commands to appropriate modules
│   │   └── module_loader.py # Dynamically loads modules
│   │
│   └── features/           # Feature modules
│       ├── __init__.py
│       ├── keyword_filter/ # Keyword filtering functionality
│       ├── link_reaction/  # Link reaction handling
│       ├── reaction_forward/ # Message forwarding
│       ├── pinger/        # Mention monitoring
│       └── redeye/        # Redeye functionality
│
├── utils/
│   ├── __init__.py
│   ├── logger.py          # Logging functionality
│   └── helpers.py         # Common helper functions
│
├── tools/                 # Development and maintenance tools
│   ├── code_formatters/   # Code formatting utilities
│   └── debug/            # Debugging tools
│
└── tests/                # Test files
    ├── __init__.py
    ├── data/            # Test data files
    ├── test_bot_manager.py
    ├── test_modules.py
    └── test_commands.py
```

## Environment Configuration

The `.env` file should contain the following variables:

```
# Main bot token (required)
DISCORD_BOT_TOKEN=your_main_bot_token

# Module-specific tokens (optional)
MOD_BOT_TOKEN=your_mod_bot_token
ONLINE_BOT_TOKEN=your_online_bot_token
INSTORE_BOT_TOKEN=your_instore_bot_token

# Additional configuration
LOG_LEVEL=INFO
COMMAND_PREFIX=/
```

## Core Components

### Bot Manager

The Bot Manager is responsible for:
- Loading environment variables
- Determining the running scenario (single bot, multi-bot, or partial)
- Initializing the appropriate bot instances
- Managing bot lifecycle
- Error handling and recovery

### Command Sync

The Command Sync component handles:
- Registering slash commands with Discord API
- Managing command permissions
- Handling command updates and deletions
- Resolving command conflicts across modules

### Command Router

The Command Router:
- Receives incoming Discord commands
- Identifies the target module and command
- Routes commands to the appropriate handler
- Manages error responses

### Module Loader

The Module Loader:
- Dynamically discovers and loads modules
- Validates module structure and requirements
- Manages module dependencies
- Handles module conflicts

## Module Structure

Each module follows a consistent structure:

1. **module.py**: Defines the module configuration, including:
   - Module name and description
   - Required permissions
   - Command groups and categories
   - Event handlers

2. **Command Files**: Each command is in its own file, containing:
   - Command registration information
   - Parameter definitions
   - Execution logic
   - Error handling

## Operational Scenarios

### Scenario 1: Single Bot Mode

When `DISCORD_BOT_TOKEN` is set and all module-specific tokens are either identical to the main token or not set:

- A single bot instance is created
- All modules are loaded under this instance
- Commands from all modules are registered under the single bot
- The command router directs commands to appropriate modules

### Scenario 2: Multi-Bot Mode

When different tokens are provided for each module:

- Multiple bot instances are created, one per module
- Each bot loads only its designated module
- Commands are registered separately for each bot
- No command routing is needed as each bot handles its own commands

### Scenario 3: Partial Mode

When tokens are missing for some modules:

- Only modules with valid tokens are loaded
- Bot instances are created according to token configuration
- Only commands from active modules are registered
- The system logs warnings for disabled modules

## Command Implementation

Commands should be implemented in individual files following this pattern:

- Each command file defines the command properties and handler function
- Commands are organized into their respective module directories
- Sub-commands or command groups are organized into subdirectories
- Each command file should be self-contained and independent

## Extension Points

The system is designed to be easily extended in several ways:

1. **Adding New Modules**:
   - Create a new directory under `modules/`
   - Add a `module.py` file with module configuration
   - Add command files for the module

2. **Adding New Commands**:
   - Create a new command file in the appropriate module directory
   - Command is automatically discovered and registered

3. **Custom Event Handlers**:
   - Modules can define custom event handlers in their `module.py`
   - Events are automatically registered with the appropriate bot instance

## Error Handling

The system implements comprehensive error handling:

- Command execution errors are caught and reported to users
- Module loading errors are logged but don't crash the system
- Network and Discord API errors are handled with retry logic
- Configuration errors provide clear diagnostics

## Logging

Logging is implemented throughout the system:

- Application startup and shutdown events
- Command execution and errors
- Module loading and initialization
- Discord API interactions
- Performance metrics

## Development Workflow

1. **Adding a New Command**:
   - Create a new file in the appropriate module directory
   - Implement the command handler
   - Restart the bot or use the reload command

2. **Adding a New Module**:
   - Create a new module directory
   - Add `module.py` with required configuration
   - Add command files
   - Update environment variables if needed
   - Restart the bot

3. **Testing**:
   - Use the built-in testing framework
   - Test commands individually
   - Test scenario handling
   - Test error conditions

## Deployment

The application can be deployed in several ways:

1. **Docker**:
   - A Dockerfile is provided
   - Environment variables can be passed via Docker environment

2. **Traditional Deployment**:
   - Install dependencies from requirements.txt
   - Configure the .env file
   - Run discord_bot.py

3. **Development Mode**:
   - Set `DEVELOPMENT=True` in the .env file
   - Commands are synced immediately after changes
   - Additional debugging is enabled

## Maintenance

Regular maintenance tasks include:

- Updating Discord.py dependencies
- Reviewing Discord API changes
- Monitoring command usage
- Optimizing performance
- Backing up configurations

## Security Considerations

- Bot tokens are handled securely using environment variables
- Permission handling follows the principle of least privilege
- Commands implement appropriate validation
- Rate limiting is implemented to prevent abuse
