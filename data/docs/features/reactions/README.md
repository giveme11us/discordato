# Reactions Module

## Overview
The reactions module provides advanced message forwarding and linking functionality through Discord reactions. It enables efficient message sharing and cross-channel communication.

## Features

### Forward Reactions
- Message forwarding to designated channels
- Category-based monitoring
- Role-based permissions
- Customizable forward emoji
- Attachment handling

### Link Reactions
- Cross-channel message linking
- Customizable link emoji
- Role-based access control
- Blacklist support
- Embed formatting

## Configuration

### Environment Variables
```env
# Role Configuration
MOD_WHITELIST_ROLE_IDS=role_id1,role_id2

# Optional Settings
FORWARD_NOTIFICATION_CHANNEL_ID=channel_id
LINK_NOTIFICATION_CHANNEL_ID=channel_id
```

### Forward Configuration
```python
# In config/features/reactions.py
FORWARD_DEFAULT_CONFIG = {
    "ENABLED": False,
    "CATEGORY_IDS": [],
    "BLACKLIST_CHANNEL_IDS": [],
    "DESTINATION_CHANNEL_ID": None,
    "FORWARD_EMOJI": "➡️",
    "FORWARD_ATTACHMENTS": True,
    "FORWARD_EMBEDS": True,
    "WHITELIST_ROLE_IDS": []
}
```

### Link Configuration
```python
# In config/features/reactions.py
LINK_DEFAULT_CONFIG = {
    "ENABLED": False,
    "CATEGORY_IDS": [],
    "BLACKLIST_CHANNEL_IDS": [],
    "LINK_EMOJI": "🔗",
    "WHITELIST_ROLE_IDS": []
}
```

## Usage

### Command Reference

#### Forward Configuration
```
/reaction forward enable [channel/category]
/reaction forward disable [channel/category]
/reaction forward settings
```

#### Link Configuration
```
/reaction link enable [channel/category]
/reaction link disable [channel/category]
/reaction link settings
```

### Examples

#### Setting Up Forward Reactions
```
# Enable forwarding in announcements
/reaction forward enable #announcements

# Configure forward settings
/reaction forward settings
  Category: #general
  Forward Emoji: ➡️
  Destination: #notifications
```

#### Setting Up Link Reactions
```
# Enable linking in support
/reaction link enable #support

# Configure link settings
/reaction link settings
  Category: #help
  Link Emoji: 🔗
```

## Implementation Details

### Message Flow

#### Forward Process
1. Reaction added
2. Check permissions
3. Verify channel
4. Process message
5. Create forward
6. Send notification

#### Link Process
1. Reaction added
2. Check permissions
3. Verify channels
4. Create link
5. Send notifications

### Message Handling

#### Content Types
- Text messages
- Embeds
- Attachments
- Webhooks
- System messages

#### Forward Options
- Keep attachments
- Preserve embeds
- Add attribution
- Include context

#### Link Options
- Create reference
- Add jump links
- Preserve context
- Track origin

## Best Practices

### Channel Setup
1. Use categories
2. Set permissions
3. Configure blacklists
4. Test thoroughly

### Permission Management
1. Define roles
2. Set hierarchies
3. Review access
4. Monitor usage

### Message Handling
1. Verify content
2. Check attachments
3. Validate embeds
4. Monitor size

## Troubleshooting

### Common Issues

#### Reactions Not Working
1. Check permissions
2. Verify emoji
3. Check channels
4. Review roles

#### Messages Not Forwarding
1. Check destination
2. Verify permissions
3. Check attachments
4. Review settings

## Development

### Adding Features
1. Update config
2. Add handlers
3. Implement commands
4. Update docs

### Testing
1. Unit tests
2. Integration tests
3. User testing
4. Load testing

## Security

### Considerations
- Role permissions
- Channel access
- Content validation
- Rate limiting

### Recommendations
1. Regular audits
2. Monitor usage
3. Review permissions
4. Update regularly

## Support

### Getting Help
1. Check docs
2. Review logs
3. Test isolated
4. Contact support

### Reporting Issues
1. Gather details
2. Check known issues
3. Create report
4. Provide examples

## Advanced Usage

### Custom Emojis
```python
# Configure custom emojis
forward_config.FORWARD_EMOJI = "<:custom_forward:123456789>"
link_config.LINK_EMOJI = "<:custom_link:987654321>"
```

### Channel Rules
```python
# Configure specific channel rules
forward_config.add_channel_rule({
    "channel_id": 123456789,
    "forward_to": 987654321,
    "require_roles": [111222333]
})
```

### Message Formatting
```python
# Configure message templates
forward_config.FORWARD_TEMPLATE = "Forwarded from {channel}\n{content}"
link_config.LINK_TEMPLATE = "Linked message: {url}"
```

## Integration

### With Other Modules
- Moderation module
- Logging system
- Permission system
- Command system

### External Services
- Webhooks
- APIs
- Databases
- Monitoring 