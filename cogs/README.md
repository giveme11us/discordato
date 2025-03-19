# Discord Bot Cogs

This directory contains the Discord.py cogs used by the bot. Cogs are extension modules that organize related commands and event handlers into a single class.

## Current Cogs

- **general_cog.py**: Provides general utility commands like ping and purge
- **config_cog.py**: Contains all configuration commands for different modules
- **keyword_filter_cog.py**: Monitors messages for problematic content using regex patterns
- **link_reaction_cog.py**: Adds a link emoji to messages containing embeds from supported stores
- **reaction_forward_cog.py**: Adds a forward arrow reaction to messages in specified categories
- **pinger_cog.py**: Monitors mentions (@everyone, @here, and role mentions) and sends notifications
- **redeye_cog.py**: Manages role-based waitlists with status tracking and notifications

## Adding a New Cog

To add a new cog to the bot:

1. Create a new file in this directory with the naming pattern `feature_cog.py`
2. Implement your cog class following this template:

```python
import discord
from discord.ext import commands
import logging

logger = logging.getLogger('discord_bot.cogs.your_cog_name')

class YourCogName(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Initializing Your Cog Name")
    
    async def cog_load(self):
        logger.info("Loading Your Cog Name")
        # Setup code here
    
    # Add commands using @commands.command() decorator
    # Add event handlers using @commands.Cog.listener() decorator

async def setup(bot):
    await bot.add_cog(YourCogName(bot))
    logger.info("Your Cog Name added to bot")
```

3. Update `discord_bot.py` to load your new cog:

```python
try:
    await bot.load_extension("cogs.your_cog_name")
    logger.info("Loaded your cog name")
except Exception as e:
    logger.error(f"Error loading your cog name: {str(e)}")
```

## Benefits of Cog-Based Architecture

- **Organized Code**: Related functionality is grouped together
- **Lifecycle Management**: Cogs provide `cog_load` and `cog_unload` hooks
- **Simplified Maintenance**: Each cog can be enabled/disabled independently 
- **Reduced Duplication**: Common setup code is in the cog rather than scattered throughout the application
- **Discord.py Best Practice**: Following the recommended architecture pattern 