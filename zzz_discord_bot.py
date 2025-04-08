"""
path: discord_bot.py
purpose: Main bot initialization and setup
critical:
- Initializes the Discord bot
- Loads enabled modules
- Sets up error handling
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
import discord
from discord.ext import commands
from dotenv import load_dotenv
from core.error_handler import ErrorHandler, ConfigurationError

# Load environment variables
load_dotenv()

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            'logs/discord_bot.log',
            maxBytes=5*1024*1024,  # 5MB
            backupCount=5
        ),
        logging.StreamHandler(sys.stdout)
    ]
)

# Set discord.py's logger to INFO to avoid excessive debug messages
discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)

# Validate required environment variables
def validate_env():
    """Validate required environment variables."""
    required_vars = {
        'DISCORD_TOKEN': os.getenv('DISCORD_TOKEN'),
        'APPLICATION_ID': os.getenv('APPLICATION_ID')
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        error_msg = (
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            "Please check your .env file and ensure all required variables are set."
        )
        logger.error(error_msg)
        raise ConfigurationError(error_msg)
        
    return required_vars

# Bot configuration
try:
    env_vars = validate_env()
    DISCORD_TOKEN = env_vars['DISCORD_TOKEN']
    APPLICATION_ID = env_vars['APPLICATION_ID']
    GUILD_IDS = [int(id) for id in os.getenv('GUILD_IDS', '').split(',') if id]
    ENABLED_MODULES = os.getenv('ENABLED_MODULES', 'mod,online').split(',')
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    sys.exit(1)

class DiscordBot(commands.Bot):
    """Custom Discord bot class."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',  # Fallback prefix for message commands
            intents=intents,
            application_id=APPLICATION_ID
        )
        
        # Initialize error handler
        self.error_handler = ErrorHandler(self)
        
    async def setup_hook(self):
        """Set up the bot's modules and sync commands."""
        # Load enabled modules
        registered_commands = set()
        
        # Clear all existing commands first
        self.tree.clear_commands(guild=None)  # Clear global commands
        for guild_id in GUILD_IDS:
            guild = discord.Object(id=guild_id)
            self.tree.clear_commands(guild=guild)
        
        # Load enabled modules
        for module_name in ENABLED_MODULES:
            try:
                # Check if module is in features directory
                if module_name in ['redeye', 'instore', 'online']:
                    module = __import__(f"modules.features.{module_name}", fromlist=["setup"])
                else:
                    module = __import__(f"modules.{module_name}", fromlist=["setup"])
                if hasattr(module, "setup"):
                    registered_commands = await module.setup(self, registered_commands)
                    logger.info(f"Loaded module: {module_name}")
            except Exception as e:
                logger.error(f"Error loading module {module_name}: {e}")
                
        # Sync commands to development guilds
        for guild_id in GUILD_IDS:
            try:
                guild = discord.Object(id=guild_id)
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                logger.info(f"Synced commands to development guild: {guild_id}")
                
                # Log all synced commands and their structure
                logger.info("=== Synced Command Structure ===")
                for cmd in self.tree.get_commands(guild=guild):
                    logger.info(f"Command: /{cmd.name}")
                    if hasattr(cmd, 'commands'):  # Group command
                        for subcmd in cmd.commands:
                            logger.info(f"  ├─ /{cmd.name} {subcmd.name}")
                            if hasattr(subcmd, 'commands'):  # Nested group
                                for nested_cmd in subcmd.commands:
                                    logger.info(f"  │  └─ /{cmd.name} {subcmd.name} {nested_cmd.name}")
                logger.info("===============================")
            except Exception as e:
                logger.error(f"Error syncing commands to guild {guild_id}: {e}")
                
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"Logged in as {self.user} ({self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")

def main():
    """Main entry point for the bot."""
    try:
        bot = DiscordBot()
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 