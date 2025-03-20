"""
Command Sync

This module handles the synchronization of slash commands with the Discord API.
"""

import logging
import discord
import asyncio
from discord import app_commands
from config.core.settings import settings
from config.environment.environment import is_development
from config.features.moderation import filter as filter_config, mod as mod_config
from config.features.reactions import forward as forward_config, link as link_config
from config.features.pinger_config import pinger_config
from config.features.redeye_config import redeye as redeye_config
from config.features.embed_config import embed as embed_config
from modules.features.mod.link_reaction.remover import remove_pid_from_file

logger = logging.getLogger('discord_bot.command_sync')

# Constants for rate limit handling
RETRY_BUFFER = 10.0      # Buffer to add to rate limit times
MAX_RETRIES = 3          # Maximum number of retries

class CommandSync:
    """
    Handles the registration and synchronization of slash commands with Discord.
    """
    
    def __init__(self):
        """
        Initialize the command sync handler.
        """
        self.synced_commands = {}
    
    def sync_commands(self, bot, bot_name):
        """
        Sync commands for a bot instance.
        Only syncs commands globally and doesn't push guild-specific commands.
        
        Args:
            bot: The Discord bot instance
            bot_name (str): The name of the bot
        """
        # Log the commands registered in the bot's command tree
        @bot.event
        async def on_ready():
            try:
                logger.info(f"Started syncing commands for {bot_name}")
                
                # Log all commands in tree
                commands = bot.tree.get_commands()
                logger.info(f"Commands in tree for {bot_name}: {len(commands)}")
                for cmd in commands:
                    if isinstance(cmd, app_commands.ContextMenu):
                        logger.info(f"Context menu command: {cmd.name}, type: {cmd.type.name}")
                    else:
                        logger.info(f"Slash command: {cmd.name}")
                
                # For development environments, sync to specific guild IDs
                if is_development():
                    # Get guild IDs from environment variable
                    guild_ids = settings.GUILD_IDS
                    if guild_ids:
                        for guild_id in guild_ids:
                            guild = bot.get_guild(guild_id)
                            if guild:
                                logger.info(f"Syncing commands for guild: {guild.name} (ID: {guild_id})")
                                # This will sync all commands including context menu commands
                                bot.tree.copy_global_to(guild=discord.Object(id=guild_id))
                                await bot.tree.sync(guild=discord.Object(id=guild_id))
                                logger.info(f"Successfully synced commands to guild {guild.name}")
                            else:
                                logger.warning(f"Could not find guild with ID {guild_id}")
                
                # Always sync globally as well (needed for context menu commands too)
                logger.info("Syncing commands globally")
                await bot.tree.sync()
                logger.info("Successfully synced commands globally")
                
                # Store the synced commands
                self.synced_commands[bot_name] = bot.tree.get_commands()
                
                logger.info(f"Finished syncing commands for {bot_name}")
            except Exception as e:
                logger.error(f"Error syncing commands for {bot_name}: {e}")
                # Log detailed error information
                import traceback
                logger.error(f"Exception traceback: {traceback.format_exc()}")
                
    def register_command(self, bot, command_name, command_callback, description="No description provided", **kwargs):
        """
        Register a slash command with a bot.
        
        Args:
            bot: The Discord bot instance
            command_name (str): The name of the command
            command_callback (callable): The function to call when the command is invoked
            description (str, optional): The description of the command
            **kwargs: Additional arguments for the command
        """
        try:
            # Create the command
            @bot.tree.command(name=command_name, description=description, **kwargs)
            async def command(interaction: discord.Interaction, **params):
                return await command_callback(interaction, **params)
            
            logger.debug(f"Registered command: {command_name}")
            return True
        except Exception as e:
            logger.error(f"Error registering command {command_name}: {str(e)}")
            return False
            
    def register_module_commands(self, bot):
        """
        Register all module commands with the bot.
        This implements a single master command for each feature.
        
        Args:
            bot: The Discord bot instance
        """
        try:
            logger.info("Registering simplified module commands")
            from utils.permissions import mod_only
            
            # General status command - provides overview of all configurations
            @bot.tree.command(name="general", description="View bot status and configuration overview")
            @mod_only()
            async def general(interaction: discord.Interaction):
                """Show bot status and configuration for all modules"""
                
                # Get raw values directly from settings managers
                # Keyword Filter config values
                kf_enabled = filter_config.ENABLED
                kf_category_ids = filter_config.CATEGORY_IDS
                kf_blacklist_ids = filter_config.BLACKLIST_CHANNEL_IDS
                kf_filters = filter_config.FILTERS
                kf_whitelist_role_ids = mod_config.WHITELIST_ROLE_IDS
                
                # Reaction Forward config values
                rf_enabled = forward_config.ENABLED
                rf_category_ids = forward_config.CATEGORY_IDS
                rf_blacklist_ids = forward_config.BLACKLIST_CHANNEL_IDS
                rf_whitelist_role_ids = forward_config.WHITELIST_ROLE_IDS
                rf_destination_channel_id = forward_config.DESTINATION_CHANNEL_ID
                
                # Pinger config values
                pn_enabled = pinger_config.ENABLED
                pn_monitor_everyone = pinger_config.MONITOR_EVERYONE
                pn_monitor_here = pinger_config.MONITOR_HERE
                pn_monitor_roles = pinger_config.MONITOR_ROLES
                pn_notif_channel_id = pinger_config.NOTIFICATION_CHANNEL_ID
                pn_whitelist_role_ids = pinger_config.WHITELIST_ROLE_IDS
                
                # Get LuisaViaRoma settings
                stores = link_config.STORES
                luisaviaroma_store = None
                if isinstance(stores, dict):
                    for store_id, store in stores.items():
                        if store.get('name', '').lower() == 'luisaviaroma':
                            luisaviaroma_store = store
                            break
                
                # Create embed for better formatting
                embed = discord.Embed(
                    title="Bot Status & Configuration Overview",
                    description="Detailed configuration for all modules",
                )
                
                # Apply styling from embed_config
                embed = embed_config.apply_default_styling(embed)
                
                # Add bot status info
                embed.add_field(
                    name="🤖 Bot Status", 
                    value=f"**Online** | Latency: **{round(bot.latency * 1000)}ms**", 
                    inline=False
                )
                
                # Add Keyword Filter config as compact format
                kw_status = "✅ Active" if kf_enabled else "❌ Inactive"
                
                # Format active filters/rules info
                active_rules = []
                if isinstance(kf_filters, dict):
                    for rule_id, rule in kf_filters.items():
                        if isinstance(rule, dict) and rule.get('enabled', False):
                            active_rules.append(f"• **{rule.get('name', rule_id)}** ({len(rule.get('keywords', []))} keywords)")
                
                embed.add_field(
                    name="📝 Keyword Filter", 
                    value=f"**Status**: {kw_status}", 
                    inline=True
                )
                
                # Add monitored categories/channels count
                embed.add_field(
                    name="Monitored", 
                    value=f"Categories: **{len(kf_category_ids)}**\nChannels: **{len(kf_blacklist_ids)}** blacklisted", 
                    inline=True
                )
                
                # Add active rules count
                embed.add_field(
                    name="Active Rules", 
                    value=f"**{len(active_rules)}** rules configured\n`/keyword` to configure", 
                    inline=True
                )
                
                # Add Reaction Forward config in a compact format
                rf_status = "✅ Active" if rf_enabled else "❌ Inactive"
                
                # Format destination channel
                destination_channel = None
                if rf_destination_channel_id:
                    destination_channel = discord.utils.get(interaction.guild.channels, id=rf_destination_channel_id)
                
                embed.add_field(
                    name="↪️ Reaction Forward", 
                    value=f"**Status**: {rf_status}", 
                    inline=True
                )
                
                embed.add_field(
                    name="Monitored", 
                    value=f"Categories: **{len(rf_category_ids)}**\nChannels: **{len(rf_blacklist_ids)}** blacklisted", 
                    inline=True
                )
                
                embed.add_field(
                    name="Destination", 
                    value=f"{f'#{destination_channel.name}' if destination_channel else 'Not set'}\n`/reaction` to configure", 
                    inline=True
                )
                
                # Add Pinger config in a compact format
                pinger_status = "✅ Active" if pn_enabled else "❌ Inactive"
                
                # Format monitored mentions
                monitored = []
                if pn_monitor_everyone:
                    monitored.append("✅ @everyone")
                else:
                    monitored.append("❌ @everyone")
                
                if pn_monitor_here:
                    monitored.append("✅ @here")
                else:
                    monitored.append("❌ @here")
                
                if pn_monitor_roles:
                    monitored.append("✅ @roles")
                else:
                    monitored.append("❌ @roles")
                
                embed.add_field(
                    name="🔔 Pinger", 
                    value=f"**Status**: {pinger_status}", 
                    inline=True
                )
                
                embed.add_field(
                    name="Monitored Mentions", 
                    value="\n".join(monitored), 
                    inline=True
                )
                
                embed.add_field(
                    name="Notification Channel", 
                    value=f"{f'#{discord.utils.get(interaction.guild.channels, id=pn_notif_channel_id).name}' if pn_notif_channel_id else 'Not set'}\n`/pinger` to configure", 
                    inline=True
                )
                
                # Add LuisaViaRoma config if available
                if luisaviaroma_store:
                    lvr_status = "✅ Active" if luisaviaroma_store.get('enabled', False) else "❌ Inactive"
                    embed.add_field(
                        name="🛍️ LuisaViaRoma", 
                        value=f"**Status**: {lvr_status}\n`/reaction` to configure", 
                        inline=True
                    )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Register ping command
            @bot.tree.command(name="ping", description="Check if the bot is responsive")
            async def ping(interaction: discord.Interaction):
                await interaction.response.send_message(f"Pong! Bot is responsive. Latency: {round(bot.latency * 1000)}ms", ephemeral=True)
            
            # Keyword Filter Command - Simplified name
            @bot.tree.command(name="keyword", description="Set up keyword filtering")
            @mod_only()
            async def keyword(
                interaction: discord.Interaction,
                name: str = None,       # Rule name
                categories: str = None,  # Category IDs to monitor
                channels: str = None,    # Individual channel IDs to monitor
                alerts: str = None,      # Channel to send alerts to
                words: str = None,       # Keywords to monitor
                delete: bool = None,     # Whether to delete matched messages (replaces action)
                severity: str = None,    # Severity level (low, medium, high)
                rule_delete: str = None  # Name of rule to delete (renamed from delete)
            ):
                # Import configuration
                from config import filter_config
                from config import embed_config
                
                # Only allow administrators to use this command
                
                # Get settings directly from the settings manager
                settings = filter_config.ENABLED
                
                # Get current configuration values
                kf_enabled = settings.get("ENABLED", False)
                kf_dry_run = settings.get("DRY_RUN", True)
                kf_notification_channel_id = settings.get("NOTIFICATION_CHANNEL_ID")
                rules = settings.get("RULES", {})
                
                await interaction.response.defer(ephemeral=True)
                
                # Handle rule deletion (renamed parameter from delete to rule_delete)
                if rule_delete:
                    rule_id = rule_delete.lower().replace(" ", "_")
                    logger.debug(f"Attempting to delete rule with ID: {rule_id}")
                    logger.debug(f"Available rules: {list(rules.keys())}")
                    
                    if rule_id in rules:
                        del rules[rule_id]
                        settings.set("RULES", rules)
                        filter_config.ENABLED.save_settings()
                        logger.info(f"Rule {rule_id} deleted successfully")
                        await interaction.followup.send(f"✅ Keyword rule '{rule_delete}' deleted successfully!")
                        return
                    else:
                        # Look for case-insensitive match
                        for existing_rule_id in list(rules.keys()):
                            if existing_rule_id.lower() == rule_id.lower() or rules[existing_rule_id].get('name', '').lower() == rule_delete.lower():
                                logger.debug(f"Found rule with case-insensitive match: {existing_rule_id}")
                                del rules[existing_rule_id]
                                settings.set("RULES", rules)
                                filter_config.ENABLED.save_settings()
                                logger.info(f"Rule {existing_rule_id} deleted successfully")
                                await interaction.followup.send(f"✅ Keyword rule '{rule_delete}' deleted successfully!")
                                return
                        
                        logger.warning(f"Rule {rule_id} not found for deletion")
                        await interaction.followup.send(f"⚠️ Rule '{rule_delete}' not found. Available rules: {', '.join(rules.keys())}")
                        return
                
                # Show current configuration if no parameters provided
                if name is None and categories is None and channels is None and alerts is None and words is None and delete is None and severity is None:
                    # Create an embed to show current settings
                    embed = discord.Embed(
                        title="Keyword Filter Configuration",
                        description="Current keyword filtering rules",
                    )
                    
                    # Apply styling from embed_config
                    embed = embed_config.apply_default_styling(embed)
                    
                    # Status field
                    status_value = f"**{'Enabled' if kf_enabled else 'Disabled'}**\n"
                    status_value += f"Dry run mode: {'Yes (no actions taken)' if kf_dry_run else 'No (taking action)'}"
                    embed.add_field(name="Status", value=status_value, inline=False)
                    
                    # Rules field
                    rules_value = ""
                    
                    # First add example rule if it exists
                    if "example_rule" in rules:
                        example = rules["example_rule"]
                        rules_value += f"❌ **{example.get('name', 'Example Rule')}** (ID: `example_rule`)\n"
                        keywords = example.get('keywords', [])
                        rules_value += f"• Keywords: {', '.join([f'`{k}`' for k in keywords]) if keywords else 'None'}\n"
                        rules_value += f"• Action: {'Delete' if example.get('action') == 'delete' else 'Notify'} | Severity: {example.get('severity', 'Medium').capitalize()}\n"
                        rules_value += f"• Alerts to: {f'<#{example.get('alert_channel_id')}>' if example.get('alert_channel_id') else 'None'}\n"
                        rules_value += f"• Monitors: {len(example.get('category_ids', []))} categories, {len(example.get('channel_ids', []))} channels\n\n"
                    
                    # Then add all other active rules
                    for rule_id, rule in rules.items():
                        if rule_id == "example_rule":
                            continue
                            
                        enabled = rule.get('enabled', False)
                        rules_value += f"{'✅' if enabled else '❌'} **{rule.get('name', rule_id)}** (ID: `{rule_id}`)\n"
                        keywords = rule.get('keywords', [])
                        rules_value += f"• Keywords: {', '.join([f'`{k}`' for k in keywords[:3]]) + (f' +{len(keywords)-3} more' if len(keywords) > 3 else '') if keywords else 'None'}\n"
                        
                        # Updated to show Delete instead of action:delete
                        delete_messages = rule.get('action') == 'delete'
                        rules_value += f"• {'Deletes messages' if delete_messages else 'Notifies only'} | Severity: {rule.get('severity', 'Medium').capitalize()}\n"
                        
                        rules_value += f"• Alerts to: {f'<#{rule.get('alert_channel_id')}>' if rule.get('alert_channel_id') else 'None'}\n"
                        rules_value += f"• Monitors: {len(rule.get('category_ids', []))} categories, {len(rule.get('channel_ids', []))} channels\n\n"
                    
                    if not rules_value:
                        rules_value = "No rules configured yet."
                    
                    embed.add_field(name="Configured Rules", value=rules_value, inline=False)
                    
                    # How to configure field
                    help_value = "`/keyword name:rulename categories:123,456 channels:789,101112 alerts:131415 words:word1,word2,word3 delete:true`\n\n"
                    help_value += "To delete a rule: `/keyword rule_delete:rulename`"
                    embed.add_field(name="How to Configure", value=help_value, inline=False)
                    
                    # Add a note about the rule_delete parameter
                    embed.add_field(
                        name="⚠️ Important",
                        value="To delete a rule, use the `rule_delete` parameter, NOT the `delete` parameter.\n" +
                              "Example: `/keyword rule_delete:test2` will delete the rule named 'test2'.",
                        inline=False
                    )
                    
                    await interaction.followup.send(embed=embed)
                    return
                
                # Validate parameters for creating/updating a rule
                if name and words:
                    # Convert name to a rule ID (lowercase, spaces to underscores)
                    rule_id = name.lower().replace(" ", "_")
                    
                    # Process categories (comma-separated list of category IDs)
                    category_ids = []
                    if categories:
                        try:
                            category_ids = [int(cat.strip()) for cat in categories.split(',') if cat.strip().isdigit()]
                        except ValueError:
                            await interaction.followup.send("⚠️ Invalid category ID format. Please use comma-separated numbers.")
                            return
                    
                    # Process channels (comma-separated list of channel IDs)
                    channel_ids = []
                    if channels:
                        try:
                            channel_ids = [int(ch.strip()) for ch in channels.split(',') if ch.strip().isdigit()]
                        except ValueError:
                            await interaction.followup.send("⚠️ Invalid channel ID format. Please use comma-separated numbers.")
                            return
                    
                    # If neither categories nor channels specified, show error
                    if not category_ids and not channel_ids:
                        await interaction.followup.send("⚠️ You must specify at least one category or channel to monitor.")
                        return
                    
                    # Process alert channel
                    alert_channel_id = None
                    if alerts:
                        try:
                            alert_channel_id = int(alerts.strip())
                        except ValueError:
                            await interaction.followup.send("⚠️ Invalid alert channel ID format. Please use a number.")
                            return
                    else:
                        # Use default notification channel if available
                        alert_channel_id = kf_notification_channel_id
                    
                    # Process keywords (comma-separated list, but respect quotes for phrases)
                    keyword_list = []
                    if words:
                        # Split by commas, but preserve quoted strings
                        in_quotes = False
                        current_word = ""
                        for char in words:
                            if char == '"':
                                in_quotes = not in_quotes
                            elif char == ',' and not in_quotes:
                                if current_word:
                                    keyword_list.append(current_word.strip().strip('"'))
                                    current_word = ""
                            else:
                                current_word += char
                        # Add the last word if there is one
                        if current_word:
                            keyword_list.append(current_word.strip().strip('"'))
                    
                    if not keyword_list:
                        await interaction.followup.send("⚠️ You must provide at least one keyword to monitor.")
                        return
                    
                    # Process severity
                    if severity and severity.lower() not in ['low', 'medium', 'high']:
                        await interaction.followup.send("⚠️ Invalid severity. Please use 'low', 'medium', or 'high'.")
                        return
                    
                    # Set default severity if not provided
                    if not severity:
                        severity = 'medium'
                    
                    # Create or update the rule
                    rule = {
                        'enabled': True,
                        'name': name,
                        'description': f"Rule created by {interaction.user}",
                        'category_ids': category_ids,
                        'channel_ids': channel_ids,
                        'blacklist_ids': [],
                        'alert_channel_id': alert_channel_id,
                        'severity': severity.lower(),
                        'action': 'delete' if delete else 'notify',  # Convert delete boolean to action string
                        'keywords': keyword_list
                    }
                    
                    # Add/update the rule in the configuration
                    rules[rule_id] = rule
                    settings.set("RULES", rules)
                    
                    # Enable the configuration if it's disabled
                    if not kf_enabled:
                        settings.set("ENABLED", True)
                    
                    # Save the settings
                    filter_config.ENABLED.save_settings()
                    
                    # Prepare a response message summarizing the rule
                    channels_text = ""
                    if category_ids:
                        channels_text += f"Categories: {', '.join([f'<#{cat_id}>' for cat_id in category_ids])}\n"
                    if channel_ids:
                        channels_text += f"Channels: {', '.join([f'<#{ch_id}>' for ch_id in channel_ids])}"
                    
                    response = f"✅ Keyword rule '{name}' {'created' if rule_id not in rules else 'updated'} successfully!\n\n"
                    response += f"Monitoring {channels_text}\n"
                    if alert_channel_id:
                        response += f"Alerts sent to: <#{alert_channel_id}>\n"
                    response += f"Keywords: {', '.join([f'`{k}`' for k in keyword_list])}\n"
                    response += f"Action: {'Delete messages' if delete else 'Notify only'} | Severity: {severity.capitalize()}"
                    
                    await interaction.followup.send(response)
                else:
                    await interaction.followup.send("⚠️ You must provide a rule name and at least one keyword to monitor.")
            
            # Reaction Forward Command - Simplified name
            @bot.tree.command(name="reaction", description="Configure reaction forward settings")
            @mod_only()
            async def reaction(
                interaction: discord.Interaction,
                whitelisted_category_id: str = None,
                blacklisted_channel_id: str = None
            ):
                # Import the permission checker
                from utils.permissions import check_interaction_permissions
                
                # Check if the user has permission to use this command
                if not await check_interaction_permissions(interaction, 'mod'):
                    return
                
                # Import configuration
                from config import forward_config
                from config import embed_config
                
                # Get current settings
                enabled = forward_config.ENABLED
                category_ids = forward_config.CATEGORY_IDS
                blacklist_channel_ids = forward_config.BLACKLIST_CHANNEL_IDS
                
                # If no parameters provided, show current configuration
                if not any([whitelisted_category_id, blacklisted_channel_id]):
                    embed = discord.Embed(
                        title="Reaction Forward Configuration",
                        description="Current settings for the reaction forward feature"
                    )
                    
                    # Apply styling from embed_config
                    embed = embed_config.apply_default_styling(embed)
                    
                    # Status field
                    embed.add_field(
                        name="Status", 
                        value=f"**{'Enabled' if enabled else 'Disabled'}**", 
                        inline=False
                    )
                    
                    # Whitelisted categories
                    category_mentions = []
                    for category_id in category_ids:
                        category = discord.utils.get(interaction.guild.categories, id=category_id)
                        if category:
                            category_mentions.append(f"{category.name} ({category_id})")
                        else:
                            category_mentions.append(f"Unknown ({category_id})")
                    
                    embed.add_field(
                        name="Whitelisted Categories", 
                        value='\n'.join(category_mentions) if category_mentions else "None", 
                        inline=False
                    )
                    
                    # Blacklisted channels
                    channel_mentions = []
                    for channel_id in blacklist_channel_ids:
                        channel = discord.utils.get(interaction.guild.channels, id=channel_id)
                        if channel:
                            channel_mentions.append(f"#{channel.name} ({channel_id})")
                        else:
                            channel_mentions.append(f"Unknown ({channel_id})")
                    
                    embed.add_field(
                        name="Blacklisted Channels", 
                        value='\n'.join(channel_mentions) if channel_mentions else "None", 
                        inline=False
                    )
                    
                    # Configuration guide
                    embed.add_field(
                        name="How to Configure", 
                        value="`/reaction whitelisted_category_id:123456789,234567890`\n`/reaction blacklisted_channel_id:987654321`", 
                        inline=False
                    )
                    
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                
                # Process whitelisted categories if provided
                if whitelisted_category_id:
                    try:
                        new_category_ids = [int(cat.strip()) for cat in whitelisted_category_id.split(',') if cat.strip().isdigit()]
                        
                        if not new_category_ids:
                            await interaction.response.send_message("⚠️ Invalid category IDs format. Please provide comma-separated numbers.", ephemeral=True)
                            return
                        
                        # Update categories
                        category_ids = new_category_ids
                        forward_config.ENABLED.set("ENABLED", True)
                        forward_config.CATEGORY_IDS.set("CATEGORY_IDS", category_ids)
                        
                    except ValueError:
                        await interaction.response.send_message("⚠️ Invalid category ID format. Please use numbers only.", ephemeral=True)
                        return
                
                # Process blacklisted channels if provided
                if blacklisted_channel_id:
                    try:
                        new_blacklist_ids = [int(ch.strip()) for ch in blacklisted_channel_id.split(',') if ch.strip().isdigit()]
                        
                        if not new_blacklist_ids:
                            await interaction.response.send_message("⚠️ Invalid channel IDs format. Please provide comma-separated numbers.", ephemeral=True)
                            return
                        
                        # Update blacklist
                        blacklist_channel_ids = new_blacklist_ids
                        forward_config.ENABLED.set("ENABLED", True)
                        forward_config.BLACKLIST_CHANNEL_IDS.set("BLACKLIST_CHANNEL_IDS", blacklist_channel_ids)
                        
                    except ValueError:
                        await interaction.response.send_message("⚠️ Invalid channel ID format. Please use numbers only.", ephemeral=True)
                        return
                
                # Save settings
                if forward_config.ENABLED.save_settings():
                    # Prepare response message
                    response_parts = ["✅ Reaction forward configuration updated!"]
                    
                    if whitelisted_category_id:
                        category_mentions = []
                        for category_id in category_ids:
                            category = discord.utils.get(interaction.guild.categories, id=category_id)
                            if category:
                                category_mentions.append(f"{category.name}")
                            else:
                                category_mentions.append(f"Unknown ({category_id})")
                        
                        if category_mentions:
                            response_parts.append(f"**Whitelisted Categories**: {', '.join(category_mentions)}")
                    
                    if blacklisted_channel_id:
                        channel_mentions = []
                        for channel_id in blacklist_channel_ids:
                            channel = discord.utils.get(interaction.guild.channels, id=channel_id)
                            if channel:
                                channel_mentions.append(f"#{channel.name}")
                            else:
                                channel_mentions.append(f"Unknown ({channel_id})")
                        
                        if channel_mentions:
                            response_parts.append(f"**Blacklisted Channels**: {', '.join(channel_mentions)}")
                    
                    response = "\n".join(response_parts)
                    await interaction.response.send_message(response, ephemeral=True)
                    
                    logger.info(f"Reaction forward configuration updated by {interaction.user}")
                else:
                    await interaction.response.send_message("⚠️ Failed to save settings", ephemeral=True)
            
            # Pinger Command - Simplified name
            @bot.tree.command(name="pinger", description="Configure mention notifications")
            @mod_only()
            async def pinger(
                interaction: discord.Interaction,
                channel: str = None,
                everyone: bool = None,
                here: bool = None,
                roles: bool = None
            ):
                # Import the permission checker
                from utils.permissions import check_interaction_permissions
                
                # Check if the user has permission to use this command
                if not await check_interaction_permissions(interaction, 'mod'):
                    return
                
                # Import configuration
                from config import pinger_config
                from config import embed_config
                
                # Get current settings directly from config object
                pn_enabled = pinger_config.ENABLED
                pn_monitor_everyone = pinger_config.MONITOR_EVERYONE
                pn_monitor_here = pinger_config.MONITOR_HERE
                pn_monitor_roles = pinger_config.MONITOR_ROLES
                pn_notif_channel_id = pinger_config.NOTIFICATION_CHANNEL_ID
                
                # If no parameters provided, show current settings
                if not any([channel, everyone, here, roles]):
                    embed = discord.Embed(
                        title="Mention Notification Configuration",
                        description="Current settings for mention notifications",
                    )
                    
                    # Apply styling from embed_config
                    embed = embed_config.apply_default_styling(embed)
                    
                    # Status field
                    status = "Enabled" if pn_enabled else "Disabled"
                    embed.add_field(
                        name="Status", 
                        value=f"**{status}**", 
                        inline=False
                    )
                    
                    # Notification channel
                    notification_channel = None
                    if pn_notif_channel_id:
                        notification_channel = discord.utils.get(
                            interaction.guild.channels, 
                            id=pn_notif_channel_id
                        )
                    
                    embed.add_field(
                        name="Notification Channel", 
                        value=f"#{notification_channel.name}" if notification_channel else "Not configured", 
                        inline=False
                    )
                    
                    # Monitored mentions
                    mentions = []
                    if pn_monitor_everyone:
                        mentions.append("✅ @everyone")
                    else:
                        mentions.append("❌ @everyone")
                        
                    if pn_monitor_here:
                        mentions.append("✅ @here")
                    else:
                        mentions.append("❌ @here")
                        
                    if pn_monitor_roles:
                        mentions.append("✅ @role mentions")
                    else:
                        mentions.append("❌ @role mentions")
                    
                    embed.add_field(
                        name="Monitored Mentions", 
                        value='\n'.join(mentions), 
                        inline=False
                    )
                    
                    # Configuration guide
                    embed.add_field(
                        name="How to Configure", 
                        value="`/pinger channel:123456789 everyone:true here:true roles:true`", 
                        inline=False
                    )
                    
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                    
                # Process parameters to update configuration
                changes_made = False
                response_parts = ["✅ Mention notification settings updated!"]
                
                # Update notification channel
                if channel:
                    try:
                        channel_id = int(channel)
                        target_channel = interaction.guild.get_channel(channel_id)
                        if target_channel:
                            pinger_config.NOTIFICATION_CHANNEL_ID = channel_id
                            response_parts.append(f"Notification channel: <#{channel_id}>")
                            changes_made = True
                        else:
                            response_parts.append(f"⚠️ Could not find channel with ID {channel}")
                    except ValueError:
                        response_parts.append("⚠️ Invalid channel ID format")
                
                # Update mention monitoring settings
                if everyone is not None:
                    pinger_config.MONITOR_EVERYONE = everyone
                    response_parts.append(f"Monitor @everyone: {'Enabled' if everyone else 'Disabled'}")
                    changes_made = True
                
                if here is not None:
                    pinger_config.MONITOR_HERE = here
                    response_parts.append(f"Monitor @here: {'Enabled' if here else 'Disabled'}")
                    changes_made = True
                
                if roles is not None:
                    pinger_config.MONITOR_ROLES = roles
                    response_parts.append(f"Monitor @role mentions: {'Enabled' if roles else 'Disabled'}")
                    changes_made = True
                
                # Enable the module if any settings were changed and it's currently disabled
                if changes_made:
                    if not pn_enabled:
                        pinger_config.ENABLED = True
                        response_parts.append("Module automatically enabled")
                    
                    # Save settings
                    if pinger_config.save_config():
                        logger.info(f"Pinger settings updated by {interaction.user}")
                    else:
                        response_parts.append("⚠️ Failed to save settings")
                else:
                    response_parts = ["No changes were made to settings"]
                
                await interaction.response.send_message('\n'.join(response_parts), ephemeral=True)

            # LuisaViaRoma Adder - Specialized command for LVR store setup
            @bot.tree.command(name="luisaviaroma_adder", description="Set up LuisaViaRoma link reactions")
            @mod_only()
            async def luisaviaroma_adder(
                interaction: discord.Interaction,
                channel_ids: str = None,
                file_path: str = None
            ):
                # Import the permission checker
                from utils.permissions import check_interaction_permissions
                
                # Check if the user has permission to use this command
                if not await check_interaction_permissions(interaction, 'mod'):
                    return
                
                # Import configuration
                from config import link_config
                from config import embed_config
                
                # Get current settings
                stores = link_config.STORES
                
                # LuisaViaRoma store ID (lowercase for consistency)
                store_id = "luisaviaroma"
                store_name = "LUISAVIAROMA"
                
                # Check if store already exists in configuration
                existing_store = stores.get(store_id) if isinstance(stores, dict) else None
                if not existing_store and isinstance(stores, list):
                    for store in stores:
                        if isinstance(store, dict) and store.get('name', '').lower() == "luisaviaroma":
                            existing_store = store
                            break
                
                # If no parameters provided, show current configuration
                if not any([channel_ids, file_path]):
                    embed = discord.Embed(
                        title="LuisaViaRoma Link Configuration",
                        description="Current settings for LuisaViaRoma link reactions",
                    )
                    
                    # Apply styling from embed_config
                    embed = embed_config.apply_default_styling(embed)
                    
                    if existing_store:
                        # Status field
                        status = "Enabled" if existing_store.get('enabled', False) else "Disabled"
                        embed.add_field(
                            name="Status", 
                            value=f"**{status}**", 
                            inline=False
                        )
                        
                        # Monitored Channels
                        channel_ids = existing_store.get('channel_ids', [])
                        channel_mentions = []
                        for channel_id in channel_ids:
                            channel = discord.utils.get(interaction.guild.channels, id=channel_id)
                            if channel:
                                channel_mentions.append(f"#{channel.name} ({channel_id})")
                            else:
                                channel_mentions.append(f"Unknown ({channel_id})")
                        
                        embed.add_field(
                            name="Monitored Channels", 
                            value='\n'.join(channel_mentions) if channel_mentions else "None configured", 
                            inline=False
                        )
                        
                        # File path
                        file_path = existing_store.get('file_path')
                        embed.add_field(
                            name="File Path", 
                            value=f"`{file_path}`" if file_path else "Not configured", 
                            inline=False
                        )
                        
                        # Detection configuration
                        detection = existing_store.get('detection', {})
                        detection_type = detection.get('type', 'None')
                        detection_value = detection.get('value', 'None')
                        
                        embed.add_field(
                            name="Detection Configuration", 
                            value=f"Type: {detection_type}\nValue: {detection_value}", 
                            inline=False
                        )
                        
                        # Fixed values
                        embed.add_field(
                            name="Fixed Configuration", 
                            value=f"Emoji: 🔗\nDomain: luisaviaroma.com", 
                            inline=False
                        )
                    else:
                        embed.add_field(
                            name="Status", 
                            value="**Not Configured**", 
                            inline=False
                        )
                    
                    # Configuration guide
                    embed.add_field(
                        name="How to Configure", 
                        value="`/luisaviaroma_adder channel_ids:123456789,987654321 file_path:/path/to/urls.txt`", 
                        inline=False
                    )
                    
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                
                # If parameters provided, update configuration
                if channel_ids:
                    # Process channel IDs
                    try:
                        channel_list = [int(ch.strip()) for ch in channel_ids.split(',') if ch.strip().isdigit()]
                        if not channel_list:
                            await interaction.response.send_message("⚠️ Invalid channel IDs. Please provide comma-separated numbers.", ephemeral=True)
                            return
                    except ValueError:
                        await interaction.response.send_message("⚠️ Invalid channel ID format. Please use comma-separated numbers.", ephemeral=True)
                        return
                else:
                    # If channels not provided but updating file_path, keep existing channels
                    channel_list = existing_store.get('channel_ids', []) if existing_store else []
                
                # Create or update LuisaViaRoma store configuration
                store_config = {
                    'enabled': True,
                    'name': store_name,
                    'description': "Extract product IDs from LUISAVIAROMA embeds",
                    'channel_ids': channel_list,
                    'detection': {
                        'type': 'author_name',
                        'value': 'LUISAVIAROMA'
                    },
                    'extraction': {
                        'primary': 'url',
                        'pattern': r'\/[^\/]+\/([^\/]+)$',
                        'fallback': 'field_pid'
                    }
                }
                
                # Add file path if provided
                if file_path:
                    store_config['file_path'] = file_path
                elif existing_store and 'file_path' in existing_store:
                    # Keep existing file path if not provided and updating existing config
                    store_config['file_path'] = existing_store['file_path']
                
                # Update the store in the stores dictionary
                stores[store_id] = store_config
                
                # Save settings
                link_config.STORES.set("STORES", stores)
                link_config.ENABLED.set("ENABLED", True)
                if link_config.STORES.save_settings():
                    logger.info(f"LuisaViaRoma link reaction configured by {interaction.user}")
                    
                    # Prepare channel mentions for display
                    channel_mentions = []
                    for channel_id in channel_list:
                        channel = interaction.guild.get_channel(channel_id)
                        if channel:
                            channel_mentions.append(f"<#{channel_id}>")
                        else:
                            channel_mentions.append(f"Unknown ({channel_id})")
                    
                    response = f"✅ LuisaViaRoma link reaction configured successfully!\n\n"
                    response += f"Monitoring channels: {', '.join(channel_mentions)}\n"
                    if file_path or (existing_store and 'file_path' in existing_store):
                        displayed_path = file_path or existing_store.get('file_path')
                        response += f"File path: `{displayed_path}`\n"
                    response += f"Detection: {store_config['detection']['type']} - {store_config['detection']['value']}\n"
                    response += f"Emoji: 🔗"
                    
                    await interaction.response.send_message(response, ephemeral=True)
                else:
                    await interaction.response.send_message("⚠️ Failed to save settings", ephemeral=True)
            
            # LuisaViaRoma Remover - Specialized command for removing PIDs from files
            @bot.tree.command(name="luisaviaroma_remover", description="Remove PIDs from LuisaViaRoma tracking and configure settings")
            @mod_only()
            async def luisaviaroma_remover(
                interaction: discord.Interaction,
                pid: str = None,
                channel_ids: str = None,
                file_path: str = None
            ):
                # Import the permission checker
                from utils.permissions import check_interaction_permissions
                
                # Check if the user has permission to use this command
                if not await check_interaction_permissions(interaction, 'mod'):
                    return
                
                # Import configuration
                from config import link_config
                from config import embed_config
                
                # Get current settings
                stores = link_config.STORES
                
                # LuisaViaRoma store ID (lowercase for consistency)
                store_id = "luisaviaroma"
                store_name = "LUISAVIAROMA"
                
                # Check if store already exists in configuration
                existing_store = stores.get(store_id) if isinstance(stores, dict) else None
                if not existing_store and isinstance(stores, list):
                    for store in stores:
                        if isinstance(store, dict) and store.get('name', '').lower() == "luisaviaroma":
                            existing_store = store
                            break
                
                # If PID provided, try to remove it from the file
                if pid:
                    success, message = await remove_pid_from_file(pid, None)
                    await interaction.response.send_message(message, ephemeral=True)
                    return
                
                # If no parameters provided, show current configuration
                if not any([channel_ids, file_path]):
                    embed = discord.Embed(
                        title="LuisaViaRoma Remover Configuration",
                        description="Current settings for LuisaViaRoma PID removal",
                    )
                    
                    # Apply styling from embed_config
                    embed = embed_config.apply_default_styling(embed)
                    
                    if existing_store:
                        # Status field
                        status = "Enabled" if existing_store.get('enabled', False) else "Disabled"
                        embed.add_field(
                            name="Status", 
                            value=f"**{status}**", 
                            inline=False
                        )
                        
                        # Monitored Channels
                        channel_ids = existing_store.get('channel_ids', [])
                        channel_mentions = []
                        for channel_id in channel_ids:
                            channel = discord.utils.get(interaction.guild.channels, id=channel_id)
                            if channel:
                                channel_mentions.append(f"#{channel.name} ({channel_id})")
                            else:
                                channel_mentions.append(f"Unknown ({channel_id})")
                        
                        embed.add_field(
                            name="Monitored Channels", 
                            value='\n'.join(channel_mentions) if channel_mentions else "None configured", 
                            inline=False
                        )
                        
                        # File path
                        file_path = existing_store.get('file_path')
                        embed.add_field(
                            name="File Path", 
                            value=f"`{file_path}`" if file_path else "Not configured", 
                            inline=False
                        )
                        
                        # Adding instructions for removing PIDs
                        embed.add_field(
                            name="How to Remove PIDs", 
                            value="Use `/luisaviaroma_remover pid:123456` to remove a specific PID\nor use the context menu by right-clicking on a user and selecting 'Remove PID'", 
                            inline=False
                        )
                    else:
                        embed.add_field(
                            name="Status", 
                            value="**Not Configured**", 
                            inline=False
                        )
                    
                    # Configuration guide
                    embed.add_field(
                        name="How to Configure", 
                        value="`/luisaviaroma_remover channel_ids:123456789,987654321 file_path:/path/to/urls.txt`", 
                        inline=False
                    )
                    
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                
                # If parameters provided, update configuration (same logic as luisaviaroma_adder)
                if channel_ids:
                    # Process channel IDs
                    try:
                        channel_list = [int(ch.strip()) for ch in channel_ids.split(',') if ch.strip().isdigit()]
                        if not channel_list:
                            await interaction.response.send_message("⚠️ Invalid channel IDs. Please provide comma-separated numbers.", ephemeral=True)
                            return
                    except ValueError:
                        await interaction.response.send_message("⚠️ Invalid channel ID format. Please use comma-separated numbers.", ephemeral=True)
                        return
                else:
                    # If channels not provided but updating file_path, keep existing channels
                    channel_list = existing_store.get('channel_ids', []) if existing_store else []
                
                # Create or update LuisaViaRoma store configuration
                store_config = {
                    'enabled': True,
                    'name': store_name,
                    'description': "Extract product IDs from LUISAVIAROMA embeds",
                    'channel_ids': channel_list,
                    'detection': {
                        'type': 'author_name',
                        'value': 'LUISAVIAROMA'
                    },
                    'extraction': {
                        'primary': 'url',
                        'pattern': r'\/[^\/]+\/([^\/]+)$',
                        'fallback': 'field_pid'
                    }
                }
                
                # Add file path if provided
                if file_path:
                    store_config['file_path'] = file_path
                elif existing_store and 'file_path' in existing_store:
                    # Keep existing file path if not provided and updating existing config
                    store_config['file_path'] = existing_store['file_path']
                
                # Update the store in the stores dictionary
                if isinstance(stores, dict):
                    stores[store_id] = store_config
                elif isinstance(stores, list):
                    # If it's a list, find and replace the existing store or append
                    found = False
                    for i, store in enumerate(stores):
                        if isinstance(store, dict) and store.get('name', '').lower() == store_name.lower():
                            stores[i] = store_config
                            found = True
                            break
                    if not found:
                        stores.append(store_config)
                else:
                    # Initialize as a dictionary if it's neither
                    stores = {store_id: store_config}
                
                # Save settings
                link_config.STORES.set("STORES", stores)
                link_config.ENABLED.set("ENABLED", True)
                if link_config.STORES.save_settings():
                    logger.info(f"LuisaViaRoma remover configured by {interaction.user}")
                    
                    # Prepare channel mentions for display
                    channel_mentions = []
                    for channel_id in channel_list:
                        channel = interaction.guild.get_channel(channel_id)
                        if channel:
                            channel_mentions.append(f"<#{channel_id}>")
                        else:
                            channel_mentions.append(f"Unknown ({channel_id})")
                    
                    response = f"✅ LuisaViaRoma remover configured successfully!\n\n"
                    response += f"Monitoring channels: {', '.join(channel_mentions)}\n"
                    if file_path or (existing_store and 'file_path' in existing_store):
                        displayed_path = file_path or existing_store.get('file_path')
                        response += f"File path: `{displayed_path}`\n"
                    
                    await interaction.response.send_message(response, ephemeral=True)
                else:
                    await interaction.response.send_message("⚠️ Failed to save settings", ephemeral=True)
            
            logger.info("Successfully registered all module commands")
            return True
        except Exception as e:
            logger.error(f"Error registering module commands: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Exception traceback: {traceback.format_exc()}")
            return False 