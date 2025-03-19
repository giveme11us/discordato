# Discord Bot Command Reference

This document provides a complete reference for all commands available in the Discord bot, including slash commands and context menu commands.

## Slash Commands

### General Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/ping` | Check if the bot is responsive | `/ping` |
| `/general` | View bot status and configuration overview | `/general` |

### Moderation Module Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/keyword` | Configure keyword filtering | `/keyword [name] [categories] [channels] [alerts] [words] [delete] [severity] [rule_delete]` |
| `/reaction` | Configure reaction forward settings | `/reaction [whitelisted_category_id] [blacklisted_channel_id]` |
| `/pinger` | Configure mention notifications | `/pinger [channel] [everyone] [here] [roles]` |

### LuisaViaRoma Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/luisaviaroma_adder` | Configure LuisaViaRoma link reaction and product ID extraction | `/luisaviaroma_adder [channel_ids] [file_path]` |
| `/luisaviaroma_remover` | Remove PIDs from tracking and manage configuration | `/luisaviaroma_remover [pid] [channel_ids] [file_path]` |

### Redeye Module Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/redeye-profiles` | View profiles from the profiles.csv file | `/redeye-profiles [profile_name]` |

## Context Menu Commands

Context menu commands are special commands that appear when you right-click on users or messages in Discord.

### User Context Menu Commands

| Command | Description | Target | Action |
|---------|-------------|--------|--------|
| **Remove PID** | Remove a product ID from LuisaViaRoma tracking | User | Removes the most recent product ID posted by the selected user |

## Detailed Command Usage

### `/keyword`

Configures the keyword filtering system for monitoring and moderating content.

**Parameters:**
- `name`: Rule name (e.g., "spam-links")
- `categories`: Category IDs to monitor (comma-separated, e.g., "123456789,987654321")
- `channels`: Channel IDs to monitor (comma-separated)
- `alerts`: Channel ID to send alerts to
- `words`: Keywords or phrases to monitor (comma-separated)
- `delete`: Whether to delete matched messages (true/false)
- `severity`: Severity level (low/medium/high)
- `rule_delete`: Name of rule to delete

**Examples:**
- `/keyword name:spam-links categories:123456789 words:spam,scam,free-nitro delete:true severity:high`
- `/keyword rule_delete:spam-links`

### `/reaction`

Configures the reaction forward system that adds reactions to messages in specified categories.

**Parameters:**
- `whitelisted_category_id`: Category IDs to monitor (comma-separated)
- `blacklisted_channel_id`: Channel IDs to exclude (comma-separated)

**Examples:**
- `/reaction whitelisted_category_id:123456789,987654321`
- `/reaction blacklisted_channel_id:123456789`

### `/pinger`

Configures the mention monitoring system that tracks @everyone, @here, and role mentions.

**Parameters:**
- `channel`: Channel ID for sending notifications
- `everyone`: Whether to monitor @everyone mentions (true/false)
- `here`: Whether to monitor @here mentions (true/false)
- `roles`: Whether to monitor role mentions (true/false)

**Examples:**
- `/pinger channel:123456789 everyone:true here:true roles:true`

### `/luisaviaroma_adder`

Configures the LuisaViaRoma link detection and product ID extraction.

**Parameters:**
- `channel_ids`: Channel IDs to monitor (comma-separated)
- `file_path`: Path to the file for storing product IDs

**Examples:**
- `/luisaviaroma_adder channel_ids:123456789,987654321 file_path:/path/to/ids.txt`
- `/luisaviaroma_adder channel_ids:123456789`
- `/luisaviaroma_adder file_path:/path/to/new_ids.txt`

### `/luisaviaroma_remover`

Removes product IDs from tracking and manages LuisaViaRoma configuration.

**Parameters:**
- `pid`: Product ID to remove from tracking
- `channel_ids`: Channel IDs to monitor (comma-separated)
- `file_path`: Path to the file for storing product IDs

**Examples:**
- `/luisaviaroma_remover pid:ABC123` - Removes the specified product ID
- `/luisaviaroma_remover channel_ids:123456789,987654321 file_path:/path/to/ids.txt` - Updates configuration

### `/redeye-profiles`

View profiles from the Redeye profiles.csv file.

**Parameters:**
- `profile_name`: Optional name of a specific profile to view

**Examples:**
- `/redeye-profiles` - Lists all available profiles with basic information
- `/redeye-profiles profile_name:Test` - Shows detailed information for the "Test" profile

## Using Context Menu Commands

### Remove PID

The "Remove PID" context menu command allows you to quickly remove product IDs from tracking:

1. Right-click on a user who has posted a product ID
2. Navigate to "Apps" in the context menu
3. Select "Remove PID"
4. The bot will search the user's recent messages for a product ID
5. If found, it will remove the ID from tracking and send a confirmation

This command requires the same permissions as the `/luisaviaroma_remover` command.

## Permission Requirements

Different commands require different permission levels:

| Command | Required Permissions |
|---------|---------------------|
| `/ping` | None (anyone can use) |
| `/general` | Mod roles defined in `MOD_WHITELIST_ROLE_IDS` |
| `/keyword` | Mod roles defined in `MOD_WHITELIST_ROLE_IDS` |
| `/reaction` | Mod roles defined in `MOD_WHITELIST_ROLE_IDS` |
| `/pinger` | Mod roles defined in `MOD_WHITELIST_ROLE_IDS` |
| `/luisaviaroma_adder` | Mod roles defined in `MOD_WHITELIST_ROLE_IDS` |
| `/luisaviaroma_remover` | Mod roles defined in `MOD_WHITELIST_ROLE_IDS` |
| `/redeye-profiles` | Redeye roles defined in `REDEYE_WHITELIST_ROLE_IDS` |
| **Remove PID** (context menu) | Mod roles defined in `MOD_WHITELIST_ROLE_IDS` | 