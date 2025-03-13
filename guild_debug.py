"""
Guild Debug Script

This script helps diagnose issues with guild access in Discord bots.
It verifies that a specific guild ID can be accessed correctly.
"""

import os
import sys
import discord
import logging
import asyncio
from dotenv import load_dotenv
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('guild_debug')

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GUILD_IDS_RAW = os.getenv('GUILD_IDS', '')
logger.info(f"Raw GUILD_IDS from .env: '{GUILD_IDS_RAW}'")

# Parse guild IDs, handling various formats
GUILD_IDS = []
if GUILD_IDS_RAW:
    # Handle comma-separated list
    if ',' in GUILD_IDS_RAW:
        GUILD_IDS = [gid.strip() for gid in GUILD_IDS_RAW.split(',') if gid.strip()]
    else:
        # Handle single value
        GUILD_IDS = [GUILD_IDS_RAW.strip()]

logger.info(f"Parsed GUILD_IDS: {GUILD_IDS}")

# GUILD_IDS = os.getenv('GUILD_IDS', '').split(',')
# TARGET_GUILD_ID = '1347333602794541066'  # The guild ID that's causing issues

class DebugClient(discord.Client):
    def __init__(self):
        # Enable all intents to ensure we have full access to guild data
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        
    async def on_ready(self):
        logger.info(f'Bot connected as {self.user} (ID: {self.user.id})')
        
        # Check all guilds the bot is in
        logger.info(f'Bot is in {len(self.guilds)} guilds:')
        for guild in self.guilds:
            logger.info(f'  - {guild.name} (ID: {guild.id})')
            # Save the guild ID for comparison
            with open('guild_ids.txt', 'a') as f:
                f.write(f"{guild.name}: {guild.id}\n")
        
        # If the bot is not in any guilds, show invite link
        if not self.guilds:
            permissions = discord.Permissions(
                send_messages=True,
                read_messages=True,
                read_message_history=True,
                manage_messages=True,
                view_channel=True,
                manage_webhooks=True,
                embed_links=True,
                attach_files=True,
                manage_guild=True  # Important for command registration
            )
            
            # Generate a bot invite link with proper permissions
            invite_link = discord.utils.oauth_url(
                self.user.id,
                permissions=permissions,
                scopes=("bot", "applications.commands")
            )
            
            logger.warning(f"Bot is not in any guilds! Use this link to invite the bot:")
            logger.warning(f"{invite_link}")
            
        # Try to find guilds from .env configuration
        for guild_id in GUILD_IDS:
            if guild_id and guild_id.strip():
                logger.info(f'Checking guild ID from configuration: {guild_id}')
                
                try:
                    guild_id_int = int(guild_id)
                    # Try to get from cache
                    guild = self.get_guild(guild_id_int)
                    if guild:
                        logger.info(f'Found guild in cache: {guild.name} (ID: {guild.id})')
                        
                        # Check bot's permissions
                        bot_member = guild.get_member(self.user.id)
                        if bot_member:
                            logger.info(f'Bot\'s roles in the guild: {[role.name for role in bot_member.roles]}')
                            permissions = bot_member.guild_permissions
                            logger.info(f'Bot has administrator permission: {permissions.administrator}')
                            logger.info(f'Bot has manage_guild permission: {permissions.manage_guild}')
                        else:
                            logger.warning(f'Bot not found as a member in the guild!')
                    else:
                        logger.warning(f'Guild with ID {guild_id} not found in cache!')
                        
                        # Try to fetch from API
                        try:
                            fetched_guild = await self.fetch_guild(guild_id_int)
                            logger.info(f'Successfully fetched guild from API: {fetched_guild.name}')
                        except discord.errors.Forbidden:
                            logger.error(f'Permission denied when fetching guild with ID {guild_id} (Forbidden error)')
                        except discord.errors.NotFound:
                            logger.error(f'Guild not found when fetching from API with ID {guild_id} (NotFound error)')
                        except Exception as e:
                            logger.error(f'Error fetching guild with ID {guild_id}: {type(e).__name__}: {str(e)}')
                except ValueError:
                    logger.error(f'Invalid guild ID format: {guild_id}')
                except Exception as e:
                    logger.error(f'Error processing guild ID {guild_id}: {type(e).__name__}: {str(e)}')
                    
        logger.info("======= ENVIRONMENT VARIABLES =======")
        for key, value in os.environ.items():
            if key.startswith('DISCORD_') or key.startswith('GUILD_'):
                # Mask token for security
                if 'TOKEN' in key:
                    masked_value = value[:10] + '...' if value else None
                    logger.info(f'{key}: {masked_value}')
                else:
                    logger.info(f'{key}: {value}')
                    
        # Check DEV_GUILD_ID too
        dev_guild_id = os.getenv('DEV_GUILD_ID', '').strip()
        if dev_guild_id:
            logger.info(f'Checking DEV_GUILD_ID: {dev_guild_id}')
            try:
                dev_guild_id_int = int(dev_guild_id)
                dev_guild = self.get_guild(dev_guild_id_int)
                if dev_guild:
                    logger.info(f'Found DEV guild in cache: {dev_guild.name} (ID: {dev_guild.id})')
                else:
                    logger.warning(f'DEV_GUILD_ID {dev_guild_id} not found in cache!')
            except ValueError:
                logger.error(f'Invalid DEV_GUILD_ID format: {dev_guild_id}')
                
        # Exit when diagnostics are complete
        await self.close()

async def main():
    client = DebugClient()
    
    # Exit if token is missing
    if not TOKEN:
        logger.error('No Discord token found. Make sure DISCORD_BOT_TOKEN is set in your .env file.')
        return
    
    # Print bot invite link even before connecting
    permissions = discord.Permissions(
        send_messages=True,
        read_messages=True,
        read_message_history=True,
        manage_messages=True,
        view_channel=True,
        manage_webhooks=True,
        embed_links=True,
        attach_files=True,
        manage_guild=True  # Important for command registration
    )
    
    # Get application ID from .env if available, otherwise use a placeholder
    application_id = os.getenv('DISCORD_APPLICATION_ID', 'YOUR_APPLICATION_ID')
    
    # Generate a bot invite link with proper permissions
    invite_link = discord.utils.oauth_url(
        application_id,
        permissions=permissions,
        scopes=("bot", "applications.commands")
    )
    
    logger.info("=== BOT INVITE LINK ===")
    logger.info(f"{invite_link}")
    logger.info("Use this link to invite the bot to your server")
    logger.info("========================")
    
    # Connect to Discord
    try:
        await client.start(TOKEN)
    except discord.errors.LoginFailure:
        logger.error('Failed to login to Discord. Check if your token is valid.')
    except Exception as e:
        logger.error(f'Error running client: {type(e).__name__}: {str(e)}')

if __name__ == '__main__':
    asyncio.run(main()) 