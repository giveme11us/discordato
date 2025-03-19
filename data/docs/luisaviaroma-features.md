# LuisaViaRoma Integration Features

This document outlines the LuisaViaRoma integration features available in the Discord bot, including link detection, product ID extraction, and management commands.

## Overview

The LuisaViaRoma integration provides functionality for:

1. **Link Detection**: Automatically detecting LuisaViaRoma product links in messages
2. **Link Reaction**: Adding reaction emojis to messages containing LuisaViaRoma links
3. **Product ID Extraction**: Extracting product IDs from links and embeds
4. **Product Tracking**: Maintaining lists of tracked product IDs in configurable files
5. **User Commands**: Adding and removing product IDs through commands and context menus

## Configuration Commands

### `/luisaviaroma_adder` Command

The `luisaviaroma_adder` command allows you to configure the link detection and product ID extraction settings.

**Usage:**
- `/luisaviaroma_adder` - Shows current LuisaViaRoma configuration
- `/luisaviaroma_adder channel_ids:123456789,987654321` - Sets channels to monitor (keeps existing file path)
- `/luisaviaroma_adder file_path:/path/to/luisaviaroma_ids.txt` - Updates the file path (keeps existing channels)
- `/luisaviaroma_adder channel_ids:123456789,987654321 file_path:/path/to/luisaviaroma_ids.txt` - Fully configures both channels and file path

When configured, the bot will:
1. Monitor the specified channels for LuisaViaRoma embeds
2. Add a 🔗 reaction to messages containing LuisaViaRoma content
3. Allow whitelisted users to click the reaction to save product IDs

### `/luisaviaroma_remover` Command

The `luisaviaroma_remover` command lets you remove product IDs from the tracking file and manage the configuration.

**Usage:**
- `/luisaviaroma_remover` - Shows current LuisaViaRoma configuration
- `/luisaviaroma_remover pid:ABC123` - Removes the specified product ID from the tracking file
- `/luisaviaroma_remover channel_ids:123456789,987654321` - Updates the channels to monitor
- `/luisaviaroma_remover file_path:/path/to/luisaviaroma_ids.txt` - Updates the file path
- `/luisaviaroma_remover channel_ids:123456789,987654321 file_path:/path/to/luisaviaroma_ids.txt` - Fully configures both channels and file path

## Context Menu Commands

The bot also provides context menu commands for convenient interaction:

**Remove PID**
- Right-click on a user who has posted a product ID
- Select "Remove PID" from the Apps section of the context menu
- The bot will find the most recent message from that user containing a product ID and remove it from the tracking file

This context menu command makes it easy to remove products from tracking without having to copy and paste the product ID.

## Detection Methods

The LuisaViaRoma integration uses various methods to detect product content:

1. **Author Name**: Detects embeds with author name "LUISAVIAROMA"
2. **URL Pattern**: Extracts product IDs from URLs following LuisaViaRoma's URL format
3. **Field Detection**: Extracts product IDs from embed fields marked as "PID"

## Message Flow

When a user with appropriate permissions clicks the 🔗 reaction on a message containing a LuisaViaRoma product:

1. The bot extracts the product ID from the message
2. It checks if the ID already exists in the tracking file
3. If new, it adds the ID to the file
4. A direct message is sent to the user confirming the action
5. All confirmation messages are sent as direct messages for privacy

Similarly, when using the remover:

1. The bot searches for the specified ID in the tracking file
2. If found, it removes the ID and all associated empty lines
3. A confirmation message is sent to the user

## Permissions

Both the adder and remover features respect the same permission system:

- Both commands require the user to have roles specified in `MOD_WHITELIST_ROLE_IDS`
- The context menu command is only available to users with appropriate permissions
- All responses are private/ephemeral to maintain privacy

## File Format

The tracking file uses a simple line-based format:
- Each product ID is stored on its own line
- Empty lines are automatically cleaned up
- The file is created automatically if it doesn't exist

## Technical Implementation

The features are implemented across several files:
- `link_reaction.py` - Core detection and reaction functionality
- `remover.py` - Functionality for removing PIDs from tracking
- `command_sync.py` - Command registration including context menu
- `store_manager.py` - Store configuration management

## Troubleshooting

If the context menu command doesn't appear:
1. Ensure the bot has the `applications.commands` scope
2. Verify the command is registered by checking logs
3. Try restarting your Discord client
4. Wait a few minutes as Discord can take time to update application commands

If tracking isn't working:
1. Verify the channels are correctly configured
2. Check that the file path is accessible to the bot
3. Make sure the detection settings are properly configured
4. Ensure messages contain valid LuisaViaRoma product information 