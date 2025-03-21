# Command Reference Guide

## Overview
This guide details all available bot commands, their usage, and required permissions.

## Command Categories

### General Commands
| Command | Description | Usage | Permissions |
|---------|-------------|-------|-------------|
| `/general` | View bot status and configuration | `/general` | Moderator |
| `/help` | Display help information | `/help [command]` | Everyone |
| `/ping` | Check bot latency | `/ping` | Everyone |

### Moderation Commands
| Command | Description | Usage | Permissions |
|---------|-------------|-------|-------------|
| `/keyword` | Manage keyword filters | `/keyword [add/remove/list]` | Moderator |
| `/reaction` | Manage reaction settings | `/reaction [enable/disable]` | Moderator |
| `/pinger` | Configure ping monitoring | `/pinger [settings]` | Moderator |

### E-commerce Commands
| Command | Description | Usage | Permissions |
|---------|-------------|-------|-------------|
| `/redeye` | Manage Redeye features | `/redeye [subcommand]` | Redeye Role |
| `/luisaviaroma` | Manage LuisaViaRoma features | `/luisaviaroma [subcommand]` | Moderator |

## Detailed Command Usage

### Keyword Filter Commands
```
/keyword add <pattern> [action] [notify]
/keyword remove <pattern>
/keyword list
/keyword test <message>
```

Options:
- `pattern`: Text or regex pattern to match
- `action`: delete/warn/notify (default: notify)
- `notify`: true/false - send notifications (default: true)

Example:
```
/keyword add "spam message" delete true
```

### Reaction Commands
```
/reaction enable [channel] [category]
/reaction disable [channel] [category]
/reaction settings
```

Options:
- `channel`: Specific channel to configure
- `category`: Category to configure

Example:
```
/reaction enable #announcements
```

### Pinger Commands
```
/pinger monitor [everyone/here/roles] [enable/disable]
/pinger channel <set/remove> <channel>
/pinger whitelist <add/remove> <role>
```

Example:
```
/pinger monitor everyone enable
/pinger channel set #notifications
```

### Redeye Commands
```
/redeye profile <create/edit/delete>
/redeye monitor <add/remove> <url>
/redeye settings
```

Example:
```
/redeye profile create
/redeye monitor add https://www.redeye.co.uk/product/123
```

### LuisaViaRoma Commands
```
/luisaviaroma adder <url>
/luisaviaroma remover <url>
/luisaviaroma list
```

Example:
```
/luisaviaroma adder https://www.luisaviaroma.com/item/123
```

## Permission Levels

### Role-Based Permissions
- **Everyone**: Basic commands
- **Moderator**: All moderation commands
- **Redeye Role**: Redeye-specific commands
- **Admin**: All commands

### Environment Variables
Configure role IDs in `.env`:
```env
MOD_WHITELIST_ROLE_IDS=role_id1,role_id2
REDEYE_WHITELIST_ROLE_IDS=role_id3,role_id4
```

## Command Cooldowns
Some commands have cooldowns to prevent abuse:
- `/ping`: 5 seconds
- `/keyword test`: 10 seconds
- Monitoring commands: 30 seconds

## Error Handling
Commands will return clear error messages for:
- Missing permissions
- Invalid input
- Rate limiting
- API errors

## Examples

### Setting Up Keyword Filtering
```
# Add a filter for spam links
/keyword add "https?://\S+" delete true

# List all active filters
/keyword list

# Test a message against filters
/keyword test "check out http://spam.com"
```

### Configuring Reaction Forwarding
```
# Enable in a channel
/reaction enable #announcements

# Configure settings
/reaction settings
  Category: #general
  Forward Emoji: ➡️
  Notification Channel: #notifications
```

### Setting Up Pinger
```
# Configure notification channel
/pinger channel set #mod-notifications

# Enable monitoring
/pinger monitor everyone enable
/pinger monitor here enable

# Add whitelisted role
/pinger whitelist add @Moderator
```

## Best Practices

1. **Permission Management**
   - Regularly review role permissions
   - Use specific roles for specific features
   - Don't give unnecessary permissions

2. **Command Usage**
   - Test commands in a private channel first
   - Use help command for guidance
   - Check command feedback

3. **Monitoring**
   - Keep track of enabled features
   - Review notification settings
   - Monitor command usage

## Troubleshooting

If a command fails:
1. Check your permissions
2. Verify bot permissions
3. Check command syntax
4. Look for error messages
5. Check the logs

## Support

For command-related issues:
1. Use `/help [command]`
2. Check this documentation
3. Contact server administrators
4. Report bugs through proper channels 