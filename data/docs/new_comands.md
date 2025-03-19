# Discord Bot Commands & Features

## Module Overview

| Module | Feature | Description | Commands |
|--------|---------|-------------|----------|
| **mod** | Keyword Filter | Automatically detects keywords in messages and forwards them to a notification channel | `/keyword-filter-setup` |
| **mod** | Reaction Forward | Forwards messages to a destination channel when a specific reaction is added | `/reaction-forward-setup` |
| **mod** | Link Reaction | Automatically adds reactions to messages containing links from supported stores | `/link-reaction`, `/luisaviaroma_adder` |
| **mod** | Pinger | Monitors for @ mentions and sends notifications | *No slash commands, automatic* |
| **instore** | In-store Monitoring | Features related to in-store product monitoring | *Commands not visible in provided code* |
| **online** | Online Monitoring | Features related to online product monitoring | *Commands not visible in provided code* |
| **redeye** | Profile Management | View and manage profiles stored in CSV files | `/redeye-profiles`, `/redeye-config` |

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
| `store_name` | Name of the store to configure | No |
| `whitelisted_category_ids` | Comma-separated list of category IDs to monitor for links | No |
| `blacklisted_channel_ids` | Comma-separated list of channel IDs to exclude from monitoring | No |
| `file_path` | Path to the file containing reaction settings | No |

**Usage Examples:**
- `/link-reaction` - Displays all store rules
- `/link-reaction store_name:Amazon` - Displays rules for a specific store
- `/link-reaction store_name:Amazon whitelisted_category_ids:123456789,234567890 blacklisted_channel_ids:987654321 file_path:/config/amazon.json`

#### `/luisaviaroma_adder`

Specialized command to configure LuisaViaRoma link reactions with simplified parameters.

| Parameter | Description | Required |
|-----------|-------------|----------|
| `channel_ids` | Comma-separated list of channel IDs to monitor for LuisaViaRoma links | No |
| `file_path` | Path to the file where extracted product IDs will be saved | No |

**Usage Examples:**
- `/luisaviaroma_adder` - Displays current LuisaViaRoma configuration
- `/luisaviaroma_adder channel_ids:123456789,987654321` - Sets channels to monitor (keeps existing file path)
- `/luisaviaroma_adder file_path:/path/to/luisaviaroma_ids.txt` - Updates the file path (keeps existing channels)
- `/luisaviaroma_adder channel_ids:123456789,987654321 file_path:/path/to/luisaviaroma_ids.txt` - Fully configures both channels and file path

### Redeye Module

#### `/redeye-profiles`

View profiles stored in the profiles CSV file.

| Parameter | Description | Required |
|-----------|-------------|----------|
| `profile_name` | Name of a specific profile to view in detail | No |

**Usage Examples:**
- `/redeye-profiles` - Displays all profiles with basic information
- `/redeye-profiles profile_name:MyProfile1` - Shows detailed information for a specific profile

#### `/redeye-config`

Configure the Redeye module settings.

| Parameter | Description | Required |
|-----------|-------------|----------|
| `profiles_path` | Path to the profiles CSV file | No |
| `tasks_path` | Path to the tasks CSV file | No |

**Usage Examples:**
- `/redeye-config` - Displays current configuration
- `/redeye-config profiles_path:/path/to/profiles.csv` - Updates profiles CSV path
- `/redeye-config tasks_path:/path/to/tasks.csv` - Updates tasks CSV path
- `/redeye-config profiles_path:/path/to/profiles.csv tasks_path:/path/to/tasks.csv` - Updates both file paths

### Other Features

#### Pinger
Monitors messages for @ mentions (everyone, here, role mentions) and sends notifications about these mentions to a configured channel. This feature runs automatically and does not require slash commands to operate.

## Store Configuration Format

The Link Reaction system now uses a dictionary-based configuration for stores, with this structure:

```json
{
  "store_id": {
    "enabled": true,
    "name": "Store Display Name",
    "description": "Description of what this store configuration does",
    "channel_ids": [123456789, 987654321],
    "detection": {
      "type": "author_name|title_contains|url_contains",
      "value": "value to match"
    },
    "extraction": {
      "primary": "url|field_name",
      "pattern": "regex pattern to extract ID",
      "fallback": "alternative field to check"
    },
    "file_path": "/path/to/store_ids.txt"
  }
}
```

**Detection Types:**
- `author_name`: Checks if embed author name contains the detection value
- `title_contains`: Checks if embed title contains the detection value
- `url_contains`: Checks if embed URL contains the detection value

**Extraction Methods:**
- `url`: Extracts product ID from the URL using the regex pattern
- `field_name`: Looks for a field with this name to extract the product ID