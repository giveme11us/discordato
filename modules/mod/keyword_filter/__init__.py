"""
path: modules/mod/keyword_filter/__init__.py
purpose: Filters messages containing configured keywords and takes appropriate actions
critical:
- Maintains a list of filtered keywords and actions
- Supports notification on filter matches
- Handles message deletion and user warnings
"""

import os
import re
import json
import logging
import discord
from discord import app_commands
from typing import Optional, Dict, List
from .. import require_mod_role

logger = logging.getLogger('discord_bot.mod.keyword_filter')

# Configuration
FILTER_CONFIG = {
    "enabled": True,
    "notification_channel_id": None,
    "keywords": {},  # keyword -> {action: str, notify: bool, warn: bool}
    "monitor_channel_ids": [],  # Empty list means all channels
    "blacklist_channel_ids": []
}

def load_config():
    """Load filter configuration from file."""
    try:
        config_path = os.path.join("data", "keyword_filter", "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                FILTER_CONFIG.update(config)
                logger.info("Loaded keyword filter configuration")
    except Exception as e:
        logger.error(f"Error loading keyword filter config: {e}")

def save_config():
    """Save filter configuration to file."""
    try:
        config_path = os.path.join("data", "keyword_filter", "config.json")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(FILTER_CONFIG, f, indent=2)
            logger.info("Saved keyword filter configuration")
    except Exception as e:
        logger.error(f"Error saving keyword filter config: {e}")

async def setup(bot):
    """Set up the keyword filter module."""
    # Load configuration
    load_config()
    
    # Register keyword command group
    keyword_group = app_commands.Group(name="keyword", description="Configure keyword filtering")
    
    @keyword_group.command(name="add")
    @app_commands.describe(
        keyword="Keyword to filter",
        action="Action to take when keyword is found",
        notify="Whether to send notifications",
        warn="Whether to warn the user"
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Delete message", value="delete"),
            app_commands.Choice(name="Log only", value="log")
        ]
    )
    @require_mod_role()
    async def keyword_add(
        interaction: discord.Interaction,
        keyword: str,
        action: str,
        notify: bool = True,
        warn: bool = False
    ):
        """Add a keyword filter."""
        # Add keyword to config
        FILTER_CONFIG["keywords"][keyword] = {
            "action": action,
            "notify": notify,
            "warn": warn
        }
        
        save_config()
        await interaction.response.send_message(
            f"Added keyword filter for `{keyword}` with action: {action}",
            ephemeral=True
        )
        
    @keyword_group.command(name="remove")
    @app_commands.describe(
        keyword="Keyword to remove"
    )
    @require_mod_role()
    async def keyword_remove(
        interaction: discord.Interaction,
        keyword: str
    ):
        """Remove a keyword filter."""
        if keyword in FILTER_CONFIG["keywords"]:
            del FILTER_CONFIG["keywords"][keyword]
            save_config()
            await interaction.response.send_message(
                f"Removed keyword filter for `{keyword}`",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"No filter found for keyword `{keyword}`",
                ephemeral=True
            )
            
    @keyword_group.command(name="list")
    @require_mod_role()
    async def keyword_list(interaction: discord.Interaction):
        """List all keyword filters."""
        if not FILTER_CONFIG["keywords"]:
            await interaction.response.send_message(
                "No keyword filters configured.",
                ephemeral=True
            )
            return
            
        embed = discord.Embed(
            title="Keyword Filters",
            color=int(os.getenv('EMBED_COLOR', '000000'), 16)
        )
        
        for keyword, config in FILTER_CONFIG["keywords"].items():
            value = [
                f"Action: {config['action']}",
                f"Notify: {'Yes' if config['notify'] else 'No'}",
                f"Warn: {'Yes' if config['warn'] else 'No'}"
            ]
            embed.add_field(
                name=f"`{keyword}`",
                value="\n".join(value),
                inline=False
            )
            
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    @keyword_group.command(name="test")
    @app_commands.describe(
        text="Text to test against filters"
    )
    @require_mod_role()
    async def keyword_test(
        interaction: discord.Interaction,
        text: str
    ):
        """Test text against keyword filters."""
        matches = []
        for keyword, config in FILTER_CONFIG["keywords"].items():
            if re.search(rf"\b{re.escape(keyword)}\b", text, re.IGNORECASE):
                matches.append({
                    "keyword": keyword,
                    "config": config
                })
                
        if matches:
            embed = discord.Embed(
                title="Filter Test Results",
                description=f"Text: ```{text}```",
                color=int(os.getenv('EMBED_COLOR', '000000'), 16)
            )
            
            for match in matches:
                config = match["config"]
                value = [
                    f"Action: {config['action']}",
                    f"Notify: {'Yes' if config['notify'] else 'No'}",
                    f"Warn: {'Yes' if config['warn'] else 'No'}"
                ]
                embed.add_field(
                    name=f"`{match['keyword']}`",
                    value="\n".join(value),
                    inline=False
                )
                
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(
                "No filters matched the text.",
                ephemeral=True
            )
            
    @keyword_group.command(name="channel")
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
    async def keyword_channel(
        interaction: discord.Interaction,
        action: str,
        type: str,
        channel: discord.TextChannel
    ):
        """Configure channel settings."""
        config_key = f"{type}_channel_ids"
        channel_id = channel.id
        
        if action == "add":
            if channel_id not in FILTER_CONFIG[config_key]:
                FILTER_CONFIG[config_key].append(channel_id)
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
            if channel_id in FILTER_CONFIG[config_key]:
                FILTER_CONFIG[config_key].remove(channel_id)
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
                
    # Add the keyword command group to the bot
    bot.tree.add_command(keyword_group)
    logger.info("Registered keyword filter commands")
    
    # Register message handler
    @bot.event
    async def on_message(message):
        # Skip bot messages
        if message.author.bot:
            return
            
        # Skip if not enabled
        if not FILTER_CONFIG["enabled"]:
            return
            
        # Skip if channel is blacklisted
        if message.channel.id in FILTER_CONFIG["blacklist_channel_ids"]:
            return
            
        # Skip if monitoring specific channels and this isn't one of them
        if FILTER_CONFIG["monitor_channel_ids"] and message.channel.id not in FILTER_CONFIG["monitor_channel_ids"]:
            return
            
        # Check message against filters
        matches = []
        for keyword, config in FILTER_CONFIG["keywords"].items():
            if re.search(rf"\b{re.escape(keyword)}\b", message.content, re.IGNORECASE):
                matches.append({
                    "keyword": keyword,
                    "config": config
                })
                
        if matches:
            try:
                # Create notification embed
                embed = discord.Embed(
                    title="Keyword Filter Match",
                    description=message.content,
                    timestamp=message.created_at,
                    color=int(os.getenv('EMBED_COLOR', '000000'), 16)
                )
                
                embed.set_author(
                    name=message.author.display_name,
                    icon_url=message.author.display_avatar.url
                )
                
                # Add matched keywords
                keywords = []
                for match in matches:
                    config = match["config"]
                    keywords.append(
                        f"`{match['keyword']}` "
                        f"(Action: {config['action']}, "
                        f"Notify: {'Yes' if config['notify'] else 'No'}, "
                        f"Warn: {'Yes' if config['warn'] else 'No'})"
                    )
                    
                embed.add_field(
                    name="Matched Keywords",
                    value="\n".join(keywords),
                    inline=False
                )
                
                embed.add_field(
                    name="Source",
                    value=f"[Jump to message]({message.jump_url})"
                )
                
                # Send notification if configured
                if FILTER_CONFIG["notification_channel_id"]:
                    channel = bot.get_channel(FILTER_CONFIG["notification_channel_id"])
                    if channel:
                        await channel.send(embed=embed)
                        
                # Process actions
                for match in matches:
                    config = match["config"]
                    
                    # Delete message if configured
                    if config["action"] == "delete":
                        try:
                            await message.delete()
                            logger.info(f"Deleted message {message.id} containing keyword '{match['keyword']}'")
                        except Exception as e:
                            logger.error(f"Error deleting message: {e}")
                            
                    # Warn user if configured
                    if config["warn"]:
                        try:
                            warning = (
                                f"Your message was flagged for containing the keyword: `{match['keyword']}`\n"
                                f"Please review our guidelines regarding appropriate language."
                            )
                            await message.author.send(warning)
                            logger.info(f"Sent warning to user {message.author.id}")
                        except Exception as e:
                            logger.error(f"Error sending warning: {e}")
                            
            except Exception as e:
                logger.error(f"Error processing keyword filter match: {e}")
                
async def teardown(bot):
    """Clean up the keyword filter module."""
    # Save configuration
    save_config()
    logger.info("Saved keyword filter configuration") 