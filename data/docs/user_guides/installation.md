# Installation Guide

This guide will walk you through the process of setting up and running the Discord bot framework.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package installer)
- Git (for version control)
- A Discord account and application token

## Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/discord-bot.git
cd discord-bot

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

## Step 2: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# For development, install additional dependencies
pip install -r requirements-dev.txt
```

## Step 3: Configure the Bot

1. Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your configuration:
   ```env
   # Required: Your Discord bot token
   DISCORD_BOT_TOKEN=your_token_here
   
   # Optional: Module-specific tokens for multi-bot mode
   MOD_TOKEN=token_for_mod_module
   ONLINE_TOKEN=token_for_online_module
   
   # Configure enabled modules
   ENABLED_MODULES=mod,online,instore
   
   # Additional settings
   COMMAND_PREFIX=!
   BOT_DESCRIPTION="Your Bot Description"
   ```

## Step 4: Initialize the Database

```bash
# Run database initialization script
python manage_settings.py init
```

## Step 5: Start the Bot

```bash
# Start in development mode
python discord_bot.py --dev

# Or start in production mode
python discord_bot.py
```

## Configuration Options

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| DISCORD_BOT_TOKEN | Main bot token | Yes | None |
| ENABLED_MODULES | Active modules | No | "mod" |
| COMMAND_PREFIX | Command prefix | No | "!" |
| BOT_DESCRIPTION | Bot description | No | "Discord Bot" |

### Module Configuration

Each module may require additional configuration in the `.env` file. Check the module's documentation for specific requirements.

## Development Setup

For development, additional tools are recommended:

1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

3. Configure your IDE:
   - Enable Python type checking
   - Use the project's `.editorconfig`
   - Set up linting with flake8

## Troubleshooting

### Common Issues

1. **Token Invalid**
   - Verify your Discord token is correct
   - Ensure the bot is added to your server
   - Check token permissions

2. **Module Not Loading**
   - Verify module is in ENABLED_MODULES
   - Check module-specific configuration
   - Look for error messages in logs

3. **Command Sync Failed**
   - Ensure bot has required permissions
   - Check Discord API status
   - Verify slash command configuration

### Getting Help

If you encounter issues:
1. Check the logs in `discord_bot.log`
2. Review the troubleshooting guide
3. Open an issue on GitHub
4. Join our Discord support server

## Next Steps

After installation:
1. Review the [Configuration Guide](configuration.md)
2. Explore available [Features](features.md)
3. Join the development community
4. Consider contributing to the project

## Security Notes

- Keep your `.env` file secure
- Never commit tokens to version control
- Regularly rotate your tokens
- Monitor bot activity and logs
