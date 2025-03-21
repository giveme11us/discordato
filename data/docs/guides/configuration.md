# Configuration Guide

## Overview
This guide explains how to configure all aspects of the Discord bot, from basic setup to advanced feature configuration.

## Configuration Files

### Environment Variables (`.env`)
Primary configuration file for sensitive and instance-specific settings.

```env
# Required Bot Settings
DISCORD_TOKEN=your_bot_token
GUILD_IDS=server_id1,server_id2

# Permission Settings
MOD_WHITELIST_ROLE_IDS=role_id1,role_id2
REDEYE_WHITELIST_ROLE_IDS=role_id3,role_id4

# Feature Settings
EMBED_COLOR=57fa1
EMBED_FOOTER_TEXT=Your Bot Name
EMBED_FOOTER_ICON_URL=https://your-icon-url.com/icon.png

# Logging Settings
LOG_LEVEL=INFO
LOG_FILE=bot.log

# Optional Settings
COMMAND_PREFIX=!
DEBUG_MODE=False
```

### Feature Configuration Files

#### Moderation (`config/features/moderation.py`)
```python
FILTER_DEFAULT_CONFIG = {
    "ENABLED": False,
    "DRY_RUN": True,
    "CATEGORY_IDS": [],
    "MONITOR_CHANNEL_IDS": [],
    "BLACKLIST_CHANNEL_IDS": [],
    "NOTIFICATION_CHANNEL_ID": None,
    "FILTERS": {
        "spam": {
            "enabled": True,
            "patterns": [],
            "action": "delete",
            "notify": True
        }
    }
}
```

#### Reactions (`config/features/reactions.py`)
```python
FORWARD_DEFAULT_CONFIG = {
    "ENABLED": False,
    "CATEGORY_IDS": [],
    "BLACKLIST_CHANNEL_IDS": [],
    "DESTINATION_CHANNEL_ID": None,
    "FORWARD_EMOJI": "➡️"
}
```

## Configuration Categories

### 1. Bot Core Settings

#### Discord Integration
- `DISCORD_TOKEN`: Your bot's token
- `GUILD_IDS`: Comma-separated list of server IDs
- `COMMAND_PREFIX`: Command prefix for legacy commands

#### Permission System
- `MOD_WHITELIST_ROLE_IDS`: Roles that can use moderation commands
- `REDEYE_WHITELIST_ROLE_IDS`: Roles that can use Redeye features
- `ONLINE_WHITELIST_ROLE_IDS`: Roles for online features

### 2. Feature Configuration

#### Moderation Module
```python
# In config/features/moderation.py
filter_config.ENABLED = True
filter_config.NOTIFICATION_CHANNEL_ID = channel_id
filter_config.add_filter("spam", {
    "patterns": ["https?://\\S+"],
    "action": "delete",
    "notify": True
})
```

#### Reaction System
```python
# In config/features/reactions.py
forward_config.ENABLED = True
forward_config.CATEGORY_IDS = [category_id1, category_id2]
forward_config.DESTINATION_CHANNEL_ID = channel_id
```

#### Pinger Module
```python
# In config/features/pinger_config.py
pinger_config.ENABLED = True
pinger_config.MONITOR_EVERYONE = True
pinger_config.NOTIFICATION_CHANNEL_ID = channel_id
```

### 3. Visual Configuration

#### Embed Settings
```python
# In config/features/embed_config.py
embed_config.EMBED_COLOR = 0x57fa1
embed_config.FOOTER_TEXT = "Your Bot Name"
embed_config.THUMBNAIL_URL = "https://your-icon-url.com/icon.png"
```

## Advanced Configuration

### Custom Validation Rules
```python
def validate_config(self) -> bool:
    if not super().validate_config():
        return False
        
    # Custom validation logic
    if self.NOTIFICATION_CHANNEL_ID is not None:
        if not isinstance(self.NOTIFICATION_CHANNEL_ID, int):
            logger.warning("NOTIFICATION_CHANNEL_ID must be an integer")
            return False
            
    return True
```

### Configuration Migration
```python
def migrate_config(self, old_version: str) -> bool:
    if old_version == "1.0.0":
        # Migration logic
        self._config["NEW_FIELD"] = self._config.get("OLD_FIELD", default_value)
        self._version = "1.1.0"
        return True
    return False
```

## Best Practices

### 1. Security
- Never commit `.env` file
- Use environment variables for sensitive data
- Regularly rotate tokens and credentials
- Implement proper permission checks

### 2. Performance
- Cache frequently accessed values
- Use appropriate data structures
- Implement rate limiting
- Monitor resource usage

### 3. Maintenance
- Keep configurations versioned
- Document all changes
- Implement backup systems
- Regular validation checks

## Configuration Examples

### Basic Setup
```env
DISCORD_TOKEN=your_token_here
GUILD_IDS=123456789,987654321
MOD_WHITELIST_ROLE_IDS=111222333,444555666
LOG_LEVEL=INFO
```

### Advanced Setup
```env
# Bot Settings
DISCORD_TOKEN=your_token_here
GUILD_IDS=123456789,987654321

# Role Configuration
MOD_WHITELIST_ROLE_IDS=111222333,444555666
REDEYE_WHITELIST_ROLE_IDS=777888999
ONLINE_WHITELIST_ROLE_IDS=123456789

# Visual Settings
EMBED_COLOR=57fa1
EMBED_FOOTER_TEXT=Your Amazing Bot
EMBED_FOOTER_ICON_URL=https://your-cdn.com/icon.png

# Logging Configuration
LOG_LEVEL=DEBUG
LOG_FILE=logs/bot.log
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Feature Toggles
ENABLE_REDEYE=True
ENABLE_LUISAVIAROMA=True
ENABLE_MODERATION=True

# Advanced Settings
DEBUG_MODE=False
COMMAND_SYNC_INTERVAL=60
MAX_CACHE_SIZE=1000
```

## Troubleshooting

### Common Issues

1. **Configuration Not Loading**
   ```
   Solution: Check file permissions and paths
   ```

2. **Invalid Values**
   ```
   Solution: Verify data types and formats
   ```

3. **Permission Errors**
   ```
   Solution: Check role ID configuration
   ```

### Validation

Always validate your configuration:
```python
if not config.validate_config():
    logger.error("Invalid configuration")
    sys.exit(1)
```

## Support

For configuration issues:
1. Check this guide
2. Verify your settings
3. Check the logs
4. Contact support with:
   - Configuration files
   - Error messages
   - Environment details 