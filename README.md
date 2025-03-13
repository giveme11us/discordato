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
- **Pinger Notification System**: Monitors `@everyone` and `@here` mentions and sends notifications to a dedicated channel. A whitelist system allows specific roles to use mentions without triggering notifications. The notification channel and monitoring settings are configurable.
- **Reaction Forward System**: Automatically adds a ➡️ reaction to messages in specified category channels. This can be used to visually mark messages for forwarding or to indicate that a message requires attention. The categories to monitor are fully configurable.
- **Message Forwarding System**: Users with whitelisted roles can forward messages to the notification channel by reacting with ➡️. Forwards all types of messages including regular user messages, webhook messages, and app messages. Uses Discord's official message forwarding feature, preserving the original author's name and avatar while showing who forwarded the message and the message source. Attachments and embeds from the original message are also included.
- **Link Reaction System**: Automatically adds a 🔗 link emoji to messages containing embeds from supported stores (like LUISAVIAROMA) in specified category channels. The bot will only add the reaction if it detects content from supported stores, optimizing the user experience by only highlighting relevant content.
  - **Store Product ID Extraction**: When whitelisted users react with the 🔗 link emoji to embeds from specific stores, the bot extracts product IDs and saves them to configured files:
    - **LUISAVIAROMA**: Extracts product IDs from embeds with author "LUISAVIAROMA" and saves them to a file specified in the `luisaviaroma_drops_urls_path` environment variable.

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

3. Try manually syncing commands with the dedicated script:
   ```
   python register_commands.py
   ```
   This script directly communicates with Discord's API to register commands.

4. If commands still don't appear, try resetting all commands first:
   ```
   python reset_commands.py
   ```
   This will remove all existing commands, then you can register them again.

5. Check the logs for any errors.

6. Be patient - changes to slash commands can sometimes take up to an hour to propagate in Discord.

## Testing

Run tests using pytest:
```
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Pinger Module

The Pinger module monitors mentions in Discord messages (@everyone, @here, and role mentions) and sends notifications to a designated channel. This helps administrators keep track of important mentions across the server.

### Features

- Monitors @everyone, @here, and role mentions
- Sends notifications with embed messages to a designated channel
- Whitelist system ensures only authorized users can trigger notifications
- Jump button allows quick navigation to the original message
- Fully configurable through environment variables or the `/pinger-config` command

### Configuration

You can configure the Pinger module in two ways:

1. **Using the `/pinger-config` command** (recommended):
   - `/pinger-config` - Shows current configuration
   - `/pinger-config channel #channel-name` - Sets the notification channel
   - `/pinger-config whitelist add @role` - Adds a role to the whitelist
   - `/pinger-config whitelist remove @role` - Removes a role from the whitelist
   - `/pinger-config whitelist clear` - Clears the entire whitelist
   - `/pinger-config everyone true|false` - Enables/disables @everyone monitoring
   - `/pinger-config here true|false` - Enables/disables @here monitoring
   - `/pinger-config roles true|false` - Enables/disables role mention monitoring

   *Note: All changes made via the command will persist in the .env file*

2. **Directly in your `.env` file**:
   ```env
   # Pinger Feature Settings
   # Channel ID where ping notifications will be sent
   PINGER_NOTIFICATION_CHANNEL_ID=969208183799296030
   # Comma-separated list of role IDs that CAN trigger notifications
   PINGER_WHITELIST_ROLE_IDS=811975979492704337,811975812596498482
   # Whether to monitor @everyone pings
   PINGER_MONITOR_EVERYONE=True
   # Whether to monitor @here pings
   PINGER_MONITOR_HERE=True
   # Whether to monitor role pings
   PINGER_MONITOR_ROLES=True
   ```

### Embed Customization

The notification embeds can be customized using the global embed settings:

```env
# Global Embed Customization Settings
# Single color for all embeds (hex format without the # symbol)
EMBED_COLOR=00ff1f
# Footer settings
EMBED_FOOTER_TEXT=Discord Bot
EMBED_FOOTER_ICON_URL=https://example.com/footer-icon.png
# Thumbnail settings
EMBED_THUMBNAIL_URL=https://example.com/thumbnail.png
# General settings
EMBED_DEFAULT_TITLE=Notification
EMBED_INCLUDE_TIMESTAMP=True
```

# Quick Start

```bash
# Navigate to your project directory
cd your_project_directory

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the bot
python discord_bot.py

# When done, deactivate the environment
deactivate
```