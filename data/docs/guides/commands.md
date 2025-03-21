# Command Guide

## Overview

This guide covers all available commands in the Discord bot.

## General Commands

### Help
```
/help - Display help information
  options:
    - command: Get help for specific command
    - category: List commands in category
```

### Info
```
/info - Show bot information
  options:
    - version: Show version info
    - uptime: Show uptime stats
```

## Moderation Commands

### Configuration
```
/mod-config - Configure moderation settings
  options:
    - whitelist_roles: Add/remove roles
    - log_channel: Set log channel
    - enable: Toggle features
```

### Actions
```
/mod mute <user> [duration] - Temporarily mute user
/mod kick <user> [reason] - Kick user from server
/mod ban <user> [reason] - Ban user from server
/mod clear <amount> - Clear messages
```

## Link Reaction Commands

### Configuration
```
/link-reaction-config - Configure link reactions
  options:
    - reactions: Set reaction emojis
    - channels: Set monitored channels
    - forward: Configure forwarding
```

### Management
```
/link-reaction list - List active reactions
/link-reaction add <emoji> - Add reaction
/link-reaction remove <emoji> - Remove reaction
```

## Mention Monitor Commands

### Configuration
```
/pinger-config - Configure mention monitoring
  options:
    - notification_channel: Set channel
    - monitor_roles: Toggle role monitoring
    - monitor_everyone: Toggle @everyone tracking
```

### Statistics
```
/pinger stats - View mention statistics
/pinger clear - Clear statistics
```

## RedEye Commands

### Configuration
```
/redeye-config - Configure quiet hours
  options:
    - quiet_start: Set start time
    - quiet_end: Set end time
    - roles: Set affected roles
```

### Management
```
/redeye status - Check current status
/redeye toggle - Toggle quiet mode
```

## Command Usage

### Permissions
- Commands require appropriate permissions
- Some commands restricted to specific roles
- Check role requirements before use

### Rate Limits
- Commands have cooldown periods
- Respect usage limits
- Avoid command spam

### Examples

#### Setting Up Moderation
```
/mod-config whitelist_roles @Moderator @Admin
/mod-config log_channel #mod-logs
```

#### Managing Link Reactions
```
/link-reaction-config reactions 👍 👎
/link-reaction-config channels #links
```

#### Configuring Mentions
```
/pinger-config notification_channel #notifications
/pinger-config monitor_roles true
```

## Best Practices

1. Command Usage
   - Use appropriate channels
   - Check command syntax
   - Review command output

2. Configuration
   - Start with basic settings
   - Test in limited scope
   - Adjust as needed

3. Permissions
   - Set up role hierarchy
   - Review access regularly
   - Document changes

## Troubleshooting

### Common Issues

1. Command Not Working
   - Check permissions
   - Verify syntax
   - Review error message

2. Configuration Problems
   - Check current settings
   - Verify channel IDs
   - Test in safe channel

3. Permission Errors
   - Check role hierarchy
   - Verify bot permissions
   - Review channel settings

## Support

Need help with commands?
1. Use `/help` command
2. Check documentation
3. Join support server
4. Contact moderators 