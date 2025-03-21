# Moderation Features

The moderation module provides essential tools for server management and moderation.

## Features

### Role-Based Access Control
- Whitelist roles for moderation commands
- Blacklist roles from specific features
- Granular permission management

### Command Restrictions
- Command cooldowns
- Usage limits
- Channel-specific restrictions

### Logging
- Comprehensive moderation action logging
- Configurable log channels
- Detailed audit trail

### Auto-Moderation
- Message content monitoring
- Spam detection
- Automated actions based on rules

## Configuration

### Environment Variables
```env
# Moderation Settings
MOD_WHITELIST_ROLE_IDS=role_id1,role_id2
MOD_LOG_CHANNEL_ID=channel_id
```

### Commands

#### Moderation Configuration
```
/mod-config - Configure moderation settings
  options:
    - whitelist_roles: Add/remove roles from whitelist
    - log_channel: Set logging channel
    - enable: Enable/disable moderation features
```

## Development

### Adding New Features

1. Create feature module in `modules/mod/`
2. Implement required interfaces
3. Add configuration options
4. Update documentation

### Testing

Run tests with:
```bash
python -m pytest tests/mod/
```

## Best Practices

1. Always log moderation actions
2. Use role-based permissions
3. Implement proper error handling
4. Keep configuration flexible
5. Document changes thoroughly 