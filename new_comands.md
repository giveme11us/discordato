# Discord Bot Commands & Features

## Module Overview

| Module | Feature | Description | Commands |
|--------|---------|-------------|----------|
| **mod** | Keyword Filter | Automatically detects keywords in messages and forwards them to a notification channel | `/keyword-filter-setup` |
| **mod** | Reaction Forward | Forwards messages to a destination channel when a specific reaction is added | `/reaction-forward-setup` |
| **mod** | Link Reaction | Automatically adds reactions to messages containing links | `/link-reaction` |
| **mod** | Pinger | Monitors for @ mentions and sends notifications | *No slash commands, automatic* |
| **instore** | In-store Monitoring | Features related to in-store product monitoring | *Commands not visible in provided code* |
| **online** | Online Monitoring | Features related to online product monitoring | *Commands not visible in provided code* |

## Detailed Command Reference

### Keyword Filter Module

#### `/keyword-filter-setup`

Command to set up keyword filtering with a single command. When used without parameters, it displays the current rules.

| Parameter | Description | Required |
|-----------|-------------|----------|
| `original_channel_id` | Channel ID to monitor | Yes |
| `forward_channel_id` | Channel ID where alerts should be sent | Yes |
| `keywords` | Comma-separated list of keywords to detect | Yes |

**Usage Examples:**
- `/keyword-filter-setup` - Displays current rules
- `/keyword-filter-setup original_channel_id:123456789 forward_channel_id:987654321 keywords:restock,drop,available`

### Reaction Forward Module

#### `/reaction-forward-setup`

Configure the reaction forward feature settings. When used without parameters, it displays the current setup.

| Parameter | Description | Required |
|-----------|-------------|----------|
| `whitelisted_category_id` | Comma-separated list of category IDs to monitor for reactions | No |
| `blacklisted_channel_id` | Comma-separated list of channel IDs to exclude from monitoring | No |

**Usage Examples:**
- `/reaction-forward-setup` - Displays current setup
- `/reaction-forward-setup whitelisted_category_id:123456789,234567890`
- `/reaction-forward-setup blacklisted_channel_id:987654321,876543210`
- `/reaction-forward-setup whitelisted_category_id:123456789 blacklisted_channel_id:987654321`

### Link Reaction Module

#### `/link-reaction`

Configure or display the rules for link reactions by store.

| Parameter | Description | Required |
|-----------|-------------|----------|
| `store_name` | Name of the store to configure | Yes |
| `whitelisted_category_ids` | Comma-separated list of category IDs to monitor for links | Yes |
| `blacklisted_channel_ids` | Comma-separated list of channel IDs to exclude from monitoring | Yes |
| `file_path` | Path to the file containing reaction settings | Yes |

**Usage Examples:**
- `/link-reaction` - Displays all store rules
- `/link-reaction store_name:Amazon whitelisted_category_ids:123456789,234567890 blacklisted_channel_ids:987654321 file_path:/config/amazon.json`

### Other Features

#### Pinger
Monitors messages for @ mentions (everyone, here, role mentions) and sends notifications about these mentions to a configured channel. This feature runs automatically and does not require slash commands to operate.