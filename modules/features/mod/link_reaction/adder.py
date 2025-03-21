"""
LuisaViaRoma PID Adder Functionality

This module provides functionality for adding PIDs to the LuisaViaRoma tracking file.
"""

import os
import logging
from config.features.reactions import link as link_reaction_config

logger = logging.getLogger('discord_bot.modules.mod.link_reaction.adder')

async def add_pid_to_file(pid, channel=None):
    """
    Add a PID to the configured LuisaViaRoma file
    
    Args:
        pid: The product ID to add
        channel: Optional Discord channel to send result messages to
    
    Returns:
        bool: True if the PID was added, False otherwise
        str: Message describing the result
    """
    # Get LuisaViaRoma store configuration
    stores = link_reaction_config.settings_manager.get("STORES", {})
    
    # Check if we're using the new dictionary format or legacy list format
    store_config = None
    
    if isinstance(stores, dict):
        # Dictionary format (new)
        store_config = stores.get("luisaviaroma", {})
    elif isinstance(stores, list):
        # List format (legacy)
        for store in stores:
            if isinstance(store, dict) and store.get('name', '').lower() == "luisaviaroma":
                store_config = store
                break
    
    if not store_config:
        message = "❌ LuisaViaRoma store not configured."
        logger.error(message)
        return False, message
    
    # Get file path from store configuration
    file_path = store_config.get('file_path')
    
    if not file_path:
        message = "❌ LuisaViaRoma file path not configured."
        logger.error(message)
        return False, message
    
    # Create directory if it doesn't exist
    try:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    except Exception as e:
        message = f"❌ Error creating directory: {str(e)}"
        logger.error(message)
        return False, message
    
    # Check if file exists and if PID is already in the file
    existing_pids = set()
    needs_newline = False
    file_empty = True
    
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            with open(file_path, "r") as f:
                # Read all existing PIDs
                existing_content = f.read()
                existing_pids = {line.strip() for line in existing_content.splitlines() if line.strip()}
                
                # Check if file ends with newline
                needs_newline = not existing_content.endswith('\n')
                file_empty = not existing_content.strip()
                
                logger.debug(f"Found {len(existing_pids)} existing PIDs in file")
        except Exception as e:
            message = f"❌ Error reading file: {str(e)}"
            logger.error(message)
            return False, message
    
    # Check if PID already exists in the file
    pid = pid.strip()
    if pid in existing_pids:
        message = f"ℹ️ Product ID `{pid}` already exists in LuisaViaRoma tracking list."
        logger.info(message)
        return False, message
    
    # Append the PID to the file
    try:
        with open(file_path, "a") as f:
            if needs_newline:
                f.write(f"\n{pid}\n")
                logger.info(f"Added newline before writing PID")
            elif file_empty:
                f.write(f"{pid}\n")
            else:
                f.write(f"{pid}\n")
        
        message = f"✅ Added product ID `{pid}` to LuisaViaRoma tracking list."
        logger.info(message)
        return True, message
    except Exception as e:
        message = f"❌ Error writing to file: {str(e)}"
        logger.error(message)
        return False, message 