# Configuration Guide

This guide explains how to configure the Discord bot framework for different operational scenarios and customize its behavior.

## Configuration Overview

The bot framework uses a layered configuration approach:
1. Environment variables (`.env` file)
2. Module-specific settings
3. Runtime configuration
4. Command-based configuration

## Environment Configuration

### Basic Settings

The `.env` file contains core configuration:

```env
# Bot Identity
DISCORD_BOT_TOKEN=your_main_token
BOT_NAME="Your Bot Name"
BOT_DESCRIPTION="A powerful Discord bot"

# Operational Mode
DEVELOPMENT_MODE=True
DEBUG_LOGGING=True

# Command Configuration
COMMAND_PREFIX=!
ENABLE_SLASH_COMMANDS=True
```

### Module Management

Configure which modules are active:

```env
# Enable specific modules
ENABLED_MODULES=mod,online,instore,redeye

# Module-specific tokens (for multi-bot mode)
MOD_TOKEN=token_for_mod_module
ONLINE_TOKEN=token_for_online_module
INSTORE_TOKEN=token_for_instore_module
```

### Logging Configuration

Control logging behavior:

```env
# Logging Settings
LOG_LEVEL=INFO
LOG_FILE=discord_bot.log
ENABLE_DEBUG_LOGGING=False
ENABLE_FILE_LOGGING=True
```

## Module Configuration

### Mod Module

```env
# Mod Module Settings
MOD_NOTIFICATION_CHANNEL=969208183799296030
MOD_WHITELIST_ROLES=811975979492704337,811975812596498482
MOD_MONITOR_EVERYONE=True
MOD_MONITOR_HERE=True
```

### Online Module

```env
# Online Module Settings
ONLINE_CHECK_INTERVAL=300
ONLINE_STATUS_CHANNEL=969208183799296030
ONLINE_ALERT_ROLES=811975979492704337
```

### Instore Module

```env
# Instore Module Settings
INSTORE_REACTION_EMOJI=✅
INSTORE_FORWARD_CHANNEL=969208183799296030
INSTORE_LINK_PATTERN=https?://[^\s<>"]+?/[^\s<>"]+
```

## Operational Scenarios

### Single Bot Mode

For running one bot with all modules:

```env
# Single Bot Configuration
DISCORD_BOT_TOKEN=your_main_token
ENABLED_MODULES=mod,online,instore
OPERATIONAL_MODE=single
```

### Multi-Bot Mode

For running separate bots for different modules:

```env
# Multi-Bot Configuration
OPERATIONAL_MODE=multi
ENABLED_MODULES=mod,online,instore

# Module Tokens
MOD_TOKEN=token_for_mod
ONLINE_TOKEN=token_for_online
INSTORE_TOKEN=token_for_instore
```

### Partial Mode

For running only specific modules:

```env
# Partial Mode Configuration
OPERATIONAL_MODE=partial
ENABLED_MODULES=mod,online
MOD_TOKEN=token_for_mod
ONLINE_TOKEN=token_for_online
```

## Command-Based Configuration

Many settings can be changed via Discord commands:

```
/config view - View current configuration
/config set <module> <setting> <value> - Update a setting
/config reset <module> - Reset module settings
```

### Permission Requirements

Configure command access:

```env
# Permission Configuration
ADMIN_ROLES=811975979492704337
MOD_ROLES=811975812596498482
CONFIG_ROLES=811975979492704337,811975812596498482
```

## Development Configuration

Additional settings for development:

```env
# Development Settings
DEVELOPMENT_MODE=True
DEBUG_LOGGING=True
TEST_GUILD_ID=your_test_server_id
ENABLE_HOT_RELOAD=True
```

## Security Considerations

1. **Token Security**
   - Store tokens securely
   - Use environment variables
   - Never commit tokens

2. **Permission Management**
   - Limit admin access
   - Use role-based permissions
   - Regularly audit access

3. **Logging Security**
   - Avoid logging sensitive data
   - Rotate log files
   - Monitor log access

## Best Practices

1. **Configuration Management**
   - Keep `.env.example` updated
   - Document all settings
   - Use version control

2. **Module Settings**
   - Group related settings
   - Use descriptive names
   - Provide defaults

3. **Operational Security**
   - Regular token rotation
   - Audit trail for changes
   - Backup configuration

## Troubleshooting

### Common Configuration Issues

1. **Invalid Token**
   - Check token format
   - Verify bot permissions
   - Ensure token is active

2. **Module Loading Fails**
   - Check ENABLED_MODULES
   - Verify module tokens
   - Check dependencies

3. **Permission Errors**
   - Verify role IDs
   - Check bot permissions
   - Review access levels

## Configuration Updates

When updating configuration:
1. Stop the bot
2. Make changes
3. Verify settings
4. Restart the bot

## Next Steps

1. Review [Features Guide](features.md)
2. Set up monitoring
3. Configure backups
4. Test configuration
