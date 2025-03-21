# Discord Bot Features

## Overview

This Discord bot provides a range of features for server management and automation.

## Moderation Features

### Role Management
- Whitelist roles for moderation commands
- Blacklist roles from specific features
- Granular permission control

### Command Control
- Command cooldowns
- Usage limits
- Channel-specific restrictions

### Logging System
- Comprehensive action logging
- Configurable log channels
- Detailed audit trails

## Link Reaction System

### Link Detection
- Automatic link detection
- Configurable reactions
- Channel-specific settings

### Link Forwarding
- Forward links to designated channels
- Customizable forwarding rules
- Link categorization

## Mention Monitoring

### Ping Tracking
- Monitor @everyone and @here mentions
- Role mention tracking
- User mention statistics

### Notification System
- Configurable notification channels
- Role-based notifications
- Custom notification formats

## RedEye Mode

### Quiet Hours
- Configurable quiet periods
- Role-based notifications
- Time zone support

### Late Night Settings
- Custom message formatting
- Role-specific rules
- Activity monitoring

## Usage Guide

### Setting Up Moderation
```
/mod-config - Configure moderation settings
  options:
    - whitelist_roles: Add/remove roles
    - log_channel: Set log channel
    - enable: Toggle features
```

### Managing Link Reactions
```
/link-reaction-config - Configure link reactions
  options:
    - reactions: Set reaction emojis
    - channels: Set monitored channels
    - forward: Configure forwarding
```

### Configuring Mentions
```
/pinger-config - Configure mention monitoring
  options:
    - notification_channel: Set channel
    - monitor_roles: Toggle role monitoring
    - monitor_everyone: Toggle @everyone tracking
```

### RedEye Settings
```
/redeye-config - Configure quiet hours
  options:
    - quiet_start: Set start time
    - quiet_end: Set end time
    - roles: Set affected roles
```

## Best Practices

1. Start with Basic Setup
   - Configure essential features
   - Test in limited channels
   - Gradually expand usage

2. Role Management
   - Use clear role hierarchy
   - Document role permissions
   - Regular permission audits

3. Channel Organization
   - Group similar channels
   - Use clear naming
   - Set appropriate permissions

4. Monitoring
   - Regular log reviews
   - Track feature usage
   - Adjust settings as needed

## Troubleshooting

### Common Issues

1. Command Access
   - Check role permissions
   - Verify channel settings
   - Review command cooldowns

2. Notifications
   - Check channel permissions
   - Verify role settings
   - Test notification flow

3. Feature Settings
   - Review configuration
   - Check enabled status
   - Verify channel setup

## Support

Need help? Contact us:
1. Check documentation
2. Join support server
3. Open GitHub issue
4. Contact moderators
