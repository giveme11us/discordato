# Discord Bot Commands Guide

## General Commands

### Basic Commands

#### `/ping`
- **Description**: Check if the bot is responsive and view latency
- **Usage**: `/ping`
- **Response**: Shows the bot's current response time in milliseconds
- **Permissions**: Everyone

#### `/hi`
- **Description**: Get a friendly greeting from the bot
- **Usage**: `/hi`
- **Response**: Random friendly greeting message
- **Permissions**: Everyone

#### `/help [command]`
- **Description**: Display help information about commands
- **Usage**: 
  - `/help` - Show all available commands
  - `/help command` - Show help for a specific command
- **Parameters**:
  - `command` (optional): The command to get help for
- **Permissions**: Everyone

#### `/number [min_value] [max_value]`
- **Description**: Generate a random number within a specified range
- **Usage**: `/number min_value max_value`
- **Parameters**:
  - `min_value` (optional): The minimum value (default: 1)
  - `max_value` (optional): The maximum value (default: 100)
- **Permissions**: Everyone

### Status Commands

#### `/general`
- **Description**: View bot status and configuration overview
- **Usage**: `/general`
- **Response**: Shows current status of all enabled modules and configurations
- **Permissions**: Moderator

## Moderation Commands

### Message Management

#### `/purge [count]`
- **Description**: Delete a specified number of messages in the current channel
- **Usage**: `/purge count`
- **Parameters**:
  - `count` (optional): Number of messages to delete (default: 10, max: 100)
- **Permissions**: Manage Messages or Administrator

### Keyword Filter

#### `/keyword-filter-config`
- **Description**: Configure the keyword filter feature
- **Usage**: `/keyword-filter-config action [filter_id] [setting] [value]`
- **Parameters**:
  - `action`: Choose from:
    - `view` - View current configuration
    - `enable` - Enable the feature
    - `disable` - Disable the feature
    - `categories` - Manage monitored categories
    - `blacklist` - Manage blacklisted channels
    - `notification` - Configure notifications
    - `dry_run` - Toggle dry run mode
    - `filters` - Manage filters
  - `filter_id` (optional): The filter ID when configuring specific filters
  - `setting` (optional): The setting to modify
  - `value` (optional): The new value
- **Permissions**: Administrator

#### `/keyword-filter-quicksetup`
- **Description**: Quick setup for keyword filter with a single command
- **Usage**: `/keyword-filter-quicksetup source_channel notification_channel keywords`
- **Parameters**:
  - `source_channel`: Channel or category ID to monitor
  - `notification_channel`: Channel ID for notifications
  - `keywords`: Comma-separated list of keywords (e.g., 'test,hello,example')
- **Permissions**: Administrator

### Reaction System

#### `/reaction-forward-config`
- **Description**: Configure the reaction forward feature
- **Usage**: `/reaction-forward-config setting [value]`
- **Parameters**:
  - `setting`: Choose from:
    - `view` - View current configuration
    - `enable` - Enable the feature
    - `disable` - Disable the feature
    - `forwarding` - Toggle forwarding
    - `categories` - Manage categories
    - `blacklist` - Manage blacklist
  - `value` (optional): New value for the setting
- **Permissions**: Administrator

#### `/link-reaction-config`
- **Description**: Configure the link reaction feature and manage store settings
- **Usage**: `/link-reaction-config action [store_id] [setting] [value]`
- **Parameters**:
  - `action`: Choose from:
    - `view` - View configuration
    - `enable` - Enable feature
    - `disable` - Disable feature
    - `categories` - Manage categories
    - `blacklist` - Manage blacklist
    - `stores` - Manage stores
  - `store_id` (optional): Store ID for store-specific settings
  - `setting` (optional): Setting to modify
  - `value` (optional): New value
- **Permissions**: Administrator

### Ping Monitoring

#### `/pinger-config`
- **Description**: Configure the pinger feature
- **Usage**: `/pinger-config setting [value]`
- **Parameters**:
  - `setting`: Choose from:
    - `view` - View current configuration
    - `channel` - Set notification channel
    - `whitelist` - Manage whitelist roles
    - `everyone` - Configure @everyone mentions
    - `here` - Configure @here mentions
  - `value` (optional): New value for the setting
- **Permissions**: Administrator

### Module Configuration

#### `/mod-config`
- **Description**: Configure module-wide settings
- **Usage**: `/mod-config setting action [value]`
- **Parameters**:
  - `setting`: Currently supports:
    - `whitelist` - Manage whitelist roles
  - `action`: Choose from:
    - `view` - View current settings
    - `add` - Add role
    - `remove` - Remove role
    - `clear` - Clear all roles
  - `value` (optional): Role ID or mention
- **Permissions**: Administrator

## Notes

1. **Permission Levels**:
   - Everyone: All users can use these commands
   - Moderator: Users with whitelisted roles
   - Administrator: Server administrators only
   - Manage Messages: Users with message management permissions

2. **Command Usage Tips**:
   - Parameters in `[]` are optional
   - Use `/help command` to get detailed help for any command
   - Most configuration commands support a `view` action to check current settings

3. **Configuration Best Practices**:
   - Always verify changes after configuration
   - Use `view` action before making changes
   - Keep track of configured channels and roles
   - Test configurations in a private channel first

4. **Error Handling**:
   - Commands will provide feedback if something goes wrong
   - Check permissions if a command doesn't work
   - Use the help command if unsure about usage
   - Contact administrators for persistent issues 