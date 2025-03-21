# Installation Guide

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git
- A Discord account and application
- Basic knowledge of terminal/command line

## Step 1: Discord Application Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and name your bot
3. Go to the "Bot" section and click "Add Bot"
4. Copy your bot token (you'll need this later)
5. Enable necessary Privileged Gateway Intents:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent

## Step 2: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/discord-bot.git
cd discord-bot

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

## Step 4: Configuration

1. Create a `.env` file in the project root:
```bash
cp .env.example .env
```

2. Edit `.env` with your settings:
```env
# Required Settings
DISCORD_TOKEN=your_bot_token_here
GUILD_IDS=server_id1,server_id2

# Feature Settings
EMBED_COLOR=57fa1
MOD_WHITELIST_ROLE_IDS=role_id1,role_id2
REDEYE_WHITELIST_ROLE_IDS=role_id3,role_id4

# Optional Settings
LOG_LEVEL=INFO
COMMAND_PREFIX=!
```

## Step 5: Database Setup (Optional)
If using database features:
```bash
# Initialize database
python tools/db_init.py
```

## Step 6: Run the Bot

```bash
# Start the bot
python discord_bot.py
```

## Step 7: Invite Bot to Server

1. Go back to Discord Developer Portal
2. Select your application
3. Go to OAuth2 → URL Generator
4. Select scopes:
   - `bot`
   - `applications.commands`
5. Select required permissions:
   - Send Messages
   - Manage Messages
   - Read Message History
   - Add Reactions
   - (Add other permissions as needed)
6. Copy and use the generated URL to invite the bot

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**
   ```
   Solution: Ensure you're in the virtual environment and have run pip install
   ```

2. **Discord.py Errors**
   ```
   Solution: Check if you've enabled the required intents
   ```

3. **Permission Errors**
   ```
   Solution: Verify bot role permissions in your Discord server
   ```

### Environment Setup Issues

1. **Virtual Environment**
   ```bash
   # If venv creation fails:
   python -m pip install --upgrade pip
   python -m pip install virtualenv
   ```

2. **Package Installation**
   ```bash
   # If pip install fails:
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

## Next Steps

1. Read the [Configuration Guide](configuration.md) for detailed setup
2. Check the [Command Reference](commands.md) for available commands
3. Visit [Troubleshooting](troubleshooting.md) if you encounter issues

## Development Setup

For developers who want to contribute:

1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

3. Configure your IDE:
   - Use Python 3.8+
   - Enable linting (flake8)
   - Enable type checking (mypy)
   - Set up black formatter

## Security Notes

- Never share your bot token
- Keep `.env` file secure
- Regularly update dependencies
- Monitor bot permissions

## Support

If you need help:
1. Check the documentation
2. Search existing issues
3. Create a new issue with:
   - Python version
   - OS details
   - Error messages
   - Steps to reproduce 