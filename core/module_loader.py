"""
Module Loader

This module handles the dynamic loading and management of bot modules.
While being phased out in favor of a cog-based architecture,
it remains critical for legacy module support.

The Module Loader is responsible for:
1. Discovering and loading modules dynamically
2. Managing module lifecycle (setup/teardown)
3. Handling module dependencies and configuration
4. Preventing command registration conflicts

Critical:
- Modules must follow the standard interface (setup/teardown)
- Configuration must be loaded before module initialization
- Module dependencies must be properly resolved
- Command registration must avoid duplicates

Classes:
    ModuleLoader: Main class for managing bot modules
"""

import os
import importlib
import logging
import inspect
from config.core.settings import settings
from config.core.settings_manager import get_manager

logger = logging.getLogger('discord_bot.module_loader')

class ModuleLoader:
    """
    Manages the dynamic loading and lifecycle of bot modules.
    
    This class handles:
    - Module discovery and initialization
    - Configuration management and validation
    - Command registration and deregistration
    - Module lifecycle events (setup/teardown)
    
    While being phased out for cogs, it remains essential for:
    - Legacy module support
    - Complex module interactions
    - Custom module behaviors
    - Dynamic module loading
    
    Attributes:
        loaded_modules (dict): Maps module names to their instances
        registered_commands (set): Tracks registered command names
        
    Critical:
        - Modules must implement setup/teardown methods
        - Configuration must be valid before loading
        - Dependencies must be available
        - Command names must be unique
    """
    
    def __init__(self):
        """
        Initialize the module loader system.
        
        Sets up:
        - Module tracking collections
        - Command registration tracking
        - Configuration management
        
        Note:
            This class is deprecated and will be replaced by cogs
            in future versions.
        """
        self.loaded_modules = {}
        self.registered_commands = set()
        logger.warning("ModuleLoader is deprecated and will be removed in future versions. Use cogs instead.")
    
    def discover_modules(self):
        """
        Discover available modules in the modules directory.
        
        This method:
        1. Checks the modules directory
        2. Identifies valid module structures
        3. Filters based on enabled modules
        4. Validates module requirements
        
        Returns:
            list: Names of discovered and enabled modules
            
        Note:
            Modules must have a module.py file and be listed
            in ENABLED_MODULES to be discovered.
        """
        modules = []
        
        modules_dir = settings.MODULES_PATH
        
        if not os.path.isdir(modules_dir):
            logger.error(f"Modules directory '{modules_dir}' not found")
            return modules
        
        for item in os.listdir(modules_dir):
            item_path = os.path.join(modules_dir, item)
            
            if os.path.isdir(item_path) and os.path.isfile(os.path.join(item_path, 'module.py')):
                if item in settings.ENABLED_MODULES:
                    modules.append(item)
                    logger.debug(f"Discovered module: {item}")
                else:
                    logger.debug(f"Module {item} is disabled in settings")
        
        return modules
    
    def load_module(self, bot, module_name):
        """
        Load a module and register its commands.
        
        This method:
        1. Imports the module package
        2. Validates module structure
        3. Handles configuration setup
        4. Executes module setup
        5. Tracks command registration
        
        Args:
            bot (discord.Client): The Discord bot instance
            module_name (str): Name of the module to load
            
        Returns:
            bool: True if module loaded successfully
            
        Note:
            Special handling exists for certain modules (e.g. redeye)
            that require specific configuration setup.
        """
        try:
            module_path = f"{settings.MODULES_PATH}.{module_name}.module"
            logger.debug(f"Attempting to import module from {module_path}")
            
            # Handle special module configurations
            if module_name == 'redeye':
                if not self._setup_redeye_config(module_name):
                    return False
            
            # Import and validate module
            try:
                module = importlib.import_module(module_path)
                logger.debug(f"Successfully imported module: {module_name}")
            except ImportError as e:
                self._diagnose_import_failure(module_name, e)
                return False
            
            # Validate and execute setup
            if hasattr(module, 'setup') and inspect.isfunction(module.setup):
                logger.debug(f"Found setup function in module: {module_name}")
                
                existing_commands = set(cmd.name for cmd in bot.tree.get_commands())
                
                try:
                    logger.debug(f"Calling setup function for module: {module_name}")
                    
                    try:
                        module.setup(bot, registered_commands=self.registered_commands)
                    except TypeError:
                        module.setup(bot)
                    
                    logger.debug(f"Successfully called setup function for module: {module_name}")
                except Exception as e:
                    logger.error(f"Error in setup function for module {module_name}: {str(e)}")
                    import traceback
                    logger.error(f"Exception traceback: {traceback.format_exc()}")
                    return False
                
                # Track new commands
                new_commands = set(cmd.name for cmd in bot.tree.get_commands()) - existing_commands
                self.registered_commands.update(new_commands)
                
                logger.info(f"Loaded module: {module_name} with {len(new_commands)} new commands")
                
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
        Reload an existing module.
        
        This method:
        1. Executes module teardown if available
        2. Reloads the module package
        3. Re-initializes the module
        4. Updates command registration
        
        Args:
            bot (discord.Client): The Discord bot instance
            module_name (str): Name of the module to reload
            
        Returns:
            bool: True if module reloaded successfully
            
        Note:
            This is useful for updating module code without
            restarting the bot.
        """
        try:
            if module_name not in self.loaded_modules:
                logger.warning(f"Module {module_name} is not loaded")
                return False
            
            module = self.loaded_modules[module_name]
            
            if hasattr(module, 'teardown') and inspect.isfunction(module.teardown):
                try:
                    module.teardown(bot)
                except Exception as e:
                    logger.error(f"Error in teardown for module {module_name}: {str(e)}")
                    return False
            
            # Remove from loaded modules
            del self.loaded_modules[module_name]
            
            # Reload the module
            return self.load_module(bot, module_name)
        except Exception as e:
            logger.error(f"Error reloading module {module_name}: {str(e)}")
            return False
    
    def _setup_redeye_config(self, module_name):
        """
        Set up configuration for the redeye module.
        
        This method:
        1. Attempts to import existing config
        2. Creates minimal config if needed
        3. Initializes settings manager
        
        Args:
            module_name (str): Name of the module (should be 'redeye')
            
        Returns:
            bool: True if configuration setup successful
            
        Note:
            This is a private helper method for handling
            redeye module's special configuration needs.
        """
        try:
            try:
                config_module = importlib.import_module(f"config.{module_name}_config")
                logger.debug(f"Successfully imported {module_name}_config module")
            except ImportError as e:
                logger.error(f"Could not import {module_name}_config, will create a minimal version: {e}")
                
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
                
                settings_manager = get_manager(module_name, DEFAULT_CONFIG)
                
                import sys
                import types
                config_module = types.ModuleType(f'config.{module_name}_config')
                config_module.settings_manager = settings_manager
                sys.modules[f'config.{module_name}_config'] = config_module
                logger.info(f"Created minimal {module_name}_config module")
                
            return True
        except Exception as e:
            logger.error(f"Error setting up configuration for {module_name}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def _diagnose_import_failure(self, module_name, error):
        """
        Diagnose module import failures.
        
        This method:
        1. Checks parent module existence
        2. Verifies submodule structure
        3. Validates module.py presence
        
        Args:
            module_name (str): Name of the failed module
            error (Exception): The import error
            
        Note:
            This is a private helper method for providing
            detailed import failure diagnostics.
        """
        try:
            parent_module = importlib.import_module(settings.MODULES_PATH)
            logger.debug(f"Parent module exists: {parent_module}")
            
            try:
                submodule = importlib.import_module(f"{settings.MODULES_PATH}.{module_name}")
                logger.debug(f"Submodule exists: {submodule}")
                logger.error(f"Module {module_name} was found but module.py could not be imported")
            except ImportError:
                logger.error(f"Submodule {module_name} does not exist or could not be imported")
        except ImportError:
            logger.error(f"Parent module {settings.MODULES_PATH} does not exist or could not be imported") 