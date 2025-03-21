# Installation Guide

## Prerequisites

Before installing the bot, ensure you have the following prerequisites:

1. **Python 3.8+**
   - Download from [python.org](https://python.org)
   - Verify installation: `python --version`

2. **pip (Python package manager)**
   - Usually comes with Python
   - Verify installation: `pip --version`

3. **Git**
   - Download from [git-scm.com](https://git-scm.com)
   - Verify installation: `git --version`

4. **Discord Developer Account**
   - Create at [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Create a bot user
   - Get your bot token

## Installation Steps

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/discord-bot.git

# Navigate to project directory
cd discord-bot
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_bot_token_here
APPLICATION_ID=your_app_id_here

# Enabled Modules
ENABLED_MODULES=mod,online,instore,redeye

# Moderation Settings
MOD_WHITELIST_ROLE_IDS=role_id1,role_id2
MOD_LOG_CHANNEL_ID=channel_id

# Pinger Settings
PINGER_NOTIFICATION_CHANNEL_ID=channel_id
PINGER_MONITOR_EVERYONE=True
PINGER_MONITOR_HERE=True
PINGER_MONITOR_ROLES=True

# Link Reaction Settings
LINK_REACTION_ENABLED=True
LINK_REACTION_NOTIFICATION_CHANNEL_ID=channel_id
LINK_REACTION_LOG_CHANNEL_ID=channel_id
```

### 5. Initialize the Bot

```bash
# Start the bot
python discord_bot.py
```

## Module Configuration

### Core Modules
Core modules are installed by default:
- Command Router
- Command Sync
- Error Handler
- Logging System

### Feature Modules

1. **Mod Module**
   ```env
   # Enable mod module
   ENABLED_MODULES=mod
   ```

2. **Redeye Module**
   ```env
   # Enable redeye module
   ENABLED_MODULES=redeye
   ```

## Discord Setup

### 1. Create Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Name your application
4. Save the Application ID

### 2. Create Bot User

1. Go to "Bot" section
2. Click "Add Bot"
3. Save the Bot Token
4. Enable required Intents:
   - Message Content Intent
   - Server Members Intent
   - Presence Intent

### 3. Invite Bot to Server

1. Go to "OAuth2" section
2. Select "bot" scope
3. Select required permissions:
   - Manage Messages
   - Read Messages/View Channels
   - Send Messages
   - Read Message History
   - Add Reactions
4. Copy and use the generated URL

## Post-Installation

### 1. Verify Bot Status

1. Check bot is online in Discord
2. Test basic commands:
   ```
   /ping - Check bot latency
   /help - View available commands
   ```
3. Check log files in `logs/` directory

### 2. Configure Modules

1. Configure mod module:
   ```
   /mod-config - Configure moderation settings
   /pinger-config - Configure mention monitoring
   /link-reaction-config - Configure link reactions
   ```

2. Configure redeye module:
   ```
   /redeye-profiles - Manage profiles
   /redeye_help - View module help
   ```

## Troubleshooting

### Common Issues

1. **Bot Won't Start**
   - Check `.env` configuration
   - Verify bot token
   - Check Python version
   - Check dependencies

2. **Command Sync Issues**
   - Verify guild IDs
   - Check bot permissions
   - Enable required intents
   - Check error logs

3. **Module Issues**
   - Check module is enabled
   - Verify permissions
   - Check configuration
   - Review logs

## Security Notes

1. **Token Security**
   - Never share bot token
   - Use environment variables
   - Rotate if compromised
   - Monitor access

2. **Permission Management**
   - Use minimal permissions
   - Regular audit
   - Monitor changes
   - Document access

## Notes

- Keep documentation updated
- Monitor Discord updates
- Regular security checks
- Maintain backups
- Test regularly

## Updates

To update the bot:

1. Pull the latest changes:
```bash
git pull origin main
```

2. Update dependencies:
```bash
pip install -r requirements.txt
```

3. Check for new environment variables in `.env.example` 