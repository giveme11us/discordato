#!/usr/bin/env python3
"""
Pinger Test Script

This script helps diagnose issues with the pinger feature
by verifying the notification channel and permissions.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

import discord
from discord.ext import commands

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pinger_test')

# Load environment variables
load_dotenv()

# Get Discord token
token = os.getenv('DISCORD_BOT_TOKEN')
if not token:
    logger.error("No Discord token found. Set DISCORD_BOT_TOKEN in .env file.")
    exit(1)

# Get notification channel ID
notification_channel_id = os.getenv('PINGER_NOTIFICATION_CHANNEL_ID')
if not notification_channel_id:
    logger.error("No notification channel ID found. Set PINGER_NOTIFICATION_CHANNEL_ID in .env file.")
    exit(1)

try:
    notification_channel_id = int(notification_channel_id)
except ValueError:
    logger.error(f"Invalid notification channel ID: {notification_channel_id}")
    exit(1)

# Create bot instance with necessary intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    logger.info(f"Bot {bot.user.name} is ready")
    
    # Test notification channel
    logger.info(f"Testing notification channel with ID: {notification_channel_id}")
    
    # Try to find notification channel across all guilds
    notification_channel = None
    for guild in bot.guilds:
        logger.info(f"Searching in guild: {guild.name} (ID: {guild.id})")
        
        # List all channels in the guild
        for channel in guild.channels:
            logger.info(f"  Channel: {channel.name} (ID: {channel.id}, Type: {channel.type})")
        
        channel = guild.get_channel(notification_channel_id)
        if channel:
            notification_channel = channel
            logger.info(f"Found notification channel: {notification_channel.name} in guild {guild.name}")
            break
    
    if not notification_channel:
        logger.error(f"Could not find notification channel with ID {notification_channel_id} in any guild")
        
        # Check if the ID is valid by trying to fetch it directly
        try:
            channel = await bot.fetch_channel(notification_channel_id)
            logger.info(f"Found channel via fetch_channel: {channel.name} (ID: {channel.id})")
            notification_channel = channel
        except Exception as e:
            logger.error(f"Error fetching channel: {str(e)}")
            await bot.close()
            return
    
    # Check permissions in the notification channel
    permissions = notification_channel.permissions_for(notification_channel.guild.me)
    logger.info(f"Bot permissions in notification channel:")
    logger.info(f"  view_channel: {permissions.view_channel}")
    logger.info(f"  send_messages: {permissions.send_messages}")
    logger.info(f"  embed_links: {permissions.embed_links}")
    logger.info(f"  attach_files: {permissions.attach_files}")
    
    # Try to send a test message
    logger.info("Attempting to send a test message")
    try:
        embed = discord.Embed(
            title="Pinger Test",
            description="This is a test message to verify the pinger notification channel is working",
            color=0xF94144
        )
        
        # Create a test button
        view = discord.ui.View()
        button = discord.ui.Button(
            style=discord.ButtonStyle.link,
            label="Test Button",
            url="https://discord.com"
        )
        view.add_item(button)
        
        await notification_channel.send(embed=embed, view=view)
        logger.info("Test message sent successfully")
    except Exception as e:
        logger.error(f"Error sending test message: {str(e)}")
    
    # Close the bot
    await bot.close()

async def main():
    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 