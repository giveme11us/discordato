# Configuration Guide

## Overview

This guide explains how to configure the bot's various features and modules.

## General Configuration

### Environment Variables

Basic bot configuration is done through environment variables:

```env
DISCORD_TOKEN=your_token_here
COMMAND_PREFIX=!
DEBUG=False
```

### Config Files

More detailed configuration is stored in JSON files:

```
config/
  ├── core.json
  ├── modules.json
  └── features.json
```

## Module Configuration

### Moderation

```json
{
  "mod": {
    "whitelist_roles": ["role_id1", "role_id2"],
    "log_channel": "channel_id",
    "enabled_features": ["purge", "warn"]
  }
}
```

### Link Reactions

```json
{
  "link_reactions": {
    "enabled": true,
    "reactions": ["👍", "👎"],
    "excluded_channels": []
  }
}
```

### Reaction Forwarding

```json
{
  "reaction_forward": {
    "threshold": 5,
    "target_channel": "channel_id",
    "excluded_channels": []
  }
}
```

### Pinger

```json
{
  "pinger": {
    "cooldown": 60,
    "max_keywords": 10,
    "blacklist_channels": []
  }
}
```

## Feature-Specific Settings

### RedEye

```json
{
  "redeye": {
    "monitor_delay": 30,
    "notification_channel": "channel_id",
    "roles_to_ping": ["role_id1"]
  }
}
```

## Best Practices

1. Keep sensitive data in environment variables
2. Use descriptive configuration keys
3. Document all configuration options
4. Validate configuration on startup
5. Provide sensible defaults

## Troubleshooting

Common configuration issues and solutions:

1. Missing permissions
2. Invalid channel IDs
3. Malformed JSON
4. Environment variable conflicts

## Development

When adding new features:

1. Follow existing configuration patterns
2. Add validation
3. Document all options
4. Include example configurations
5. Write configuration tests