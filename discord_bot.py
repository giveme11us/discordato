#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Bot - Main Entry Point

This script initializes and runs the Discord bot system.
It handles command-line arguments and configuration loading.
"""

import argparse
import logging
import os
import sys
from dotenv import load_dotenv
import discord
from discord.ext import commands

from core.bot_manager import BotManager
from config.environment.environment import load_environment
from core.command_sync import CommandSync
from config.features.embed_config import embed as embed_config
from modules.features.mod.keyword_filter.keyword_filter import setup_keyword_filter
from modules.features.mod.reaction_forward.reaction_forward import setup_reaction_forward
from modules.features.mod.link_reaction.link_reaction import setup_link_reaction
from modules.features.mod.pinger.pinger import setup_pinger
from modules.features.redeye.profile_cmd import setup_profile_cmd
from config.features.moderation import filter as filter_config, mod as mod_config
from config.features.reactions import forward as forward_config, link as link_config
from config.features.pinger_config import pinger_config
from config.features.redeye_config import redeye as redeye_config

# Remove direct imports of setup functions - we'll use cogs instead

def main():
    """
    Main entry point for the Discord bot application.
    Parses command-line arguments, loads configuration, and starts the bot.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Discord Bot')
    parser.add_argument('--config', type=str, default='.env',
                        help='Path to the configuration file')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode')
    args = parser.parse_args()

    # Load environment variables
    load_environment(args.config)

    # Configure logging
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger('discord_bot')
    logger.info("Starting Discord Bot")
    
    # Override log level if debug flag is provided
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    try:
        # Initialize the bot manager
        bot_manager = BotManager()
        
        # Register the setup_modules function with each bot in single mode
        if 'main' in bot_manager.bots:
            bot = bot_manager.bots['main']
            
            # Add application command error handler for consistent styling
            from config.features.embed_config import embed as embed_config
            
            @bot.tree.error
            async def on_app_command_error(interaction: discord.Interaction, error):
                """Handle errors from application commands (slash commands)"""
                error_message = str(error)
                logger.error(f"Application command error in {interaction.command.name if interaction.command else 'unknown command'}: {error_message}")
                
                # Check for permission errors (CheckFailure)
                if isinstance(error, discord.app_commands.CheckFailure):
                    # Create a better permission error embed
                    embed = discord.Embed(
                        title="Permission Denied",
                        description="You don't have permission to use this command.",
                        color=discord.Color.red()
                    )
                    
                    # Add information about required roles
                    from utils.permissions import get_whitelisted_roles
                    module_name = 'mod'  # Default to mod since most commands use this
                    
                    # Try to extract the module name from the error message
                    if "module" in error_message.lower():
                        # New logic to better detect module name
                        if 'redeye' in error_message.lower():
                            module_name = 'redeye'
                        elif 'mod' in error_message.lower():
                            module_name = 'mod'
                        elif 'online' in error_message.lower():
                            module_name = 'online'
                        elif 'instore' in error_message.lower():
                            module_name = 'instore'
                        else:
                            # Legacy extraction as fallback
                            module_parts = error_message.lower().split("module")
                            if len(module_parts) > 1 and module_parts[0].strip().endswith("use "):
                                # Extract module name, assuming format "... use Module module ..."
                                extracted_name = module_parts[0].strip().split(" ")[-1].lower()
                                if extracted_name in ['mod', 'online', 'instore', 'redeye']:
                                    module_name = extracted_name
                    
                    # Get the whitelist roles for this module
                    role_ids = get_whitelisted_roles(module_name)
                    logger.debug(f"Permission denied for {module_name} module. Available roles: {role_ids}")
                    
                    # Add info about required roles if available
                    if role_ids:
                        role_mentions = []
                        for role_id in role_ids:
                            role = discord.utils.get(interaction.guild.roles, id=role_id) if interaction.guild else None
                            if role:
                                role_mentions.append(f"<@&{role_id}> ({role.name})")
                            else:
                                role_mentions.append(f"Role ID: {role_id}")
                        
                        embed.add_field(
                            name="Required Roles",
                            value="You need one of these roles:\n" + "\n".join(role_mentions),
                            inline=False
                        )
                else:
                    # Standard error embed for non-permission errors
                    embed = discord.Embed(
                        title="Command Error",
                        description=f"An error occurred while processing your command.",
                        color=discord.Color.red()
                    )
                    
                    # Add error details
                    embed.add_field(name="Error Details", value=f"```{error_message}```", inline=False)
                
                # Apply default styling from embed_config
                embed = embed_config.apply_default_styling(embed)
                
                # Try to respond with the error message
                try:
                    if interaction.response.is_done():
                        await interaction.followup.send(embed=embed, ephemeral=True)
                    else:
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                except Exception as e:
                    logger.error(f"Failed to send error response: {e}")
            
            # Register our simplified module commands
            command_sync = CommandSync()
            command_sync.register_module_commands(bot)
            logger.info("Registered simplified module commands")
            
            # Import the module setup functions
            from modules.features.mod.keyword_filter.keyword_filter import setup_keyword_filter
            from modules.features.mod.reaction_forward.reaction_forward import setup_reaction_forward
            from modules.features.mod.link_reaction.link_reaction import setup_link_reaction
            from modules.features.mod.pinger.pinger import setup_pinger
            # Import the new redeye module profile command
            from modules.features.redeye.profile_cmd import setup_profile_cmd
            
            # Set up event handlers directly
            logger.info("Setting up direct event handlers for message and reaction processing")
            
            # We need to create wrapper functions to properly handle property access
            def setup_keyword_filter_wrapper(bot):
                # Import the module for direct property access bypass
                from config.features.moderation import filter as filter_config
                # Store original property values
                original_filters = dict(filter_config.FILTERS)  # Convert to dict to ensure it's serializable
                original_category_ids = list(filter_config.CATEGORY_IDS)  # Convert to list
                original_blacklist = list(filter_config.BLACKLIST_CHANNEL_IDS)  # Convert to list
                
                # Store original property descriptors
                original_filters_prop = type(filter_config).FILTERS
                original_category_ids_prop = type(filter_config).CATEGORY_IDS
                original_blacklist_prop = type(filter_config).BLACKLIST_CHANNEL_IDS
                
                # Override the properties with simple values
                setattr(type(filter_config), 'FILTERS', original_filters)
                setattr(type(filter_config), 'CATEGORY_IDS', original_category_ids)
                setattr(type(filter_config), 'BLACKLIST_CHANNEL_IDS', original_blacklist)
                
                try:
                    # Call the original setup function
                    setup_keyword_filter(bot)
                finally:
                    # Restore original property descriptors
                    setattr(type(filter_config), 'FILTERS', original_filters_prop)
                    setattr(type(filter_config), 'CATEGORY_IDS', original_category_ids_prop)
                    setattr(type(filter_config), 'BLACKLIST_CHANNEL_IDS', original_blacklist_prop)
            
            def setup_reaction_forward_wrapper(bot):
                # Import the module for direct property access bypass
                from config.features.reactions import forward as forward_config
                # Store original property values
                original_enabled = bool(forward_config.ENABLED)
                original_msg_forward = bool(forward_config.ENABLE_FORWARDING)
                original_category_ids = list(forward_config.CATEGORY_IDS)
                original_blacklist = list(forward_config.BLACKLIST_CHANNEL_IDS)
                original_destination_channel = forward_config.DESTINATION_CHANNEL_ID
                
                # Store original property descriptors
                original_enabled_prop = type(forward_config).ENABLED
                original_msg_forward_prop = type(forward_config).ENABLE_FORWARDING
                original_category_ids_prop = type(forward_config).CATEGORY_IDS
                original_blacklist_prop = type(forward_config).BLACKLIST_CHANNEL_IDS
                original_destination_channel_prop = type(forward_config).DESTINATION_CHANNEL_ID
                
                # Override the properties with simple values
                setattr(type(forward_config), 'ENABLED', original_enabled)
                setattr(type(forward_config), 'ENABLE_FORWARDING', original_msg_forward)
                setattr(type(forward_config), 'CATEGORY_IDS', original_category_ids)
                setattr(type(forward_config), 'BLACKLIST_CHANNEL_IDS', original_blacklist)
                setattr(type(forward_config), 'DESTINATION_CHANNEL_ID', original_destination_channel)
                
                try:
                    # Call the original setup function
                    setup_reaction_forward(bot)
                finally:
                    # Restore original property descriptors
                    setattr(type(forward_config), 'ENABLED', original_enabled_prop)
                    setattr(type(forward_config), 'ENABLE_FORWARDING', original_msg_forward_prop)
                    setattr(type(forward_config), 'CATEGORY_IDS', original_category_ids_prop)
                    setattr(type(forward_config), 'BLACKLIST_CHANNEL_IDS', original_blacklist_prop)
                    setattr(type(forward_config), 'DESTINATION_CHANNEL_ID', original_destination_channel_prop)
            
            def setup_link_reaction_wrapper(bot):
                # Import the module for direct property access bypass
                from config.features.reactions import link as link_config
                # Store original property values
                original_enabled = bool(link_config.ENABLED)
                original_category_ids = list(link_config.CATEGORY_IDS)
                original_blacklist = list(link_config.BLACKLIST_CHANNEL_IDS)
                original_stores = link_config.STORES  # Remove dict() call since it's already a dict
                
                # Store original property descriptors
                original_enabled_prop = type(link_config).ENABLED
                original_category_ids_prop = type(link_config).CATEGORY_IDS
                original_blacklist_prop = type(link_config).BLACKLIST_CHANNEL_IDS
                original_stores_prop = type(link_config).STORES
                
                # Override the properties with simple values
                setattr(type(link_config), 'ENABLED', original_enabled)
                setattr(type(link_config), 'CATEGORY_IDS', original_category_ids)
                setattr(type(link_config), 'BLACKLIST_CHANNEL_IDS', original_blacklist)
                setattr(type(link_config), 'STORES', original_stores)
                
                try:
                    # Call the original setup function
                    setup_link_reaction(bot)
                finally:
                    # Restore original property descriptors
                    setattr(type(link_config), 'ENABLED', original_enabled_prop)
                    setattr(type(link_config), 'CATEGORY_IDS', original_category_ids_prop)
                    setattr(type(link_config), 'BLACKLIST_CHANNEL_IDS', original_blacklist_prop)
                    setattr(type(link_config), 'STORES', original_stores_prop)
            
            def setup_pinger_wrapper(bot):
                # Import the module for direct property access bypass
                from config.features.pinger_config import pinger_config
                # Store original property values
                original_enabled = bool(pinger_config.ENABLED)
                original_monitor_everyone = bool(pinger_config.MONITOR_EVERYONE)
                original_monitor_here = bool(pinger_config.MONITOR_HERE)
                original_monitor_roles = bool(pinger_config.MONITOR_ROLES)
                original_notif_channel = pinger_config.NOTIFICATION_CHANNEL_ID
                original_whitelist = list(pinger_config.WHITELIST_ROLE_IDS)
                
                # Store original property descriptors
                original_enabled_prop = type(pinger_config).ENABLED
                original_monitor_everyone_prop = type(pinger_config).MONITOR_EVERYONE
                original_monitor_here_prop = type(pinger_config).MONITOR_HERE
                original_monitor_roles_prop = type(pinger_config).MONITOR_ROLES
                original_notif_channel_prop = type(pinger_config).NOTIFICATION_CHANNEL_ID
                original_whitelist_prop = type(pinger_config).WHITELIST_ROLE_IDS
                
                # Override the properties with simple values
                setattr(type(pinger_config), 'ENABLED', original_enabled)
                setattr(type(pinger_config), 'MONITOR_EVERYONE', original_monitor_everyone)
                setattr(type(pinger_config), 'MONITOR_HERE', original_monitor_here)
                setattr(type(pinger_config), 'MONITOR_ROLES', original_monitor_roles)
                setattr(type(pinger_config), 'NOTIFICATION_CHANNEL_ID', original_notif_channel)
                setattr(type(pinger_config), 'WHITELIST_ROLE_IDS', original_whitelist)
                
                try:
                    # Call the original setup function
                    setup_pinger(bot)
                finally:
                    # Restore original property descriptors
                    setattr(type(pinger_config), 'ENABLED', original_enabled_prop)
                    setattr(type(pinger_config), 'MONITOR_EVERYONE', original_monitor_everyone_prop)
                    setattr(type(pinger_config), 'MONITOR_HERE', original_monitor_here_prop)
                    setattr(type(pinger_config), 'MONITOR_ROLES', original_monitor_roles_prop)
                    setattr(type(pinger_config), 'NOTIFICATION_CHANNEL_ID', original_notif_channel_prop)
                    setattr(type(pinger_config), 'WHITELIST_ROLE_IDS', original_whitelist_prop)
            
            def setup_profile_cmd_wrapper(bot):
                """
                Initialize the redeye module by working around property issues.
                
                This function temporarily overrides property accessors with fixed values
                to ensure consistent behavior during initialization.
                
                Args:
                    bot: The Discord bot instance
                
                Returns:
                    bool: True if successful, False otherwise
                """
                # Import the redeye configuration
                from config.features.redeye_config import redeye as redeye_config
                
                try:
                    # Store original property values
                    original_enabled = bool(redeye_config.ENABLED)
                    original_notification_channel = redeye_config.NOTIFICATION_CHANNEL_ID
                    original_profiles_path = redeye_config.PROFILES_PATH
                    
                    # Store original property descriptors
                    original_enabled_prop = type(redeye_config).ENABLED
                    original_notification_channel_prop = type(redeye_config).NOTIFICATION_CHANNEL_ID
                    original_profiles_path_prop = type(redeye_config).PROFILES_PATH
                    
                    # Override the properties with simple values
                    setattr(type(redeye_config), 'ENABLED', original_enabled)
                    setattr(type(redeye_config), 'NOTIFICATION_CHANNEL_ID', original_notification_channel)
                    setattr(type(redeye_config), 'PROFILES_PATH', original_profiles_path)
                    
                    # Now call the actual setup function for the profile command
                    from modules.features.redeye.profile_cmd import setup_profile_cmd
                    setup_profile_cmd(bot)
                    
                    # Restore original property descriptors
                    setattr(type(redeye_config), 'ENABLED', original_enabled_prop)
                    setattr(type(redeye_config), 'NOTIFICATION_CHANNEL_ID', original_notification_channel_prop)
                    setattr(type(redeye_config), 'PROFILES_PATH', original_profiles_path_prop)
                    
                    return True
                except Exception as e:
                    logger.error(f"Error setting up redeye module: {e}")
                    return False
            
            # Initialize the event handlers tracking
            bot.event_handlers = {}

            # Add additional debug logging for message event handler registration
            original_on_message = bot.on_message
            @bot.event
            async def on_message(message):
                logger.debug(f"Message received: {message.content[:50]}{'...' if len(message.content) > 50 else ''}")
                
                # Process through keyword filter if available
                if hasattr(bot, 'keyword_filter_process'):
                    await bot.keyword_filter_process(bot, message)
                
                # Process other event handlers
                await original_on_message(message) if original_on_message else None
                
                # Add needed event handling here
                await bot.process_commands(message)
            
            # Track the message handler
            bot.event_handlers['on_message'] = 1
            
            # Initialize all modules directly without loading cogs
            # This way we get the event handlers but use our own commands
            try:
                # Get the enabled modules from environment
                enabled_modules_str = os.getenv('ENABLED_MODULES', '')
                enabled_modules = [m.strip() for m in enabled_modules_str.split(',') if m.strip()]
                
                if 'mod' in enabled_modules:
                    logger.info("Setting up mod module event handlers...")
                    
                    # Set the log level to DEBUG for this setup phase to see all event registrations
                    logger.setLevel(logging.DEBUG)
                    
                    # Use our wrapper to avoid property issues
                    setup_keyword_filter_wrapper(bot)
                    logger.info("Keyword filter handlers registered")
                    
                    # For the rest, we might need similar wrappers if they have property issues
                    # For now, try direct calls
                    try:
                        setup_reaction_forward_wrapper(bot)
                        logger.info("Reaction forward handlers registered")
                    except AttributeError as e:
                        logger.error(f"Error in reaction_forward setup: {str(e)}")
                    
                    try:
                        setup_link_reaction_wrapper(bot)
                        logger.info("Link reaction handlers registered")
                    except AttributeError as e:
                        logger.error(f"Error in link_reaction setup: {str(e)}")
                    
                    # Set up the pinger module
                    try:
                        setup_pinger_wrapper(bot)
                        logger.info("Pinger module set up successfully")
                    except Exception as e:
                        logger.error(f"Error setting up pinger module: {e}")
                    
                    # Set up the redeye module
                    try:
                        setup_profile_cmd_wrapper(bot)
                        logger.info("Redeye module set up successfully")
                    except Exception as e:
                        logger.error(f"Error setting up redeye module: {e}")
                    
                    # List all registered event handlers for verification
                    event_handlers = {}
                    for event_name in dir(bot):
                        if event_name.startswith('on_'):
                            handlers = getattr(bot, '_listeners', {}).get(event_name, [])
                            if handlers:
                                event_handlers[event_name] = len(handlers)
                    
                    logger.info(f"Registered event handlers: {event_handlers}")
                    logger.info("Successfully set up all mod module event handlers")
            except Exception as e:
                logger.error(f"Error setting up event handlers: {str(e)}")
                import traceback
                logger.error(f"Exception traceback: {traceback.format_exc()}")
            
            @bot.event
            async def on_ready():
                logger.info(f"Bot {bot.user.name} is ready!")
                logger.info(f"Bot ID: {bot.user.id}")
                logger.info(f"Connected to {len(bot.guilds)} guilds")
                
                # Log guilds the bot is connected to
                for guild in bot.guilds:
                    logger.info(f"Connected to guild: {guild.name} (ID: {guild.id})")
                    logger.info(f"Guild has {len(guild.channels)} channels and {len(guild.members)} members")
                
                # Set up a periodic health check to verify the bot is still listening
                import asyncio
                async def health_check():
                    while True:
                        logger.info("Bot is alive and listening for events")
                        await asyncio.sleep(300)  # Log every 5 minutes
                
                bot.loop.create_task(health_check())
                logger.info("Bot is now actively listening for messages and reactions")
        
        # Start the bots
        bot_manager.start()
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        sys.exit(1)

# We've removed the setup_modules function as we now handle event handlers directly

if __name__ == "__main__":
    main()