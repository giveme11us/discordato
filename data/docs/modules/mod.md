# Mod Module Documentation

## Overview

The Mod module provides moderation and server management functionality for Discord servers.

## Features

### User Management
- Temporary mute
- Kick users
- Ban users
- Warning system

### Message Moderation
- Message deletion
- Bulk message clearing
- Content filtering
- Mention monitoring

### Server Management
- Role management
- Channel configuration
- Permission updates
- Server settings

## Commands

### Moderation Commands

```
/mod mute <user> [duration] [reason]
Description: Temporarily mute a user
Options:
- user: User to mute
- duration: Mute duration (e.g., 1h, 30m)
- reason: Reason for mute
Permissions: MODERATE_MEMBERS
```

```
/mod kick <user> [reason]
Description: Kick a user from the server
Options:
- user: User to kick
- reason: Reason for kick
Permissions: KICK_MEMBERS
```

```
/mod ban <user> [reason] [delete_days]
Description: Ban a user from the server
Options:
- user: User to ban
- reason: Reason for ban
- delete_days: Days of messages to delete
Permissions: BAN_MEMBERS
```

### Message Management

```
/mod clear <amount> [user]
Description: Clear messages in a channel
Options:
- amount: Number of messages to clear
- user: Only clear messages from this user
Permissions: MANAGE_MESSAGES
```

```
/mod slowmode <duration>
Description: Set channel slowmode
Options:
- duration: Slowmode duration
Permissions: MANAGE_CHANNELS
```

### Warning System

```
/mod warn <user> <reason>
Description: Warn a user
Options:
- user: User to warn
- reason: Reason for warning
Permissions: MODERATE_MEMBERS
```

```
/mod warnings <user>
Description: View user warnings
Options:
- user: User to check
Permissions: MODERATE_MEMBERS
```

## Configuration

### Environment Variables

```env
# Mod Module Settings
MOD_ENABLED=True
MOD_LOG_CHANNEL=channel_id
MOD_MUTE_ROLE=role_id
MOD_ADMIN_ROLES=role1,role2
MOD_MOD_ROLES=role3,role4
MOD_WARN_THRESHOLD=3
MOD_WARN_ACTION=mute
MOD_WARN_DURATION=1h
```

### Module Settings

```python
MOD_SETTINGS = {
    'mute_duration': 300,  # Default mute duration
    'warn_threshold': 3,   # Warnings before action
    'warn_action': 'mute', # Action on threshold
    'warn_duration': '1h', # Duration for auto-actions
    'log_enabled': True,   # Enable action logging
    'dm_notifications': True, # Send DM notifications
}
```

## Events

### Monitored Events
- `on_message`: Content monitoring
- `on_message_edit`: Edit tracking
- `on_message_delete`: Deletion logging
- `on_member_join`: Join monitoring
- `on_member_remove`: Leave tracking
- `on_member_update`: Member updates
- `on_guild_update`: Server changes

### Event Handlers

```python
async def on_message(message):
    """Monitor message content."""
    if should_moderate(message):
        await handle_moderation(message)

async def on_member_join(member):
    """Monitor new members."""
    await check_member(member)
```

## Utilities

### Permission Checking

```python
def check_permissions(member, action):
    """Check if member can perform action."""
    return has_required_roles(member, action)

def is_moderator(member):
    """Check if member is a moderator."""
    return has_mod_roles(member)
```

### Action Logging

```python
async def log_action(action, user, mod, reason):
    """Log moderation action."""
    await log_channel.send(
        f"**{action}** | User: {user}\n"
        f"Moderator: {mod}\n"
        f"Reason: {reason}"
    )
```

## Database Schema

### Warnings Table
```sql
CREATE TABLE warnings (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    mod_id TEXT NOT NULL,
    reason TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Mutes Table
```sql
CREATE TABLE mutes (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    mod_id TEXT NOT NULL,
    reason TEXT,
    end_time DATETIME NOT NULL,
    active BOOLEAN DEFAULT TRUE
);
```

## API Reference

### ModModule Class

```python
class ModModule:
    """Main mod module class."""
    
    def __init__(self, bot):
        self.bot = bot
        self.settings = ModSettings()
        self.db = ModDatabase()
    
    async def mute_user(self, user, duration, reason):
        """Mute a user."""
        pass
    
    async def warn_user(self, user, reason):
        """Warn a user."""
        pass
    
    async def check_warnings(self, user):
        """Get user warnings."""
        pass
```

### ModSettings Class

```python
class ModSettings:
    """Mod module settings."""
    
    def __init__(self):
        self.load_settings()
    
    def get_mute_role(self):
        """Get mute role ID."""
        pass
    
    def get_mod_roles(self):
        """Get moderator role IDs."""
        pass
```

## Error Handling

### Custom Exceptions

```python
class ModError(Exception):
    """Base mod module error."""
    pass

class PermissionError(ModError):
    """Permission-related errors."""
    pass

class ConfigError(ModError):
    """Configuration errors."""
    pass
```

### Error Processing

```python
try:
    await mod.mute_user(user, duration)
except PermissionError:
    await handle_permission_error()
except ModError as e:
    await handle_mod_error(e)
```

## Best Practices

1. **Permission Management**
   - Always check permissions
   - Use role hierarchy
   - Log permission errors
   - Maintain audit trail

2. **Action Processing**
   - Validate inputs
   - Check user status
   - Handle edge cases
   - Provide feedback

3. **Data Management**
   - Regular cleanup
   - Data validation
   - Backup warnings
   - Monitor storage

4. **Error Handling**
   - Graceful failures
   - User feedback
   - Error logging
   - Recovery procedures

## Notes

- Keep audit logs
- Regular maintenance
- Monitor performance
- Update documentation
- Test thoroughly
- Handle appeals process 