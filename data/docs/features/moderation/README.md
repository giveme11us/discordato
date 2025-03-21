# Moderation Module

## Overview
The moderation module provides comprehensive tools for server moderation, including keyword filtering, message monitoring, and automated actions.

## Features

### Keyword Filtering
- Pattern-based message filtering
- Regular expression support
- Customizable actions (delete/warn/notify)
- Channel-specific monitoring
- Notification system

### Message Monitoring
- Category-based monitoring
- Channel blacklisting
- Webhook message support
- Embed content scanning

### Automated Actions
- Message deletion
- User warnings
- Moderator notifications
- Action logging

## Configuration

### Environment Variables
```env
# Moderation Role Configuration
MOD_WHITELIST_ROLE_IDS=role_id1,role_id2

# Optional Settings
MOD_LOG_CHANNEL_ID=channel_id
MOD_NOTIFICATION_CHANNEL_ID=channel_id
```

### Module Configuration
```python
# In config/features/moderation.py
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

## Usage

### Command Reference

#### Keyword Management
```
/keyword add <pattern> [action] [notify]
/keyword remove <pattern>
/keyword list
/keyword test <message>
```

#### Filter Configuration
```
/filter enable [channel/category]
/filter disable [channel/category]
/filter settings
```

### Examples

#### Adding Spam Filter
```
/keyword add "https?://\S+" delete true
```

#### Setting Up Channel Monitoring
```
/filter enable #announcements
```

#### Testing Messages
```
/keyword test "Check out http://spam.com!"
```

## Implementation Details

### Message Processing Flow
1. Message received
2. Check channel/category
3. Extract content
4. Apply filters
5. Take action
6. Send notifications

### Filter Types

#### Text Patterns
- Simple text matching
- Case sensitivity options
- Word boundaries

#### Regular Expressions
- Complex pattern matching
- Capture groups
- Lookahead/behind

#### Special Filters
- Link detection
- Caps ratio
- Spam detection

### Action Types

#### Delete
- Remove message
- Log action
- Optional notification

#### Warn
- Keep message
- Send warning
- Log incident

#### Notify
- Keep message
- Alert moderators
- Log for review

## Best Practices

### Filter Creation
1. Start with dry run
2. Test thoroughly
3. Monitor false positives
4. Adjust as needed

### Channel Management
1. Use categories
2. Maintain blacklist
3. Set notifications
4. Review regularly

### Permission Setup
1. Define clear roles
2. Use role hierarchy
3. Set channel permissions
4. Document access

## Troubleshooting

### Common Issues

#### Filters Not Triggering
1. Check enabled status
2. Verify patterns
3. Check permissions
4. Review channels

#### Notifications Not Sending
1. Verify channel ID
2. Check permissions
3. Enable notifications
4. Test webhook

## Development

### Adding New Features
1. Update config schema
2. Implement handler
3. Add commands
4. Update docs

### Testing
1. Unit tests
2. Integration tests
3. Performance tests
4. User testing

## Security

### Considerations
- Role management
- Permission checks
- Input validation
- Action logging

### Recommendations
1. Regular audits
2. Backup configs
3. Monitor usage
4. Update regularly

## Support

### Getting Help
1. Check documentation
2. Review logs
3. Test in isolation
4. Contact support

### Reporting Issues
1. Gather info
2. Check known issues
3. Create report
4. Provide examples 