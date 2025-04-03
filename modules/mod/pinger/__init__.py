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
from .. import require_mod_role, require_pinger_user_role
import io
import asyncio
import time
import random

logger = logging.getLogger('discord_bot.mod.pinger')

# Configuration
PINGER_CONFIG = {
    "enabled": True,
    "monitor_channel_ids": [],  # Empty list means all channels
    "blacklist_channel_ids": [],
    "user_keywords": {},  # user_id -> {keywords: List[str], channels: List[int]}
    "notification_channel_id": None
}

# Track processed message IDs to prevent duplicates
# Format: { message_id: { "users": [user_ids], "rules": [rule_indices] } }
processed_messages = {}

# Track recently forwarded keywords by channel to prevent spam
# Format: { channel_id: { keyword: timestamp } }
recent_forwards = {}

# Track recently notified users by keyword to prevent spam
# Format: { user_id: { keyword: timestamp } }
recent_notifications = {}

# Throttle duration in seconds
THROTTLE_DURATION = 60

# Clean out old messages periodically
def clean_processed_messages():
    """Remove old messages from the tracking dictionary to prevent memory growth."""
    current_time = time.time()
    cutoff_time = current_time - 3600  # Remove messages older than 1 hour
    throttle_cutoff = current_time - THROTTLE_DURATION  # Remove throttled items older than throttle duration
    
    # Clean processed messages
    to_remove = []
    for message_id, data in processed_messages.items():
        if data.get("timestamp", current_time) < cutoff_time:
            to_remove.append(message_id)
            
    for message_id in to_remove:
        del processed_messages[message_id]
        
    if to_remove:
        logger.debug(f"Cleaned {len(to_remove)} old messages from tracking")
    
    # Clean recent forwards
    forward_channels_to_clean = []
    keywords_to_clean = {}
    
    for channel_id, keywords in recent_forwards.items():
        keyword_to_remove = []
        for keyword, timestamp in keywords.items():
            if timestamp < throttle_cutoff:
                keyword_to_remove.append(keyword)
        
        if keyword_to_remove:
            keywords_to_clean[channel_id] = keyword_to_remove
            
        if len(keyword_to_remove) == len(keywords):
            forward_channels_to_clean.append(channel_id)
    
    # Remove old keywords
    for channel_id, keywords in keywords_to_clean.items():
        for keyword in keywords:
            del recent_forwards[channel_id][keyword]
    
    # Remove empty channels
    for channel_id in forward_channels_to_clean:
        del recent_forwards[channel_id]
    
    # Clean recent notifications
    users_to_clean = []
    notifications_to_clean = {}
    
    for user_id, keywords in recent_notifications.items():
        keyword_to_remove = []
        for keyword, timestamp in keywords.items():
            if timestamp < throttle_cutoff:
                keyword_to_remove.append(keyword)
        
        if keyword_to_remove:
            notifications_to_clean[user_id] = keyword_to_remove
            
        if len(keyword_to_remove) == len(keywords):
            users_to_clean.append(user_id)
    
    # Remove old keywords
    for user_id, keywords in notifications_to_clean.items():
        for keyword in keywords:
            del recent_notifications[user_id][keyword]
    
    # Remove empty users
    for user_id in users_to_clean:
        del recent_notifications[user_id]

# Schedule the cleanup to run periodically
async def schedule_cleanup():
    """Schedule periodic cleanup of processed messages."""
    while True:
        await asyncio.sleep(1800)  # Run every 30 minutes
        clean_processed_messages()

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
    
    # Start the cleanup task for processed messages
    bot.loop.create_task(schedule_cleanup())
    
    # Helper function to check if user has the keyword access role
    async def has_keyword_role(interaction: discord.Interaction) -> bool:
        """Check if user has the keyword access role."""
        if not interaction.guild:
            return False
            
        if not isinstance(interaction.user, discord.Member):
            return False
            
        role_ids_str = os.getenv('PINGER_USER_ROLE_ID')
        if not role_ids_str:
            return False
            
        try:
            # Split the comma-separated role IDs and convert each to int
            role_ids = [int(role_id.strip()) for role_id in role_ids_str.split(',') if role_id.strip()]
            return any(role.id in role_ids for role in interaction.user.roles)
        except:
            return False
    
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
        """Add keywords for a user to be notified about."""
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
        try:
            # Defer the response immediately to prevent timeout
            await interaction.response.defer(ephemeral=True)
            
            if user:
                # List keywords for specific user
                if str(user.id) not in PINGER_CONFIG["user_keywords"]:
                    await interaction.followup.send(
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
                    
                await interaction.followup.send(embed=embed, ephemeral=True)
                
            else:
                # List all users
                if not PINGER_CONFIG["user_keywords"]:
                    await interaction.followup.send(
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
                    except Exception as e:
                        logger.debug(f"Error fetching member {user_id}: {e}")
                        continue
                    
                await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in pinger_list command: {e}")
            # Use followup since we already deferred
            await interaction.followup.send(
                "An error occurred while listing keywords.",
                ephemeral=True
            )
    
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
    
    # Register user keyword command group with role-based access
    keywords_group = app_commands.Group(name="keywords", description="Manage your notification keywords")
    
    # Custom check for keywords command access
    def keyword_access():
        """Check if user has access to keyword commands."""
        async def predicate(interaction: discord.Interaction) -> bool:
            has_access = await has_keyword_role(interaction)
            if not has_access:
                role_id = os.getenv('PINGER_USER_ROLE_ID')
                role_mention = f"<@&{role_id}>" if role_id else "required role"
                # Instead of responding directly, raise a custom exception
                # that can be properly handled by the error handler
                raise KeywordAccessError(f"You need the {role_mention} role to use keyword commands.")
            return has_access
        return app_commands.check(predicate)
        
    # Custom exception for keyword access checks
    class KeywordAccessError(app_commands.errors.CheckFailure):
        """Raised when a user doesn't have access to keyword commands."""
        pass
    
    # Helper function for safe responses
    async def safe_respond(interaction, message, ephemeral=True):
        """Send a response safely, handling already-responded interactions."""
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(message, ephemeral=ephemeral)
            else:
                try:
                    await interaction.followup.send(message, ephemeral=ephemeral)
                except Exception as e:
                    logger.error(f"Error sending followup: {e}")
        except Exception as e:
            logger.error(f"Error in safe_respond: {e}")
        
    # Error handler for keyword commands
    @keywords_group.error
    async def on_keywords_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Handle errors for keyword commands."""
        if isinstance(error, KeywordAccessError):
            # Only respond if the interaction hasn't been responded to yet
            await safe_respond(interaction, str(error), ephemeral=True)
            return True
        
        # For other errors, log them
        logger.error(f"Error in keywords command: {error}")
        await safe_respond(interaction, "An error occurred while processing your command.", ephemeral=True)
        return False
    
    @keywords_group.command(name="list")
    @require_pinger_user_role()
    async def keywords_list(interaction: discord.Interaction):
        """List your personal notification keywords."""
        try:
            user_id = str(interaction.user.id)
            
            if user_id not in PINGER_CONFIG["user_keywords"] or not PINGER_CONFIG["user_keywords"][user_id]["keywords"]:
                await interaction.response.send_message(
                    "You don't have any keywords configured.",
                    ephemeral=True
                )
                return
            
            user_config = PINGER_CONFIG["user_keywords"][user_id]
            embed = discord.Embed(
                title="Your Notification Keywords",
                description="You'll be notified when these keywords are mentioned.",
                color=int(os.getenv('EMBED_COLOR', '000000'), 16)
            )
            
            embed.add_field(
                name="Keywords",
                value=", ".join(f"`{k}`" for k in user_config["keywords"]),
                inline=False
            )
            
            if user_config["channels"]:
                channels = [f"<#{c}>" for c in user_config["channels"]]
                embed.add_field(
                    name="Channel Whitelist",
                    value="You'll only be notified when these keywords appear in these channels: " + ", ".join(channels),
                    inline=False
                )
            else:
                embed.add_field(
                    name="Channel Whitelist",
                    value="You'll be notified from all monitored channels.",
                    inline=False
                )
                
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in keywords_list command: {e}")
            await safe_respond(interaction, "An error occurred while listing your keywords.", ephemeral=True)
    
    @keywords_group.command(name="add")
    @require_pinger_user_role()
    @app_commands.describe(keywords="Comma-separated list of keywords to add")
    async def keywords_add(interaction: discord.Interaction, keywords: str):
        """Add keywords to your personal notification list."""
        try:
            user_id = str(interaction.user.id)
            
            # Initialize user config if needed
            if user_id not in PINGER_CONFIG["user_keywords"]:
                PINGER_CONFIG["user_keywords"][user_id] = {
                    "keywords": [],
                    "channels": []
                }
            
            # Add new keywords
            new_keywords = [k.strip() for k in keywords.split(",")]
            user_config = PINGER_CONFIG["user_keywords"][user_id]
            added = []
            
            for keyword in new_keywords:
                if keyword and keyword not in user_config["keywords"]:
                    user_config["keywords"].append(keyword)
                    added.append(keyword)
                    
            if added:
                save_config()
                await interaction.response.send_message(
                    f"Added keywords: {', '.join(f'`{k}`' for k in added)}",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "No new keywords were added.",
                    ephemeral=True
                )
        except Exception as e:
            logger.error(f"Error in keywords_add command: {e}")
            await safe_respond(interaction, "An error occurred while adding your keywords.", ephemeral=True)
    
    @keywords_group.command(name="remove")
    @require_pinger_user_role()
    @app_commands.describe(keywords="Comma-separated list of keywords to remove")
    async def keywords_remove(interaction: discord.Interaction, keywords: str):
        """Remove keywords from your personal notification list."""
        try:
            user_id = str(interaction.user.id)
            
            if user_id not in PINGER_CONFIG["user_keywords"]:
                await interaction.response.send_message(
                    "You don't have any keywords configured.",
                    ephemeral=True
                )
                return
            
            # Remove keywords
            remove_keywords = [k.strip() for k in keywords.split(",")]
            user_config = PINGER_CONFIG["user_keywords"][user_id]
            removed = []
            
            for keyword in remove_keywords:
                if keyword in user_config["keywords"]:
                    user_config["keywords"].remove(keyword)
                    removed.append(keyword)
                    
            if removed:
                save_config()
                await interaction.response.send_message(
                    f"Removed keywords: {', '.join(f'`{k}`' for k in removed)}",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "No keywords were removed.",
                    ephemeral=True
                )
        except Exception as e:
            logger.error(f"Error in keywords_remove command: {e}")
            await safe_respond(interaction, "An error occurred while removing your keywords.", ephemeral=True)
    
    @keywords_group.command(name="channels")
    @require_pinger_user_role()
    async def keywords_channels(interaction: discord.Interaction, channels: str):
        """Set channel whitelist for your keywords."""
        try:
            user_id = str(interaction.user.id)
            
            if user_id not in PINGER_CONFIG["user_keywords"]:
                await interaction.response.send_message(
                    "You don't have any keyword settings configured.",
                    ephemeral=True
                )
                return
            
            user_config = PINGER_CONFIG["user_keywords"][user_id]
            embed = discord.Embed(
                title="Your Keyword Channel Settings",
                color=int(os.getenv('EMBED_COLOR', '000000'), 16)
            )
            
            if user_config["channels"]:
                channels = [f"<#{c}>" for c in user_config["channels"]]
                embed.add_field(
                    name="Active Channels",
                    value="Your keywords will only be monitored in these channels:\n" + ", ".join(channels),
                    inline=False
                )
                embed.description = "You have specific channels whitelisted."
            else:
                embed.description = "You're receiving notifications from all monitored channels."
                embed.add_field(
                    name="No Channel Restrictions",
                    value="Your keywords are being monitored in all channels.",
                    inline=False
                )
                
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in keywords_channels command: {e}")
            await safe_respond(interaction, "An error occurred while listing your channel settings.", ephemeral=True)
                    
    @keywords_group.command(name="add_channel")
    @require_pinger_user_role()
    @app_commands.describe(channel="The channel to add to your whitelist")
    async def keywords_add_channel(interaction: discord.Interaction, channel: discord.TextChannel):
        """Add a channel to your keyword whitelist."""
        try:
            user_id = str(interaction.user.id)
            
            # Initialize user config if needed
            if user_id not in PINGER_CONFIG["user_keywords"]:
                PINGER_CONFIG["user_keywords"][user_id] = {
                    "keywords": [],
                    "channels": []
                }
            
            user_config = PINGER_CONFIG["user_keywords"][user_id]
            
            if channel.id in user_config["channels"]:
                await interaction.response.send_message(
                    f"{channel.mention} is already in your whitelist.",
                    ephemeral=True
                )
                return
                
            # Add channel to whitelist
            user_config["channels"].append(channel.id)
            save_config()
            
            await interaction.response.send_message(
                f"Added {channel.mention} to your keyword channel whitelist.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in keywords_add_channel command: {e}")
            await safe_respond(interaction, "An error occurred while adding the channel.", ephemeral=True)
                    
    @keywords_group.command(name="remove_channel")
    @require_pinger_user_role()
    @app_commands.describe(channel="The channel to remove from your whitelist")
    async def keywords_remove_channel(interaction: discord.Interaction, channel: discord.TextChannel):
        """Remove a channel from your keyword whitelist."""
        try:
            user_id = str(interaction.user.id)
            
            if user_id not in PINGER_CONFIG["user_keywords"] or not PINGER_CONFIG["user_keywords"][user_id]["channels"]:
                await interaction.response.send_message(
                    "You don't have any channels in your whitelist.",
                    ephemeral=True
                )
                return
                
            user_config = PINGER_CONFIG["user_keywords"][user_id]
            
            if channel.id not in user_config["channels"]:
                await interaction.response.send_message(
                    f"{channel.mention} is not in your whitelist.",
                    ephemeral=True
                )
                return
                
            # Remove channel from whitelist
            user_config["channels"].remove(channel.id)
            save_config()
            
            await interaction.response.send_message(
                f"Removed {channel.mention} from your keyword channel whitelist.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in keywords_remove_channel command: {e}")
            await safe_respond(interaction, "An error occurred while removing the channel.", ephemeral=True)
                    
    @keywords_group.command(name="clear_channels")
    @require_pinger_user_role()
    async def keywords_clear_channels(interaction: discord.Interaction):
        """Clear your channel whitelist to listen in all channels."""
        try:
            user_id = str(interaction.user.id)
            
            if user_id not in PINGER_CONFIG["user_keywords"]:
                PINGER_CONFIG["user_keywords"][user_id] = {
                    "keywords": [],
                    "channels": []
                }
                
            user_config = PINGER_CONFIG["user_keywords"][user_id]
            
            if not user_config["channels"]:
                await interaction.response.send_message(
                    "You don't have any channels in your whitelist.",
                    ephemeral=True
                )
                return
                
            # Clear the channel whitelist
            user_config["channels"] = []
            save_config()
            
            await interaction.response.send_message(
                "Cleared your channel whitelist. Your keywords will now be monitored in all channels.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in keywords_clear_channels command: {e}")
            await safe_respond(interaction, "An error occurred while clearing your channel whitelist.", ephemeral=True)
    
    # Add keywords command group to bot
    bot.tree.add_command(keywords_group)
    logger.info("Registered role-based keyword commands")
    
    # Create forward rules command group
    forward_group = app_commands.Group(name="forward", description="Configure keyword forwarding rules")
    
    # Add a structure for forwarding rules
    if "forwarding_rules" not in PINGER_CONFIG:
        PINGER_CONFIG["forwarding_rules"] = []
        save_config()
    
    @forward_group.command(name="add_channel_rule")
    @app_commands.describe(
        channels="Comma-separated list of channel IDs to monitor",
        keyword="Keyword to match (use quotes for phrases)",
        target_channel="Channel ID where matches will be forwarded"
    )
    @require_mod_role()
    async def forward_add_channel_rule(
        interaction: discord.Interaction,
        channels: str,
        keyword: str,
        target_channel: str
    ):
        """Add a forwarding rule for specific channels."""
        try:
            # Parse channel IDs
            channel_ids = []
            for channel_id in channels.split(','):
                try:
                    channel_ids.append(int(channel_id.strip()))
                except ValueError:
                    continue
            
            if not channel_ids:
                await interaction.response.send_message(
                    "❌ No valid channel IDs provided.",
                    ephemeral=True
                )
                return
            
            # Validate target channel
            try:
                target_id = int(target_channel.strip())
                # Check if target channel exists
                if not interaction.guild.get_channel(target_id):
                    await interaction.response.send_message(
                        "❌ Target channel not found.",
                        ephemeral=True
                    )
                    return
            except ValueError:
                await interaction.response.send_message(
                    "❌ Invalid target channel ID.",
                    ephemeral=True
                )
                return
            
            # Check if the same rule already exists
            for rule in PINGER_CONFIG["forwarding_rules"]:
                if (rule.get("type") == "channels" and 
                    rule.get("keyword") == keyword and
                    set(rule.get("channel_ids", [])) == set(channel_ids) and
                    rule.get("target_channel") == target_id):
                    await interaction.response.send_message(
                        "❌ This rule already exists.",
                        ephemeral=True
                    )
                    return
            
            # Create the rule
            rule = {
                "type": "channels",
                "keyword": keyword,
                "channel_ids": channel_ids,
                "target_channel": target_id
            }
            
            # Add rule to configuration
            PINGER_CONFIG["forwarding_rules"].append(rule)
            save_config()
            
            # Create response embed
            embed = discord.Embed(
                title="✅ Forwarding Rule Added",
                description=f"Messages containing `{keyword}` will be forwarded.",
                color=int(os.getenv('EMBED_COLOR', '000000'), 16)
            )
            
            # Add rule details
            channel_mentions = [f"<#{c_id}>" for c_id in channel_ids]
            embed.add_field(
                name="Monitored Channels",
                value=", ".join(channel_mentions) if channel_mentions else "None",
                inline=False
            )
            
            embed.add_field(
                name="Target Channel",
                value=f"<#{target_id}>",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error adding forwarding rule: {e}")
            await safe_respond(interaction, f"❌ Error adding rule: {str(e)}", ephemeral=True)
    
    @forward_group.command(name="add_category_rule")
    @app_commands.describe(
        category="Category ID to monitor",
        keyword="Keyword to match (use quotes for phrases)",
        target_channel="Channel ID where matches will be forwarded",
        blacklist_channels="Optional: Comma-separated list of channel IDs to exclude",
        blacklist_rooms="Optional: Comma-separated list of room IDs within the category to exclude"
    )
    @require_mod_role()
    async def forward_add_category_rule(
        interaction: discord.Interaction,
        category: str,
        keyword: str,
        target_channel: str,
        blacklist_channels: Optional[str] = None,
        blacklist_rooms: Optional[str] = None
    ):
        """Add a forwarding rule for an entire category with optional blacklisted channels and rooms."""
        try:
            # Parse category ID
            try:
                category_id = int(category.strip())
                # Check if category exists
                if not interaction.guild.get_channel(category_id):
                    await interaction.response.send_message(
                        "❌ Category not found.",
                        ephemeral=True
                    )
                    return
            except ValueError:
                await interaction.response.send_message(
                    "❌ Invalid category ID.",
                    ephemeral=True
                )
                return
            
            # Parse blacklisted channels
            blacklist_ids = []
            if blacklist_channels:
                for channel_id in blacklist_channels.split(','):
                    try:
                        blacklist_ids.append(int(channel_id.strip()))
                    except ValueError:
                        continue
                        
            # Parse blacklisted rooms
            blacklist_room_ids = []
            if blacklist_rooms:
                for room_id in blacklist_rooms.split(','):
                    try:
                        blacklist_room_ids.append(int(room_id.strip()))
                    except ValueError:
                        continue
            
            # Validate target channel
            try:
                target_id = int(target_channel.strip())
                # Check if target channel exists
                if not interaction.guild.get_channel(target_id):
                    await interaction.response.send_message(
                        "❌ Target channel not found.",
                        ephemeral=True
                    )
                    return
            except ValueError:
                await interaction.response.send_message(
                    "❌ Invalid target channel ID.",
                    ephemeral=True
                )
                return
            
            # Check if the same rule already exists
            for rule in PINGER_CONFIG["forwarding_rules"]:
                if (rule.get("type") == "category" and 
                    rule.get("keyword") == keyword and
                    rule.get("category_id") == category_id and
                    rule.get("target_channel") == target_id and
                    set(rule.get("blacklist_ids", [])) == set(blacklist_ids) and
                    set(rule.get("blacklist_room_ids", [])) == set(blacklist_room_ids)):
                    await interaction.response.send_message(
                        "❌ This rule already exists.",
                        ephemeral=True
                    )
                    return
            
            # Create the rule
            rule = {
                "type": "category",
                "keyword": keyword,
                "category_id": category_id,
                "blacklist_ids": blacklist_ids,
                "blacklist_room_ids": blacklist_room_ids,
                "target_channel": target_id
            }
            
            # Add rule to configuration
            PINGER_CONFIG["forwarding_rules"].append(rule)
            save_config()
            
            # Create response embed
            embed = discord.Embed(
                title="✅ Category Forwarding Rule Added",
                description=f"Messages containing `{keyword}` will be forwarded.",
                color=int(os.getenv('EMBED_COLOR', '000000'), 16)
            )
            
            # Add rule details
            embed.add_field(
                name="Monitored Category",
                value=f"<#{category_id}>",
                inline=False
            )
            
            if blacklist_ids:
                blacklist_mentions = [f"<#{c_id}>" for c_id in blacklist_ids]
                embed.add_field(
                    name="Excluded Channels",
                    value=", ".join(blacklist_mentions),
                    inline=False
                )
                
            if blacklist_room_ids:
                room_mentions = [f"<#{r_id}>" for r_id in blacklist_room_ids]
                embed.add_field(
                    name="Excluded Rooms",
                    value=", ".join(room_mentions),
                    inline=False
                )
            
            embed.add_field(
                name="Target Channel",
                value=f"<#{target_id}>",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error adding category forwarding rule: {e}")
            await safe_respond(interaction, f"❌ Error adding rule: {str(e)}", ephemeral=True)
    
    @forward_group.command(name="list")
    @require_mod_role()
    async def forward_list(interaction: discord.Interaction):
        """List all forwarding rules."""
        if not PINGER_CONFIG["forwarding_rules"]:
            await interaction.response.send_message(
                "No forwarding rules configured.",
                ephemeral=True
            )
            return
            
        # Create embed for rules
        embed = discord.Embed(
            title="Keyword Forwarding Rules",
            color=int(os.getenv('EMBED_COLOR', '000000'), 16)
        )
        
        # Add channel rules
        channel_rules = [r for r in PINGER_CONFIG["forwarding_rules"] if r.get("type") == "channels"]
        if channel_rules:
            for i, rule in enumerate(channel_rules):
                channels = [f"<#{c_id}>" for c_id in rule.get("channel_ids", [])]
                target = f"<#{rule.get('target_channel')}>"
                embed.add_field(
                    name=f"Channel Rule #{i+1}",
                    value=f"Keyword: `{rule.get('keyword')}`\nChannels: {', '.join(channels)}\nTarget: {target}",
                    inline=False
                )
        
        # Add category rules
        category_rules = [r for r in PINGER_CONFIG["forwarding_rules"] if r.get("type") == "category"]
        if category_rules:
            for i, rule in enumerate(category_rules):
                category = f"<#{rule.get('category_id')}>"
                target = f"<#{rule.get('target_channel')}>"
                blacklist = ""
                if rule.get("blacklist_ids"):
                    blacklist_mentions = [f"<#{c_id}>" for c_id in rule.get("blacklist_ids")]
                    blacklist = f"\nExcluded: {', '.join(blacklist_mentions)}"
                embed.add_field(
                    name=f"Category Rule #{i+1}",
                    value=f"Keyword: `{rule.get('keyword')}`\nCategory: {category}{blacklist}\nTarget: {target}",
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @forward_group.command(name="remove")
    @app_commands.describe(
        rule_number="The rule number to remove (use /forward list to see numbers)"
    )
    @require_mod_role()
    async def forward_remove(interaction: discord.Interaction, rule_number: int):
        """Remove a forwarding rule by its number."""
        if not PINGER_CONFIG["forwarding_rules"]:
            await interaction.response.send_message(
                "No forwarding rules configured.",
                ephemeral=True
            )
            return
            
        if rule_number <= 0 or rule_number > len(PINGER_CONFIG["forwarding_rules"]):
            await interaction.response.send_message(
                f"❌ Invalid rule number. Use /forward list to see available rules.",
                ephemeral=True
            )
            return
            
        # Get the rule and remove it
        rule = PINGER_CONFIG["forwarding_rules"].pop(rule_number - 1)
        save_config()
        
        # Create a response embed
        embed = discord.Embed(
            title="✅ Forwarding Rule Removed",
            description=f"Rule for keyword `{rule.get('keyword')}` has been removed.",
            color=int(os.getenv('EMBED_COLOR', '000000'), 16)
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Add forward command group to the bot
    bot.tree.add_command(forward_group)
    logger.info("Registered forwarding commands")
    
    # Modify message handler to include forwarding rules
    @bot.event
    async def on_message(message):
        # Skip if not enabled
        if not PINGER_CONFIG["enabled"]:
            return
            
        # Skip messages from the bot itself completely
        if message.author.id == bot.user.id:
            logger.debug(f"Skipping message from the bot itself: {message.id}")
            return
            
        # Skip if channel is blacklisted
        if message.channel.id in PINGER_CONFIG["blacklist_channel_ids"]:
            return
            
        # Skip if monitoring specific channels and this isn't one of them
        if PINGER_CONFIG["monitor_channel_ids"] and message.channel.id not in PINGER_CONFIG["monitor_channel_ids"]:
            return
            
        # Process forwarding rules
        if message.guild and PINGER_CONFIG.get("forwarding_rules"):
            await process_forwarding_rules(bot, message)

        # Continue with original code for @everyone and mentions
        monitor_everyone = os.getenv('PINGER_MONITOR_EVERYONE', 'True').lower() == 'true'
        monitor_here = os.getenv('PINGER_MONITOR_HERE', 'True').lower() == 'true'
        monitor_roles = os.getenv('PINGER_MONITOR_ROLES', 'True').lower() == 'true'
        
        # Get whitelist roles
        whitelist_role_ids = [int(id) for id in os.getenv('PINGER_WHITELIST_ROLE_IDS', '').split(',') if id]
        
        # Check if user has permission to mention everyone/here
        has_permission = False
        if whitelist_role_ids:
            # Check if author is a Member (has roles) and not a User or ClientUser
            if hasattr(message.author, 'roles'):
                member_roles = [role.id for role in message.author.roles]
                has_permission = any(role_id in whitelist_role_ids for role_id in member_roles)
            else:
                # Skip role check for non-member users (like the bot itself)
                logger.debug(f"Author {message.author} has no roles attribute, skipping role check")
        
        if has_permission:
            notification_channel_id = int(os.getenv('PINGER_NOTIFICATION_CHANNEL_ID', 0))
            if notification_channel_id:
                channel = bot.get_channel(notification_channel_id)
                if channel:
                    mentions = []
                    
                    # Check for @everyone
                    if monitor_everyone and message.mention_everyone:
                        mentions.append('@everyone')
                        
                    # Check for @here
                    if monitor_here and '@here' in message.content:
                        mentions.append('@here')
                        
                    # Check for role mentions
                    if monitor_roles and message.role_mentions:
                        mentions.extend([role.name for role in message.role_mentions])
                    
                    if mentions:
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
                            name="Important Mention",
                            value=", ".join(f"`{m}`" for m in mentions)
                        )
                        
                        # Create button for jumping to message
                        view = discord.ui.View()
                        view.add_item(
                            discord.ui.Button(
                                style=discord.ButtonStyle.link,
                                label="Jump to Message",
                                url=message.jump_url
                            )
                        )
                        
                        await channel.send(embed=embed, view=view)
            
        # Check message against user keywords
        for user_id, config in PINGER_CONFIG["user_keywords"].items():
            # Skip if not in a guild
            if not message.guild:
                continue
                
            # Skip if user has channel whitelist and this channel isn't in it
            if config["channels"] and message.channel.id not in config["channels"]:
                continue
                
            # Check if we've already processed this message for this user
            message_id_str = str(message.id)
            if message_id_str in processed_messages and user_id in processed_messages[message_id_str].get("users", []):
                logger.debug(f"Skipping already processed message {message.id} for user {user_id}")
                continue
                
            # Initialize tracking for this message if needed
            if message_id_str not in processed_messages:
                processed_messages[message_id_str] = {
                    "timestamp": time.time(),
                    "users": [],
                    "rules": [],
                    "retry_count": 0
                }
                
            # Initialize user notifications if needed
            if user_id not in recent_notifications:
                recent_notifications[user_id] = {}
                
            # Track if we already sent a notification to this user for this message
            notification_sent = False
                
            # Check each keyword
            for keyword in config["keywords"]:
                # Skip if we already notified this user about this message
                if notification_sent:
                    break
                    
                # Check message content for keyword
                match_found = re.search(rf"\b{re.escape(keyword)}\b", message.content, re.IGNORECASE)
                matched_content = message.content
                matched_location = "content"
                
                # If no match in content, check embeds
                if not match_found and message.embeds:
                    for embed_index, embed in enumerate(message.embeds):
                        # Check embed title
                        if embed.title and re.search(rf"\b{re.escape(keyword)}\b", embed.title, re.IGNORECASE):
                            match_found = True
                            matched_content = f"**{embed.title}**"
                            if embed.description:
                                matched_content += f"\n{embed.description}"
                            matched_location = f"embed.title ({embed_index})"
                            break
                            
                        # Check embed description
                        if embed.description and re.search(rf"\b{re.escape(keyword)}\b", embed.description, re.IGNORECASE):
                            match_found = True
                            if embed.title:
                                matched_content = f"**{embed.title}**\n{embed.description}"
                            else:
                                matched_content = embed.description
                            matched_location = f"embed.description ({embed_index})"
                            break
                            
                        # Check embed fields
                        for field_index, field in enumerate(embed.fields):
                            if (field.name and re.search(rf"\b{re.escape(keyword)}\b", field.name, re.IGNORECASE)) or \
                               (field.value and re.search(rf"\b{re.escape(keyword)}\b", field.value, re.IGNORECASE)):
                                match_found = True
                                if embed.title:
                                    matched_content = f"**{embed.title}**\n"
                                else:
                                    matched_content = ""
                                    
                                if embed.description:
                                    matched_content += f"{embed.description}\n"
                                    
                                matched_content += f"**{field.name}**: {field.value}"
                                matched_location = f"embed.field ({embed_index}.{field_index})"
                                break
                                
                        if match_found:
                            break
                
                if match_found:
                    try:
                        # Check if this keyword was recently notified for this user (throttling)
                        current_time = time.time()
                        if keyword in recent_notifications[user_id]:
                            last_notified = recent_notifications[user_id][keyword]
                            time_since_last = current_time - last_notified
                            
                            if time_since_last < THROTTLE_DURATION:
                                # Skip this notification - still in throttle period
                                logger.debug(f"Throttling notification for user {user_id}, keyword '{keyword}' - last sent {time_since_last:.1f}s ago")
                                continue
                        
                        # Mark that we've already sent a notification for this message to this user
                        notification_sent = True
                        # Record in our global tracking that this user was notified about this message
                        processed_messages[message_id_str]["users"].append(user_id)
                        # Record the time of this notification for throttling
                        recent_notifications[user_id][keyword] = current_time
                        
                        # Get the user to notify
                        try:
                            user = await message.guild.fetch_member(int(user_id))
                            if not user:
                                logger.warning(f"Could not find user with ID {user_id} in guild {message.guild.id}")
                                continue
                        except Exception as e:
                            logger.warning(f"Error fetching member {user_id}: {e}")
                            continue
                            
                        # Create notification embed
                        embed = discord.Embed(
                            title="Keyword Notification",
                            description=matched_content,
                            timestamp=message.created_at,
                            color=int(os.getenv('EMBED_COLOR', '000000'), 16)
                        )
                        
                        embed.set_author(
                            name=message.author.display_name,
                            icon_url=message.author.display_avatar.url
                        )
                        
                        # Add match information
                        embed.add_field(
                            name="Matched Keyword",
                            value=f"`{keyword}`",
                            inline=True
                        )
                        
                        # Add channel information
                        embed.add_field(
                            name="Channel",
                            value=f"<#{message.channel.id}>",
                            inline=True
                        )
                        
                        # Create button for jumping to message
                        view = discord.ui.View()
                        view.add_item(
                            discord.ui.Button(
                                style=discord.ButtonStyle.link,
                                label="Jump to Message",
                                url=message.jump_url
                            )
                        )
                        
                        # Send notification to channel or DM
                        try:
                            if PINGER_CONFIG["notification_channel_id"]:
                                channel = bot.get_channel(PINGER_CONFIG["notification_channel_id"])
                                if channel:
                                    await channel.send(content=user.mention, embed=embed, view=view)
                            else:
                                # Send DM to user
                                try:
                                    await user.send(embed=embed, view=view)
                                    logger.info(f"Sent keyword notification to {user.display_name} for keyword '{keyword}'")
                                    logger.debug(f"Throttling: User {user_id} with keyword '{keyword}' will be throttled for {THROTTLE_DURATION}s")
                                except discord.Forbidden:
                                    logger.warning(f"Cannot send DM to user {user_id} (DMs disabled)")
                                except discord.HTTPException as e:
                                    if e.status == 429:  # Rate limited
                                        logger.warning(f"Rate limited when sending DM to user {user_id}")
                                    else:
                                        logger.warning(f"Could not DM user {user_id}: {str(e)}")
                        except Exception as e:
                            logger.error(f"Error sending notification: {str(e)}")
                                
                    except Exception as e:
                        logger.error(f"Error sending notification: {str(e)}")
                        import traceback
                        logger.error(traceback.format_exc())

async def teardown(bot):
    """Clean up the pinger module."""
    # Save configuration
    save_config()
    logger.info("Saved pinger configuration")

async def process_forwarding_rules(bot, message):
    """Process forwarding rules for a message."""
    try:
        # Skip if no rules configured
        if not PINGER_CONFIG.get("forwarding_rules"):
            return
            
        # Get message ID for tracking
        message_id_str = str(message.id)
        
        # Initialize tracking for this message if not already done
        if message_id_str not in processed_messages:
            processed_messages[message_id_str] = {
                "timestamp": time.time(),
                "rules": set(),
                "forwards": 0
            }
            
        # Track number of forwards for this message
        processed_forwards = processed_messages[message_id_str].get("forwards", 0)
        max_forwards_per_message = 5  # Limit to prevent spam
        
        # Check each rule
        for rule_index, rule in enumerate(PINGER_CONFIG["forwarding_rules"]):
            # Stop if we've already processed too many rules for this message
            if processed_forwards >= max_forwards_per_message:
                logger.warning(f"Skipping remaining rules for message {message.id} - reached forward limit")
                break
                
            # Skip if we've already processed this rule for this message
            if rule_index in processed_messages[message_id_str].get("rules", []):
                logger.debug(f"Skipping already processed rule {rule_index} for message {message.id}")
                continue
                
            rule_type = rule.get("type")
            keyword = rule.get("keyword", "")
            
            # Skip if no keyword
            if not keyword:
                continue
                
            # Check if message is in scope for this rule
            in_scope = False
            
            if rule_type == "channels":
                # Check if message is in one of the rule's channels
                channel_ids = rule.get("channel_ids", [])
                if message.channel.id in channel_ids:
                    in_scope = True
                    
            elif rule_type == "category":
                # Check if message is in the rule's category
                category_id = rule.get("category_id")
                blacklist_ids = rule.get("blacklist_ids", [])
                blacklist_room_ids = rule.get("blacklist_room_ids", [])
                
                if (message.channel.category and 
                    message.channel.category.id == category_id and 
                    message.channel.id not in blacklist_ids and
                    message.channel.id not in blacklist_room_ids):
                    in_scope = True
            
            # Skip if not in scope
            if not in_scope:
                continue
                
            # Check keyword match in message content
            keyword_match = False
            
            # Check in message content
            if message.content and keyword.lower() in message.content.lower():
                keyword_match = True
                
            # Check in embeds if no match in content
            if not keyword_match and message.embeds:
                for embed in message.embeds:
                    # Check embed title
                    if embed.title and keyword.lower() in embed.title.lower():
                        keyword_match = True
                        break
                        
                    # Check embed description
                    if embed.description and keyword.lower() in embed.description.lower():
                        keyword_match = True
                        break
                        
                    # Check embed fields
                    for field in embed.fields:
                        if (field.name and keyword.lower() in field.name.lower()) or \
                           (field.value and keyword.lower() in field.value.lower()):
                            keyword_match = True
                            break
                            
                    if keyword_match:
                        break
            
            # Skip if no keyword match
            if not keyword_match:
                continue
                
            # Get target channel
            target_channel_id = rule.get("target_channel")
            if not target_channel_id:
                continue
                
            target_channel = bot.get_channel(target_channel_id)
            if not target_channel:
                logger.warning(f"Target channel {target_channel_id} not found for rule {rule_index}")
                continue
                
            # Create forward embed
            embed = discord.Embed(
                title="Forwarded Message",
                description=message.content if message.content else "No content",
                color=int(os.getenv('EMBED_COLOR', '000000'), 16)
            )
            
            # Add message link
            embed.add_field(
                name="Source",
                value=f"[Jump to Message]({message.jump_url})",
                inline=False
            )
            
            # Add author info if available
            if message.author:
                embed.set_author(
                    name=message.author.display_name,
                    icon_url=message.author.display_avatar.url if message.author.display_avatar else None
                )
                
            # Add channel info
            embed.add_field(
                name="Channel",
                value=f"<#{message.channel.id}>",
                inline=True
            )
            
            # Add matched keyword
            embed.add_field(
                name="Matched Keyword",
                value=f"`{keyword}`",
                inline=True
            )
            
            # Forward the message
            try:
                await target_channel.send(embed=embed)
                processed_forwards += 1
                processed_messages[message_id_str]["forwards"] = processed_forwards
                processed_messages[message_id_str]["rules"].add(rule_index)
                logger.info(f"Forwarded message {message.id} to channel {target_channel.name} (rule {rule_index})")
            except Exception as e:
                logger.error(f"Error forwarding message {message.id} to channel {target_channel.name}: {e}")
                
    except Exception as e:
        logger.error(f"Error processing forwarding rules: {e}")
        
    finally:
        # Clean up old messages periodically
        if random.random() < 0.1:  # 10% chance to clean on each message
            clean_processed_messages() 