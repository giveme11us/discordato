"""
path: modules/mod/pinger/__init__.py
purpose: Monitors messages for keywords and pings users when matches are found
critical:
- Maintains per-user keyword lists
- Sends notifications when keywords are matched
- Supports channel whitelisting and blacklisting
"""

import os
import re
import json
import logging
import discord
from discord import app_commands
from typing import Optional, Dict, List, Set
from .. import require_mod_role

logger = logging.getLogger('discord_bot.mod.pinger')

# Configuration
PINGER_CONFIG = {
    "enabled": True,
    "monitor_channel_ids": [],  # Empty list means all channels
    "blacklist_channel_ids": [],
    "user_keywords": {},  # user_id -> {keywords: List[str], channels: List[int]}
    "notification_channel_id": None
}

def load_config():
    """Load pinger configuration from file."""
    try:
        config_path = os.path.join("data", "pinger", "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                PINGER_CONFIG.update(config)
                logger.info("Loaded pinger configuration")
    except Exception as e:
        logger.error(f"Error loading pinger config: {e}")

def save_config():
    """Save pinger configuration to file."""
    try:
        config_path = os.path.join("data", "pinger", "config.json")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(PINGER_CONFIG, f, indent=2)
            logger.info("Saved pinger configuration")
    except Exception as e:
        logger.error(f"Error saving pinger config: {e}")

async def setup(bot):
    """Set up the pinger module."""
    # Load configuration
    load_config()
    
    # Register pinger command group
    pinger_group = app_commands.Group(name="pinger", description="Configure keyword pinging")
    
    @pinger_group.command(name="add")
    @app_commands.describe(
        user="User to add keywords for",
        keywords="Comma-separated list of keywords"
    )
    @require_mod_role()
    async def pinger_add(
        interaction: discord.Interaction,
        user: discord.Member,
        keywords: str
    ):
        """Add keywords for a user."""
        # Initialize user config if needed
        if str(user.id) not in PINGER_CONFIG["user_keywords"]:
            PINGER_CONFIG["user_keywords"][str(user.id)] = {
                "keywords": [],
                "channels": []
            }
            
        # Add new keywords
        new_keywords = [k.strip() for k in keywords.split(",")]
        user_config = PINGER_CONFIG["user_keywords"][str(user.id)]
        added = []
        
        for keyword in new_keywords:
            if keyword and keyword not in user_config["keywords"]:
                user_config["keywords"].append(keyword)
                added.append(keyword)
                
        if added:
            save_config()
            await interaction.response.send_message(
                f"Added keywords for {user.mention}: {', '.join(f'`{k}`' for k in added)}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "No new keywords were added.",
                ephemeral=True
            )
            
    @pinger_group.command(name="remove")
    @app_commands.describe(
        user="User to remove keywords from",
        keywords="Comma-separated list of keywords"
    )
    @require_mod_role()
    async def pinger_remove(
        interaction: discord.Interaction,
        user: discord.Member,
        keywords: str
    ):
        """Remove keywords for a user."""
        if str(user.id) not in PINGER_CONFIG["user_keywords"]:
            await interaction.response.send_message(
                f"No keywords found for {user.mention}",
                ephemeral=True
            )
            return
            
        # Remove keywords
        remove_keywords = [k.strip() for k in keywords.split(",")]
        user_config = PINGER_CONFIG["user_keywords"][str(user.id)]
        removed = []
        
        for keyword in remove_keywords:
            if keyword in user_config["keywords"]:
                user_config["keywords"].remove(keyword)
                removed.append(keyword)
                
        if removed:
            save_config()
            await interaction.response.send_message(
                f"Removed keywords for {user.mention}: {', '.join(f'`{k}`' for k in removed)}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "No keywords were removed.",
                ephemeral=True
            )
            
    @pinger_group.command(name="list")
    @app_commands.describe(
        user="User to list keywords for (optional)"
    )
    @require_mod_role()
    async def pinger_list(
        interaction: discord.Interaction,
        user: Optional[discord.Member] = None
    ):
        """List keywords for a user or all users."""
        if user:
            # List keywords for specific user
            if str(user.id) not in PINGER_CONFIG["user_keywords"]:
                await interaction.response.send_message(
                    f"No keywords found for {user.mention}",
                    ephemeral=True
                )
                return
                
            user_config = PINGER_CONFIG["user_keywords"][str(user.id)]
            embed = discord.Embed(
                title=f"Keywords for {user.display_name}",
                color=int(os.getenv('EMBED_COLOR', '000000'), 16)
            )
            
            if user_config["keywords"]:
                embed.add_field(
                    name="Keywords",
                    value=", ".join(f"`{k}`" for k in user_config["keywords"]),
                    inline=False
                )
            else:
                embed.description = "No keywords configured"
                
            if user_config["channels"]:
                channels = [f"<#{c}>" for c in user_config["channels"]]
                embed.add_field(
                    name="Channel Whitelist",
                    value=", ".join(channels),
                    inline=False
                )
                
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        else:
            # List all users
            if not PINGER_CONFIG["user_keywords"]:
                await interaction.response.send_message(
                    "No keywords configured for any users.",
                    ephemeral=True
                )
                return
                
            embed = discord.Embed(
                title="Keyword Configurations",
                color=int(os.getenv('EMBED_COLOR', '000000'), 16)
            )
            
            for user_id, config in PINGER_CONFIG["user_keywords"].items():
                try:
                    member = await interaction.guild.fetch_member(int(user_id))
                    if member and config["keywords"]:
                        embed.add_field(
                            name=member.display_name,
                            value=", ".join(f"`{k}`" for k in config["keywords"]),
                            inline=False
                        )
                except:
                    continue
                    
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
    @pinger_group.command(name="channel")
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
    async def pinger_channel(
        interaction: discord.Interaction,
        action: str,
        type: str,
        channel: discord.TextChannel
    ):
        """Configure channel settings."""
        config_key = f"{type}_channel_ids"
        channel_id = channel.id
        
        if action == "add":
            if channel_id not in PINGER_CONFIG[config_key]:
                PINGER_CONFIG[config_key].append(channel_id)
                save_config()
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
            if channel_id in PINGER_CONFIG[config_key]:
                PINGER_CONFIG[config_key].remove(channel_id)
                save_config()
                await interaction.response.send_message(
                    f"Removed {channel.mention} from {type} channels.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"{channel.mention} is not in {type} channels.",
                    ephemeral=True
                )
                
    @pinger_group.command(name="whitelist")
    @app_commands.describe(
        user="User to configure channel whitelist for",
        action="Whether to add or remove a channel",
        channel="The channel to add/remove"
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Add channel", value="add"),
            app_commands.Choice(name="Remove channel", value="remove")
        ]
    )
    @require_mod_role()
    async def pinger_whitelist(
        interaction: discord.Interaction,
        user: discord.Member,
        action: str,
        channel: discord.TextChannel
    ):
        """Configure user-specific channel whitelist."""
        if str(user.id) not in PINGER_CONFIG["user_keywords"]:
            PINGER_CONFIG["user_keywords"][str(user.id)] = {
                "keywords": [],
                "channels": []
            }
            
        user_config = PINGER_CONFIG["user_keywords"][str(user.id)]
        channel_id = channel.id
        
        if action == "add":
            if channel_id not in user_config["channels"]:
                user_config["channels"].append(channel_id)
                save_config()
                await interaction.response.send_message(
                    f"Added {channel.mention} to {user.mention}'s whitelist.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"{channel.mention} is already in {user.mention}'s whitelist.",
                    ephemeral=True
                )
        else:  # remove
            if channel_id in user_config["channels"]:
                user_config["channels"].remove(channel_id)
                save_config()
                await interaction.response.send_message(
                    f"Removed {channel.mention} from {user.mention}'s whitelist.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"{channel.mention} is not in {user.mention}'s whitelist.",
                    ephemeral=True
                )
                
    # Add the pinger command group to the bot
    bot.tree.add_command(pinger_group)
    logger.info("Registered pinger commands")
    
    # Register message handler
    @bot.event
    async def on_message(message):
        # Skip bot messages
        if message.author.bot:
            return
            
        # Skip if not enabled
        if not PINGER_CONFIG["enabled"]:
            return
            
        # Skip if channel is blacklisted
        if message.channel.id in PINGER_CONFIG["blacklist_channel_ids"]:
            return
            
        # Skip if monitoring specific channels and this isn't one of them
        if PINGER_CONFIG["monitor_channel_ids"] and message.channel.id not in PINGER_CONFIG["monitor_channel_ids"]:
            return
            
        # Check message against user keywords
        for user_id, config in PINGER_CONFIG["user_keywords"].items():
            # Skip if user has channel whitelist and this channel isn't in it
            if config["channels"] and message.channel.id not in config["channels"]:
                continue
                
            # Check each keyword
            for keyword in config["keywords"]:
                if re.search(rf"\b{re.escape(keyword)}\b", message.content, re.IGNORECASE):
                    try:
                        # Get the user to notify
                        user = await message.guild.fetch_member(int(user_id))
                        if not user:
                            continue
                            
                        # Create notification embed
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
                            name="Matched Keyword",
                            value=f"`{keyword}`"
                        )
                        
                        embed.add_field(
                            name="Source",
                            value=f"[Jump to message]({message.jump_url})"
                        )
                        
                        # Send notification
                        if PINGER_CONFIG["notification_channel_id"]:
                            channel = bot.get_channel(PINGER_CONFIG["notification_channel_id"])
                            if channel:
                                await channel.send(content=user.mention, embed=embed)
                        else:
                            try:
                                await user.send(embed=embed)
                            except:
                                logger.warning(f"Could not DM user {user_id}")
                                
                    except Exception as e:
                        logger.error(f"Error sending notification: {e}")
                        
async def teardown(bot):
    """Clean up the pinger module."""
    # Save configuration
    save_config()
    logger.info("Saved pinger configuration") 