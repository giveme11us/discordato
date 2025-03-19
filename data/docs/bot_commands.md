# Discord Bot Commands & Features

## Module Overview

| Module | Feature | Description | Commands |
|--------|---------|-------------|----------|
| **mod** | Keyword Filter | Automatically detects keywords in messages and forwards them to a notification channel | `/keyword-filter-config`, `/keyword-filter-quicksetup` |
| **mod** | Reaction Forward | Forwards messages to a destination channel when a specific reaction is added | *No slash commands, reaction-based* |
| **mod** | Link Reaction | Automatically adds reactions to messages containing links | *No slash commands, automatic* |
| **mod** | Pinger | Monitors for @ mentions and sends notifications | *No slash commands, automatic* |
| **instore** | In-store Monitoring | Features related to in-store product monitoring | *Commands not visible in provided code* |
| **online** | Online Monitoring | Features related to online product monitoring | *Commands not visible in provided code* |

## Detailed Command Reference

### Keyword Filter Module

#### `/keyword-filter-config`

Command to configure all aspects of the keyword filter functionality.

| Option | Sub-option | Description |
|--------|------------|-------------|
| `view` | | Display current configuration including status, categories, and filters |
| `enable` | | Enable the keyword filter feature |
| `disable` | | Disable the keyword filter feature |
| `categories` | | Manage monitored categories |
| | `add` | Add a category to the monitoring whitelist |
| | `remove` | Remove a category from the monitoring whitelist |
| | `list` | List all currently monitored categories |
| `blacklist` | | Manage blacklisted channels |
| | `add` | Add a channel to the blacklist (won't be monitored) |
| | `remove` | Remove a channel from the blacklist |
| | `list` | List all currently blacklisted channels |
| `notification` | | Configure notification settings |
| | `channel` | Set the notification channel where alerts are sent |
| | `enable` | Enable sending notifications for filtered messages |
| | `disable` | Disable sending notifications for filtered messages |
| `dry_run` | | Toggle dry run mode (detect but don't take action) |
| | `enable` | Enable dry run mode |
| | `disable` | Disable dry run mode |
| `filters` | | Manage keyword filters |
| | `<filter_id> enable` | Enable a specific filter |
| | `<filter_id> disable` | Disable a specific filter |
| | `<filter_id> description "text"` | Update filter description |
| | `<filter_id> action log/notify/delete` | Set the action taken when filter matches |
| | `<filter_id> severity low/medium/high` | Set the severity level of the filter |
| | `<filter_id> patterns add "pattern"` | Add a keyword pattern to the filter |
| | `<filter_id> patterns remove <index>` | Remove a pattern by index |
| | `<filter_id> patterns set "pattern1,pattern2"` | Set all patterns at once |
| | `<filter_id> remove` | Delete the filter completely |
| | `add <name> "description"` | Create a new filter |

#### `/keyword-filter-quicksetup`

Quickly set up keyword filtering with a single command.

| Parameter | Description |
|-----------|-------------|
| `source_channel` | Channel or category ID to monitor |
| `notification_channel` | Channel ID where alerts should be sent |
| `keywords` | Comma-separated list of keywords to detect |

### Other Features

#### Reaction Forward
Messages can be forwarded to a designated channel by adding a specific reaction. The module automatically detects the reaction and handles the forwarding process.

#### Link Reaction
Automatically adds configured reactions to messages containing links, making it easier to identify and manage messages with external URLs.

#### Pinger
Monitors messages for @ mentions (everyone, here, role mentions) and sends notifications about these mentions to a configured channel. 