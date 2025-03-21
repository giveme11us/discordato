"""
path: modules/mod/reaction/__init__.py
purpose: Manages reaction-based message forwarding and product link detection
critical:
- Requires channel configuration
- Handles reaction-based forwarding
- Manages product link detection
"""

import os
import logging
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

logger = logging.getLogger('discord_bot.mod.reaction')

# Default configuration
REACTION_CONFIG = {
    "ENABLED": False,
    "CATEGORY_IDS": [],
    "MONITOR_CHANNEL_IDS": [],
    "FORWARD_EMOJI": "➡️",
    "NOTIFICATION_CHANNEL_ID": None
}

async def setup(bot):
    """
    Set up the reaction module.
    
    Args:
        bot: The Discord bot instance
    """
    # Register reaction command group
    reaction_group = app_commands.Group(name="reaction", description="Manage reaction settings")
    
    @reaction_group.command(name="enable")
    @app_commands.describe(
        channel="Channel to enable reactions in",
        category="Category to enable reactions in"
    )
    async def reaction_enable(
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None,
        category: Optional[discord.CategoryChannel] = None
    ):
        # Check if user has moderator role
        if not any(role.id in bot.config.MOD_WHITELIST_ROLE_IDS for role in interaction.user.roles):
            await interaction.response.send_message(
                "You need moderator permissions to use this command.",
                ephemeral=True
            )
            return
        
        if channel:
            if channel.id not in REACTION_CONFIG["MONITOR_CHANNEL_IDS"]:
                REACTION_CONFIG["MONITOR_CHANNEL_IDS"].append(channel.id)
            await interaction.response.send_message(
                f"Enabled reactions in {channel.mention}",
                ephemeral=True
            )
        elif category:
            if category.id not in REACTION_CONFIG["CATEGORY_IDS"]:
                REACTION_CONFIG["CATEGORY_IDS"].append(category.id)
            await interaction.response.send_message(
                f"Enabled reactions in category {category.name}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Please specify a channel or category.",
                ephemeral=True
            )
    
    @reaction_group.command(name="disable")
    @app_commands.describe(
        channel="Channel to disable reactions in",
        category="Category to disable reactions in"
    )
    async def reaction_disable(
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None,
        category: Optional[discord.CategoryChannel] = None
    ):
        # Check if user has moderator role
        if not any(role.id in bot.config.MOD_WHITELIST_ROLE_IDS for role in interaction.user.roles):
            await interaction.response.send_message(
                "You need moderator permissions to use this command.",
                ephemeral=True
            )
            return
        
        if channel:
            if channel.id in REACTION_CONFIG["MONITOR_CHANNEL_IDS"]:
                REACTION_CONFIG["MONITOR_CHANNEL_IDS"].remove(channel.id)
            await interaction.response.send_message(
                f"Disabled reactions in {channel.mention}",
                ephemeral=True
            )
        elif category:
            if category.id in REACTION_CONFIG["CATEGORY_IDS"]:
                REACTION_CONFIG["CATEGORY_IDS"].remove(category.id)
            await interaction.response.send_message(
                f"Disabled reactions in category {category.name}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Please specify a channel or category.",
                ephemeral=True
            )
    
    @reaction_group.command(name="settings")
    async def reaction_settings(interaction: discord.Interaction):
        # Check if user has moderator role
        if not any(role.id in bot.config.MOD_WHITELIST_ROLE_IDS for role in interaction.user.roles):
            await interaction.response.send_message(
                "You need moderator permissions to use this command.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="Reaction Settings",
            color=int(os.getenv('EMBED_COLOR', '000000'), 16)
        )
        
        # Add enabled status
        embed.add_field(
            name="Status",
            value="Enabled" if REACTION_CONFIG["ENABLED"] else "Disabled",
            inline=False
        )
        
        # Add monitored channels
        monitored_channels = []
        for channel_id in REACTION_CONFIG["MONITOR_CHANNEL_IDS"]:
            channel = interaction.guild.get_channel(channel_id)
            if channel:
                monitored_channels.append(channel.mention)
        
        embed.add_field(
            name="Monitored Channels",
            value="\n".join(monitored_channels) if monitored_channels else "None",
            inline=False
        )
        
        # Add monitored categories
        monitored_categories = []
        for category_id in REACTION_CONFIG["CATEGORY_IDS"]:
            category = interaction.guild.get_channel(category_id)
            if category:
                monitored_categories.append(category.name)
        
        embed.add_field(
            name="Monitored Categories",
            value="\n".join(monitored_categories) if monitored_categories else "None",
            inline=False
        )
        
        # Add forward emoji
        embed.add_field(
            name="Forward Emoji",
            value=REACTION_CONFIG["FORWARD_EMOJI"],
            inline=False
        )
        
        # Add notification channel
        notification_channel = None
        if REACTION_CONFIG["NOTIFICATION_CHANNEL_ID"]:
            notification_channel = interaction.guild.get_channel(REACTION_CONFIG["NOTIFICATION_CHANNEL_ID"])
        
        embed.add_field(
            name="Notification Channel",
            value=notification_channel.mention if notification_channel else "Not set",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Add the reaction command group to the bot
    bot.tree.add_command(reaction_group)
    logger.info("Registered reaction commands")
    
    # Register reaction listener
    @bot.event
    async def on_raw_reaction_add(payload):
        # Skip bot reactions
        if payload.member.bot:
            return
        
        # Skip if reactions are disabled
        if not REACTION_CONFIG["ENABLED"]:
            return
        
        # Get the channel
        channel = bot.get_channel(payload.channel_id)
        if not channel:
            return
        
        # Check if channel is monitored
        if (channel.id not in REACTION_CONFIG["MONITOR_CHANNEL_IDS"] and
            (not channel.category or channel.category.id not in REACTION_CONFIG["CATEGORY_IDS"])):
            return
        
        # Check if it's the forward emoji
        if str(payload.emoji) != REACTION_CONFIG["FORWARD_EMOJI"]:
            return
        
        try:
            # Get the message
            message = await channel.fetch_message(payload.message_id)
            
            # Get the notification channel
            if not REACTION_CONFIG["NOTIFICATION_CHANNEL_ID"]:
                return
            
            notification_channel = bot.get_channel(REACTION_CONFIG["NOTIFICATION_CHANNEL_ID"])
            if not notification_channel:
                return
            
            # Create forward embed
            embed = discord.Embed(
                title="Message Forwarded",
                description=message.content,
                color=int(os.getenv('EMBED_COLOR', '000000'), 16)
            )
            
            embed.add_field(
                name="Author",
                value=f"{message.author.mention} ({message.author.name})",
                inline=True
            )
            
            embed.add_field(
                name="Channel",
                value=message.channel.mention,
                inline=True
            )
            
            embed.add_field(
                name="Forwarded by",
                value=f"{payload.member.mention} ({payload.member.name})",
                inline=True
            )
            
            # Add message link
            embed.add_field(
                name="Original Message",
                value=f"[Click here]({message.jump_url})",
                inline=False
            )
            
            # Forward any attachments
            files = []
            for attachment in message.attachments:
                try:
                    files.append(await attachment.to_file())
                except Exception as e:
                    logger.error(f"Error downloading attachment: {e}")
            
            await notification_channel.send(embed=embed, files=files)
            logger.info(f"Forwarded message {message.id} to {notification_channel.name}")
            
        except discord.NotFound:
            logger.error(f"Message {payload.message_id} not found")
        except discord.Forbidden:
            logger.error("Missing permissions to forward message")
        except Exception as e:
            logger.error(f"Error forwarding message: {e}")

async def teardown(bot):
    """Clean up the reaction module."""
    pass 