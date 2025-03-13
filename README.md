# Discord Bot Project

A modular Discord bot system capable of managing multiple functional modules with different configurations.

## Features

- **Modular Design**: Easily add new modules and commands without modifying the core framework
- **Multiple Operational Modes**:
  - **Single Bot Mode**: One token for all modules
  - **Multi-Bot Mode**: Different tokens for each module
  - **Partial Mode**: Only modules with valid tokens are activated
- **Slash Command Support**: Modern Discord interactions using slash commands
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Flexible Configuration**: Environment-based configuration for easy deployment
- **Command Registration System**: Robust system to prevent duplicate command registration

## Project Structure

```
discord_bot_project/
│
├── discord_bot.py            # Main entry point
├── .env                      # Environment variables file
├── config/                   # Configuration settings
├── core/                     # Core bot framework
│   ├── bot_manager.py        # Bot initialization and lifecycle manager
│   ├── command_sync.py       # Handles Discord slash command registration
│   ├── command_router.py     # Routes commands to appropriate modules
│   ├── module_loader.py      # Dynamically loads modules
│   └── command_registry.py   # Central registry for all commands
├── modules/                  # Functional modules
│   ├── mod/                  # Moderation module
│   ├── online/               # Online interaction module
│   └── instore/              # In-store interaction module
├── utils/                    # Utility functions
└── tests/                    # Test files
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/giveme11us/discordato.git
   cd discordato
   ```

2. Install dependencies:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on the `.env.example` template:
   ```
   cp .env.example .env
   ```

4. Edit the `.env` file with your Discord bot tokens and configuration:
   ```
   # Main bot token (required)
   DISCORD_BOT_TOKEN=your_token_here
   
   # Application ID (required for slash commands)
   APPLICATION_ID=your_app_id_here
   
   # Guild IDs for development
   GUILD_IDS=guild_id1,guild_id2
   ```

## Usage

### Running the Bot

```
python discord_bot.py
```

### Command Line Arguments

- `--config`: Path to the configuration file (default: `.env`)
- `--debug`: Enable debug mode for more detailed logging

Example:
```
python discord_bot.py --config custom.env --debug
```

### Registering Commands

The bot automatically registers slash commands when it starts, but you can also manually register them:

```
python register_commands.py
```

## Adding New Modules

1. Create a new directory under `modules/`:
   ```
   mkdir -p modules/new_module
   ```

2. Create a `module.py` file with setup and teardown functions:
   ```python
   def setup(bot, registered_commands=None):
       # Initialize registered_commands if not provided
       if registered_commands is None:
           registered_commands = set()
           
       # Register commands if not already registered
       if 'command_name' not in registered_commands:
           # Register your command
           pass
   
   def teardown(bot):
       # Clean up resources
       pass
   ```

3. Add command files to the module directory.

4. Update the `ENABLED_MODULES` setting in your `.env` file.

## Adding New Commands

1. Add the command to the central registry in `core/command_registry.py`:
   ```python
   # Register your new command
   @bot.tree.command(
       name="command_name",
       description="Command description"
   )
   async def command_name(interaction: discord.Interaction):
       # Command implementation
       pass
   ```

2. Create a command file in the appropriate module directory:
   ```python
   async def command_handler(interaction):
       # Command implementation
       pass
   
   def setup_command(bot):
       @bot.tree.command(
           name="command_name",
           description="Command description"
       )
       async def command(interaction):
           await command_handler(interaction)
   ```

3. Import and register the command in the module's `module.py` file.

## Troubleshooting

### Command Syncing Issues

If you encounter issues with commands not being synced to Discord:

1. Ensure your bot has the proper permissions:
   - Go to Discord Developer Portal → Your Application → Bot
   - Enable "MESSAGE CONTENT INTENT"
   - Under OAuth2 → URL Generator, select "bot" and "applications.commands" scopes

2. Verify your APPLICATION_ID is correctly set in .env file

3. Try manually syncing commands:
   ```
   python register_commands.py
   ```

4. Check the logs for any errors.

## Testing

Run tests using pytest:
```
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.


# Navigate to your project directory
cd your_project_directory

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# When done, deactivate the environment
deactivate