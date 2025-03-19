"""
Module Loader (Legacy)

This module handles the dynamic loading of bot modules.
It is being phased out in favor of a cog-based architecture.
"""

import os
import importlib
import logging
import inspect
from config import settings

logger = logging.getLogger('discord_bot.module_loader')

class ModuleLoader:
    """
    Handles the discovery and loading of bot modules.
    
    NOTE: This class is being phased out in favor of a cog-based architecture.
    New modules should be implemented as cogs and loaded via bot.load_extension.
    """
    
    def __init__(self):
        """
        Initialize the module loader.
        """
        self.loaded_modules = {}
        self.registered_commands = set()  # Track registered command names
        logger.warning("ModuleLoader is deprecated and will be removed in future versions. Use cogs instead.")
    
    def discover_modules(self):
        """
        Discover available modules in the modules directory.
        
        Returns:
            list: List of module names
        """
        modules = []
        
        # Get the modules directory
        modules_dir = settings.MODULES_PATH
        
        # Check if the directory exists
        if not os.path.isdir(modules_dir):
            logger.error(f"Modules directory '{modules_dir}' not found")
            return modules
        
        # Get all subdirectories in the modules directory
        for item in os.listdir(modules_dir):
            item_path = os.path.join(modules_dir, item)
            
            # Check if it's a directory and has a module.py file
            if os.path.isdir(item_path) and os.path.isfile(os.path.join(item_path, 'module.py')):
                # Check if the module is enabled
                if item in settings.ENABLED_MODULES:
                    modules.append(item)
                    logger.debug(f"Discovered module: {item}")
                else:
                    logger.debug(f"Module {item} is disabled in settings")
        
        return modules
    
    def load_module(self, bot, module_name):
        """
        Load a module and register its commands with the bot.
        
        Args:
            bot: The Discord bot instance
            module_name (str): The name of the module to load
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Import the module
            module_path = f"{settings.MODULES_PATH}.{module_name}.module"
            module = importlib.import_module(module_path)
            
            # Check if the module has a setup function
            if hasattr(module, 'setup') and inspect.isfunction(module.setup):
                # Get existing commands before setup
                existing_commands = set(cmd.name for cmd in bot.tree.get_commands())
                
                # Call the setup function with our registered commands to avoid duplicates
                try:
                    # Try to pass registered_commands as an argument
                    module.setup(bot, registered_commands=self.registered_commands)
                except TypeError:
                    # If that fails, call the original setup function
                    module.setup(bot)
                
                # Get new commands after setup
                new_commands = set(cmd.name for cmd in bot.tree.get_commands()) - existing_commands
                
                # Update our registered commands set
                self.registered_commands.update(new_commands)
                
                logger.info(f"Loaded module: {module_name} with {len(new_commands)} new commands")
                
                # Store the loaded module
                self.loaded_modules[module_name] = module
                
                return True
            else:
                logger.error(f"Module {module_name} does not have a setup function")
                return False
        except Exception as e:
            logger.error(f"Error loading module {module_name}: {str(e)}")
            return False
    
    def reload_module(self, bot, module_name):
        """
        Reload a module.
        
        Args:
            bot: The Discord bot instance
            module_name (str): The name of the module to reload
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if the module is loaded
            if module_name not in self.loaded_modules:
                logger.warning(f"Module {module_name} is not loaded")
                return False
            
            # Get the module
            module = self.loaded_modules[module_name]
            
            # Check if the module has a teardown function
            if hasattr(module, 'teardown') and inspect.isfunction(module.teardown):
                # Call the teardown function
                module.teardown(bot)
            
            # Get existing commands before reload
            existing_commands = set(cmd.name for cmd in bot.tree.get_commands())
            
            # Reload the module
            module_path = f"{settings.MODULES_PATH}.{module_name}.module"
            reloaded_module = importlib.reload(importlib.import_module(module_path))
            
            # Check if the reloaded module has a setup function
            if hasattr(reloaded_module, 'setup') and inspect.isfunction(reloaded_module.setup):
                # Call the setup function with our registered commands to avoid duplicates
                try:
                    # Try to pass registered_commands as an argument
                    reloaded_module.setup(bot, registered_commands=self.registered_commands)
                except TypeError:
                    # If that fails, call the original setup function
                    reloaded_module.setup(bot)
                
                # Get new commands after reload
                new_commands = set(cmd.name for cmd in bot.tree.get_commands()) - existing_commands
                
                # Update our registered commands set
                self.registered_commands.update(new_commands)
                
                logger.info(f"Reloaded module: {module_name} with {len(new_commands)} new commands")
                
                # Update the loaded module
                self.loaded_modules[module_name] = reloaded_module
                
                return True
            else:
                logger.error(f"Reloaded module {module_name} does not have a setup function")
                return False
        except Exception as e:
            logger.error(f"Error reloading module {module_name}: {str(e)}")
            return False 