"""
path: modules/mod/link_reaction/__init__.py
purpose: Monitors messages for product links and adds reactions for tracking
critical:
- Detects product links using regex patterns
- Adds configured reactions to messages with links
- Supports message forwarding via reactions
"""

import os
import re
import logging
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Dict, List
from .. import require_mod_role

logger = logging.getLogger('discord_bot.mod.link_reaction')

# Configuration
LINK_REACTION_WHITELIST_ROLE_IDS = [int(id) for id in os.getenv('LINK_REACTION_WHITELIST_ROLE_IDS', '').split(',') if id]

# Default configuration
REACTION_CONFIG = {
    "enabled": True,
    "monitor_channel_ids": [],  # Empty list means all channels
    "blacklist_channel_ids": [],
    "forward_emoji": "➡️",  # Default forward emoji
    "forward_channel_id": None,  # Channel to forward messages to
    "link_patterns": {
        # Pattern name -> {regex: str, emoji: str, description: str}
        "amazon": {
            "regex": r"https?://(?:www\.)?amazon\.(?:\w{2,3})(?:/|\w)\S+",
            "emoji": "🛒",
            "description": "Amazon product links"
        },
        "ebay": {
            "regex": r"https?://(?:www\.)?ebay\.(?:\w{2,3})/\S+",
            "emoji": "📦",
            "description": "eBay listings"
        }
    }
}

async def setup(bot):
    """
    Set up the link reaction module.
    
    Args:
        bot: The Discord bot instance
    """
    # Register reaction command group
    reaction_group = app_commands.Group(name="reaction", description="Configure link reactions")
    
    @reaction_group.command(name="add")
    @app_commands.describe(
        name="Name for this link pattern",
        pattern="Regular expression pattern to match links",
        emoji="Emoji to react with",
        description="Description of what this pattern matches"
    )
    @require_mod_role()
    async def reaction_add(
        interaction: discord.Interaction,
        name: str,
        pattern: str,
        emoji: str,
        description: str
    ):
        """Add a new link pattern."""
        try:
            # Validate pattern
            re.compile(pattern)
            
            # Add pattern to config
            REACTION_CONFIG["link_patterns"][name] = {
                "regex": pattern,
                "emoji": emoji,
                "description": description
            }
            
            await interaction.response.send_message(
                f"Added link pattern '{name}' with emoji {emoji}",
                ephemeral=True
            )
            
        except re.error:
            await interaction.response.send_message(
                "Invalid regex pattern.",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Error adding link pattern: {e}", exc_info=True)
            await interaction.response.send_message(
                "An error occurred while adding the pattern.",
                ephemeral=True
            )
            
    @reaction_group.command(name="remove")
    @app_commands.describe(
        name="Name of the pattern to remove"
    )
    @require_mod_role()
    async def reaction_remove(
        interaction: discord.Interaction,
        name: str
    ):
        """Remove a link pattern."""
        if name in REACTION_CONFIG["link_patterns"]:
            del REACTION_CONFIG["link_patterns"][name]
            await interaction.response.send_message(
                f"Removed link pattern '{name}'",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"Pattern '{name}' not found.",
                ephemeral=True
            )
            
    @reaction_group.command(name="list")
    @require_mod_role()
    async def reaction_list(interaction: discord.Interaction):
        """List all link patterns."""
        if not REACTION_CONFIG["link_patterns"]:
            await interaction.response.send_message(
                "No link patterns configured.",
                ephemeral=True
            )
            return
            
        embed = discord.Embed(
            title="Link Reaction Patterns",
            color=int(os.getenv('EMBED_COLOR', '000000'), 16)
        )
        
        for name, pattern in REACTION_CONFIG["link_patterns"].items():
            embed.add_field(
                name=f"{name} {pattern['emoji']}",
                value=f"Pattern: `{pattern['regex']}`\n{pattern['description']}",
                inline=False
            )
            
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    @reaction_group.command(name="test")
    @app_commands.describe(
        text="Text to test against active patterns"
    )
    @require_mod_role()
    async def reaction_test(
        interaction: discord.Interaction,
        text: str
    ):
        """Test text against link patterns."""
        matches = []
        for name, pattern in REACTION_CONFIG["link_patterns"].items():
            if re.search(pattern["regex"], text):
                matches.append(f"{name} {pattern['emoji']}")
                
        if matches:
            await interaction.response.send_message(
                f"Matched patterns:\n" + "\n".join(matches),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "No patterns matched.",
                ephemeral=True
            )
            
    @reaction_group.command(name="channel")
    @app_commands.describe(
        action="Whether to add or remove a channel",
        type="Whether this is for monitoring or blacklist",
        channel="The channel to add/remove"
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Add channel", value="add"),
            app_commands.Choice(name="Remove channel", value="remove")
        ],
        type=[
            app_commands.Choice(name="Monitor channel", value="monitor"),
            app_commands.Choice(name="Blacklist channel", value="blacklist")
        ]
    )
    @require_mod_role()
    async def reaction_channel(
        interaction: discord.Interaction,
        action: str,
        type: str,
        channel: discord.TextChannel
    ):
        """Configure channel settings."""
        config_key = f"{type}_channel_ids"
        channel_id = channel.id
        
        if action == "add":
            if channel_id not in REACTION_CONFIG[config_key]:
                REACTION_CONFIG[config_key].append(channel_id)
                await interaction.response.send_message(
                    f"Added {channel.mention} to {type} channels.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"{channel.mention} is already in {type} channels.",
                    ephemeral=True
                )
        else:  # remove
            if channel_id in REACTION_CONFIG[config_key]:
                REACTION_CONFIG[config_key].remove(channel_id)
                await interaction.response.send_message(
                    f"Removed {channel.mention} from {type} channels.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"{channel.mention} is not in {type} channels.",
                    ephemeral=True
                )
                
    @reaction_group.command(name="forward")
    @app_commands.describe(
        action="Whether to set or remove the forward channel",
        channel="The channel to forward messages to",
        emoji="Custom emoji to use for forwarding (optional)"
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Set forward channel", value="set"),
            app_commands.Choice(name="Remove forward channel", value="remove")
        ]
    )
    @require_mod_role()
    async def reaction_forward(
        interaction: discord.Interaction,
        action: str,
        channel: Optional[discord.TextChannel] = None,
        emoji: Optional[str] = None
    ):
        """Configure message forwarding."""
        if action == "set":
            if not channel:
                await interaction.response.send_message(
                    "Channel is required when setting forward channel.",
                    ephemeral=True
                )
                return
                
            REACTION_CONFIG["forward_channel_id"] = channel.id
            if emoji:
                REACTION_CONFIG["forward_emoji"] = emoji
                
            await interaction.response.send_message(
                f"Set forward channel to {channel.mention} with emoji {REACTION_CONFIG['forward_emoji']}",
                ephemeral=True
            )
        else:  # remove
            REACTION_CONFIG["forward_channel_id"] = None
            await interaction.response.send_message(
                "Removed forward channel configuration.",
                ephemeral=True
            )
            
    # Add the reaction command group to the bot
    bot.tree.add_command(reaction_group)
    logger.info("Registered link reaction commands")
    
    # Register message handler
    @bot.event
    async def on_message(message):
        # Skip bot messages
        if message.author.bot:
            return
            
        # Skip if not enabled
        if not REACTION_CONFIG["enabled"]:
            return
            
        # Skip if channel is blacklisted
        if message.channel.id in REACTION_CONFIG["blacklist_channel_ids"]:
            return
            
        # Skip if monitoring specific channels and this isn't one of them
        if REACTION_CONFIG["monitor_channel_ids"] and message.channel.id not in REACTION_CONFIG["monitor_channel_ids"]:
            return
            
        # Check message against patterns
        for pattern in REACTION_CONFIG["link_patterns"].values():
            if re.search(pattern["regex"], message.content):
                try:
                    await message.add_reaction(pattern["emoji"])
                except Exception as e:
                    logger.error(f"Error adding reaction: {e}")
                    
        # Add forward reaction if configured
        if REACTION_CONFIG["forward_channel_id"]:
            try:
                await message.add_reaction(REACTION_CONFIG["forward_emoji"])
            except Exception as e:
                logger.error(f"Error adding forward reaction: {e}")
                
    # Register reaction handler
    @bot.event
    async def on_raw_reaction_add(payload):
        # Skip bot reactions
        if payload.user_id == bot.user.id:
            return
            
        # Skip if not enabled or no forward channel configured
        if not REACTION_CONFIG["enabled"] or not REACTION_CONFIG["forward_channel_id"]:
            return
            
        # Skip if not the forward emoji
        if str(payload.emoji) != REACTION_CONFIG["forward_emoji"]:
            return
            
        try:
            # Get the source channel and message
            source_channel = bot.get_channel(payload.channel_id)
            message = await source_channel.fetch_message(payload.message_id)
            
            # Get the forward channel
            forward_channel = bot.get_channel(REACTION_CONFIG["forward_channel_id"])
            
            if forward_channel:
                # Create embed for forwarded message
                embed = discord.Embed(
                    description=message.content,
                    timestamp=message.created_at,
                    color=int(os.getenv('EMBED_COLOR', '000000'), 16)
                )
                
                embed.set_author(
                    name=message.author.display_name,
                    icon_url=message.author.display_avatar.url
                )
                
                embed.add_field(
                    name="Source",
                    value=f"[Jump to message]({message.jump_url})"
                )
                
                # Forward the message
                await forward_channel.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error forwarding message: {e}")
            
async def teardown(bot):
    """Clean up the link reaction module."""
    pass 