"""
path: modules/mod/reaction/__init__.py
purpose: Manages automatic embed forwarding from whitelisted categories
critical:
- Uses environment variables for configuration
- Automatically adds reactions to messages with embeds in whitelisted categories
- Forwards embeds to configured channel when reacted to
"""

import os
import logging
import discord

logger = logging.getLogger('discord_bot.mod.reaction')

# Default configuration
REACTION_CONFIG = {
    "ENABLED": True,
    "FORWARD_EMOJI": "➡️",  # Default forward emoji
    "FORWARD_CHANNEL_ID": None  # Channel to forward messages to
}

def load_config():
    """Load configuration from environment variables."""
    forward_channel_id = os.getenv("REACTION_FORWARD_CHANNEL_ID")
    if forward_channel_id:
        try:
            REACTION_CONFIG["FORWARD_CHANNEL_ID"] = int(forward_channel_id)
            logger.info(f"Loaded forward channel ID: {REACTION_CONFIG['FORWARD_CHANNEL_ID']}")
        except ValueError:
            logger.error(f"Invalid forward channel ID: {forward_channel_id}")
    else:
        logger.warning("No forward channel configured! Please set REACTION_FORWARD_CHANNEL_ID in .env")

def get_whitelisted_categories():
    """Get whitelisted category IDs from environment."""
    category_ids_str = os.getenv("REACTION_FORWARD_CATEGORY_IDS", "")
    logger.info(f"Reading whitelisted categories from env: {category_ids_str}")
    if not category_ids_str:
        return []
    try:
        categories = [int(cat_id.strip()) for cat_id in category_ids_str.split(",") if cat_id.strip()]
        logger.info(f"Parsed whitelisted categories: {categories}")
        return categories
    except (ValueError, TypeError) as e:
        logger.error(f"Error parsing whitelisted categories: {e}")
        return []

async def handle_message(message):
    """Handle message events for adding reactions."""
    try:
        # Skip DM messages
        if not isinstance(message.channel, discord.TextChannel):
            return
            
        # Skip if message is in the forward channel
        if REACTION_CONFIG["FORWARD_CHANNEL_ID"] and message.channel.id == REACTION_CONFIG["FORWARD_CHANNEL_ID"]:
            return
            
        # Skip if not enabled
        if not REACTION_CONFIG["ENABLED"]:
            return
            
        # Skip if not in a category
        if not message.channel.category:
            return
            
        # Get whitelisted categories
        whitelisted_categories = get_whitelisted_categories()
        if not whitelisted_categories:
            return
            
        # Skip if category not whitelisted
        if message.channel.category.id not in whitelisted_categories:
            return
            
        # Skip if message has no embeds
        if not message.embeds:
            return
            
        # Add forward reaction
        await message.add_reaction(REACTION_CONFIG["FORWARD_EMOJI"])
        logger.info(f"Added reaction to message {message.id} in {message.channel.name} (has {len(message.embeds)} embeds)")
        
    except Exception as e:
        logger.error(f"Error in handle_message: {e}", exc_info=True)

async def setup(bot):
    """Set up the reaction module."""
    logger.info("Setting up reaction module")
    
    # Load configuration
    load_config()
    
    # Register message handler
    @bot.listen('on_message')
    async def on_message_reaction(message):
        await handle_message(message)
                
    # Register reaction handler
    @bot.listen('on_raw_reaction_add')
    async def on_raw_reaction_add(payload):
        # Skip bot reactions
        if payload.user_id == bot.user.id:
            return
            
        # Skip if not enabled or no forward channel configured
        if not REACTION_CONFIG["ENABLED"]:
            logger.info("Reaction module disabled")
            return
            
        if not REACTION_CONFIG["FORWARD_CHANNEL_ID"]:
            logger.warning("No forward channel configured! Please set REACTION_FORWARD_CHANNEL_ID in .env")
            return
            
        # Skip if not the forward emoji
        if str(payload.emoji) != REACTION_CONFIG["FORWARD_EMOJI"]:
            return
            
        try:
            # Get the source channel and message
            source_channel = bot.get_channel(payload.channel_id)
            if not source_channel or not source_channel.category:
                return
                
            # Skip if category not whitelisted
            whitelisted_categories = get_whitelisted_categories()
            if not whitelisted_categories or source_channel.category.id not in whitelisted_categories:
                return
                
            # Get the message
            message = await source_channel.fetch_message(payload.message_id)
            if not message or not message.embeds:
                return
                
            # Get the forward channel
            forward_channel = bot.get_channel(REACTION_CONFIG["FORWARD_CHANNEL_ID"])
            if not forward_channel:
                logger.error(f"Could not find forward channel {REACTION_CONFIG['FORWARD_CHANNEL_ID']}")
                return
                
            # Forward the embeds
            logger.info(f"Forwarding {len(message.embeds)} embeds from message {message.id} to {forward_channel.name}")
            for embed in message.embeds:
                new_embed = discord.Embed.from_dict(embed.to_dict())
                new_embed.add_field(
                    name="Source",
                    value=f"[Jump to message]({message.jump_url})"
                )
                await forward_channel.send(embed=new_embed)
                
            logger.info(f"Successfully forwarded {len(message.embeds)} embeds to {forward_channel.name}")
            
        except Exception as e:
            logger.error(f"Error forwarding message {payload.message_id}: {e}", exc_info=True)

async def teardown(bot):
    """Clean up the reaction module."""
    logger.info("Reaction module teardown complete") 