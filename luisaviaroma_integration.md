# LuisaViaRoma Integration

This document describes the specialized integration with LuisaViaRoma for the Discord bot.

## Overview

The bot includes specialized functionality to detect LuisaViaRoma product embeds in Discord messages, add a link reaction emoji, and extract product IDs when users interact with these embeds.

## Features

- **Automated Detection**: Recognizes embeds with LuisaViaRoma as the author
- **Channel Monitoring**: Monitors specific channels for LuisaViaRoma content
- **Product ID Extraction**: Extracts product IDs from URLs or embed fields
- **Duplicate Prevention**: Checks for existing IDs before saving
- **Dedicated Command**: Simplified `/luisaviaroma_adder` command for configuration

## Setup Process

### Using the LuisaViaRoma Adder Command

Use the `/luisaviaroma_adder` command to configure the integration:

```
/luisaviaroma_adder channel_ids:123456789,987654321 file_path:/path/to/ids.txt
```

This command will:
1. Enable the link reaction feature if it's disabled
2. Create or update the LuisaViaRoma store configuration
3. Configure the specified channels to be monitored
4. Set the file path where product IDs will be saved

### Configuration Options

The `/luisaviaroma_adder` command accepts these parameters:

| Parameter | Description | Required |
|-----------|-------------|----------|
| `channel_ids` | Comma-separated list of Discord channel IDs to monitor | No |
| `file_path` | File path where extracted product IDs will be saved | No |

If no parameters are provided, the command displays the current configuration.

## Technical Implementation

### Detection Process

The bot detects LuisaViaRoma content through several checks:

1. **Author Name Check**: The primary detection is based on the embed author name "LUISAVIAROMA"
2. **Channel Restrictions**: Only processes messages in the configured channels
3. **User Filtering**: Applies whitelist role checks for user-posted messages

Example detection code:
```python
if embed.author and embed.author.name == "LUISAVIAROMA":
    logger.info(f"Found LuisaViaRoma embed")
    # Process the embed
```

### Product ID Extraction

When a user with appropriate permissions adds the link emoji reaction, the bot extracts the product ID using these methods:

1. **URL Extraction** (Primary method):
   - Parses the URL from the embed (example: `https://www.luisaviaroma.com/en-it/p/sneakers/81I-DL1057`)
   - Applies a regex pattern to extract the ID portion (`81I-DL1057`)

2. **Field Extraction** (Fallback method):
   - Looks for a field named "PID" in the embed
   - Extracts the product ID from the field content

Example extraction code:
```python
# Try URL extraction first
if embed.url:
    logger.info(f"Trying URL extraction for LuisaViaRoma")
    # Extract from URL pattern
    url_parts = embed.url.split('/')
    if url_parts and len(url_parts) > 1:
        potential_pid = url_parts[-1]
        # Check if it matches LuisaViaRoma PID format (usually has hyphens)
        if '-' in potential_pid:
            pid_value = potential_pid
            logger.info(f"Extracted product ID from URL: {pid_value}")
```

### Storage Format

The product IDs are stored one per line in the configured file:
```
81I-DL1057
81I-DL2345
81I-DL6789
```

## Command Output

When you run the command without parameters, it displays an embed with the current configuration:

- **Status**: Enabled/Disabled
- **Monitored Channels**: List of configured channels
- **File Path**: Where product IDs are being saved
- **Detection Configuration**: Details about how embeds are recognized
- **Fixed Configuration**: Emoji and domain settings

## Typical Usage Flow

1. A monitor bot or user posts a LuisaViaRoma product in a monitored channel
2. The bot automatically adds a 🔗 reaction to the message
3. A user with appropriate permissions clicks the 🔗 reaction
4. The bot extracts the product ID and saves it to the configured file
5. The bot confirms the extraction with a message in the channel

## Example Message Format

A typical LuisaViaRoma embed will contain these elements:
- **Title**: Product name and brand
- **Author**: "LUISAVIAROMA"
- **URL**: Link to the product
- **Image**: Product thumbnail
- **Fields**:
  - PID: The product ID
  - PRICE: The product price
  - SIZES: Available sizes
  - UNCACHED LINK: Direct link to the product
  - QUICK TASK: Links to various automation tools

## Troubleshooting

If you encounter issues with the LuisaViaRoma integration:

1. **No reaction added to embeds**:
   - Ensure the feature is enabled
   - Verify the channel is in the configured channel list
   - Check that the embed has "LUISAVIAROMA" as the author

2. **Reaction added but ID not saved**:
   - Ensure the user has whitelisted roles
   - Verify the file path is valid and writable
   - Check logs for extraction errors

3. **Wrong IDs being extracted**:
   - Examine the URL pattern in the configuration
   - Check if the embed has a properly formatted PID field

## Future Enhancements

Planned improvements for the LuisaViaRoma integration:

1. **Multi-region Support**: Configure different extraction patterns for different regions
2. **Size Tracking**: Extract and track available sizes
3. **Price Monitoring**: Track price changes over time
4. **Automatic Notifications**: Alert when specific products or sizes become available 