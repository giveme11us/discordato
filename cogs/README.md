# Discord Bot Cogs

This directory contains the cogs (modular components) for the Discord bot.

## Available Cogs

- **config_cog.py**: Handles configuration commands for all modules
- **link_reaction_cog.py**: Manages reactions to store links
- **pinger_cog.py**: Monitors and notifies about mentions
- **reaction_forward_cog.py**: Forwards messages based on reactions

## Development

When adding a new cog:
1. Create a new file named `your_feature_cog.py`
2. Implement the cog class inheriting from `commands.Cog`
3. Add setup and teardown functions
4. Register the cog in `discord_bot.py`

Example:
```python
from discord.ext import commands

class YourFeatureCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def cog_load(self):
        # Setup code
        pass
        
    async def cog_unload(self):
        # Cleanup code
        pass

async def setup(bot):
    await bot.add_cog(YourFeatureCog(bot))
```

## Benefits of Cog-Based Architecture

- **Organized Code**: Related functionality is grouped together
- **Lifecycle Management**: Cogs provide `cog_load` and `cog_unload` hooks
- **Simplified Maintenance**: Each cog can be enabled/disabled independently 
- **Reduced Duplication**: Common setup code is in the cog rather than scattered throughout the application
- **Discord.py Best Practice**: Following the recommended architecture pattern 