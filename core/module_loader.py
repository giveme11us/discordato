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
            logger.debug(f"Attempting to import module from {module_path}")
            
            # Pre-check: If the module is redeye, ensure its configuration exists
            if module_name == 'redeye':
                try:
                    # Try to import the config
                    import importlib
                    try:
                        config_module = importlib.import_module(f"config.{module_name}_config")
                        logger.debug(f"Successfully imported {module_name}_config module")
                    except ImportError as e:
                        logger.error(f"Could not import {module_name}_config, will create a minimal version: {e}")
                        
                        # Create a minimal config module dynamically if it doesn't exist
                        from config.settings_manager import get_manager
                        # Define minimal default config
                        DEFAULT_CONFIG = {
                            "ENABLED": False,
                            "WAITLISTS": {},
                            "ROLE_REQUIREMENTS": {},
                            "NOTIFICATION_CHANNEL_ID": None,
                            "STATUS_EMOJIS": {
                                "WAITING": "⏳",
                                "APPROVED": "✅",
                                "DENIED": "❌",
                                "EXPIRED": "⌛"
                            }
                        }
                        
                        # Create the settings manager
                        settings_manager = get_manager(module_name, DEFAULT_CONFIG)
                        
                        # Create a temporary module
                        import sys
                        import types
                        config_module = types.ModuleType(f'config.{module_name}_config')
                        config_module.settings_manager = settings_manager
                        sys.modules[f'config.{module_name}_config'] = config_module
                        logger.info(f"Created minimal {module_name}_config module")
                        
                except Exception as e:
                    logger.error(f"Error setting up configuration for {module_name}: {e}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    return False
            
            try:
                module = importlib.import_module(module_path)
                logger.debug(f"Successfully imported module: {module_name}")
            except ImportError as e:
                logger.error(f"Import error loading module {module_name}: {str(e)}")
                # Try to diagnose what part of the import failed
                try:
                    parent_module = importlib.import_module(settings.MODULES_PATH)
                    logger.debug(f"Parent module exists: {parent_module}")
                    
                    try:
                        submodule = importlib.import_module(f"{settings.MODULES_PATH}.{module_name}")
                        logger.debug(f"Submodule exists: {submodule}")
                        
                        # The issue might be with the module.py file itself
                        logger.error(f"Module {module_name} was found but module.py could not be imported")
                    except ImportError:
                        logger.error(f"Submodule {module_name} does not exist or could not be imported")
                except ImportError:
                    logger.error(f"Parent module {settings.MODULES_PATH} does not exist or could not be imported")
                return False
            
            # Check if the module has a setup function
            if hasattr(module, 'setup') and inspect.isfunction(module.setup):
                logger.debug(f"Found setup function in module: {module_name}")
                
                # Get existing commands before setup
                existing_commands = set(cmd.name for cmd in bot.tree.get_commands())
                
                # Call the setup function with our registered commands to avoid duplicates
                try:
                    logger.debug(f"Calling setup function for module: {module_name}")
                    
                    # Try to pass registered_commands as an argument
                    try:
                        module.setup(bot, registered_commands=self.registered_commands)
                    except TypeError:
                        # If that fails, call the original setup function
                        module.setup(bot)
                    
                    logger.debug(f"Successfully called setup function for module: {module_name}")
                except Exception as e:
                    logger.error(f"Error in setup function for module {module_name}: {str(e)}")
                    import traceback
                    logger.error(f"Exception traceback: {traceback.format_exc()}")
                    return False
                
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
            import traceback
            logger.error(f"Exception traceback: {traceback.format_exc()}")
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