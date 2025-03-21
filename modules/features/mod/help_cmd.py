"""
Mod Help Command

Provides help information for the mod module.
"""

import discord
from discord import app_commands
import logging
from utils.permissions import mod_only
from config.features.embed_config import embed as embed_config

logger = logging.getLogger('discord_bot.modules.mod.help_cmd')

async def handle_mod_help(interaction):
    """
    Handle the mod help command.
    
    Args:
        interaction: The Discord interaction
    """
    embed = discord.Embed(
        title="Mod Module Help",
        description="The Mod module provides moderation and management tools for your Discord server."
    )
    
    # Apply styling from embed_config
    embed = embed_config.apply_default_styling(embed)
    
    # Add general information
    embed.add_field(
        name="🔄 Reaction System",
        value="Forward messages and handle reactions.\n`/reaction` - Configure reaction system",
        inline=True
    )
    
    embed.add_field(
        name="🔔 Pinger",
        value="Monitor and notify about pings.\n`/pinger` - Configure ping monitoring",
        inline=True
    )
    
    embed.add_field(
        name="🔗 Link Reaction",
        value="Add reactions to messages containing links from supported stores.\n`/link-reaction` - Configure link reactions\n`/luisaviaroma_adder` - Configure LuisaViaRoma link reactions\n`/luisaviaroma_remover` - Remove PIDs from tracking",
        inline=False
    )
    
    # Add more detailed command examples
    examples = (
        "**Examples:**\n"
        "`/reaction whitelisted_category_id:123456789` - Set category to monitor\n"
        "`/pinger channel:123456789 everyone:true` - Configure ping notifications\n"
        "`/luisaviaroma_adder channel_ids:123456789` - Configure store monitoring"
    )
    embed.add_field(name="Command Examples", value=examples, inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

def setup_help_cmd(bot):
    """
    Set up the mod_help command.
    
    Args:
        bot: The Discord bot to add the command to
    """
    logger.info("Setting up mod_help command")
    
    @bot.tree.command(
        name="mod_help",
        description="Display help information for the mod module"
    )
    @mod_only()
    async def mod_help(interaction: discord.Interaction):
        """
        Display help information for the mod module.
        
        Args:
            interaction: The Discord interaction
        """
        await handle_mod_help(interaction)
    
    logger.info("Successfully set up mod_help command") 