#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initialize Settings

This script initializes default settings for all modules.
Instead of using the properties API which might have issues,
it directly writes the default settings to JSON files.
"""

import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('initialize_settings')

# Import default configurations
from config.keyword_filter_config import DEFAULT_CONFIG as KEYWORD_FILTER_DEFAULT
from config.link_reaction_config import DEFAULT_CONFIG as LINK_REACTION_DEFAULT
from config.reaction_forward_config import DEFAULT_CONFIG as REACTION_FORWARD_DEFAULT
from config.pinger_config import DEFAULT_CONFIG as PINGER_DEFAULT

# Settings directory
SETTINGS_DIR = os.path.join('data', 'settings')

# Module settings to initialize
MODULE_SETTINGS = {
    'keyword_filter': KEYWORD_FILTER_DEFAULT,
    'link_reaction': LINK_REACTION_DEFAULT,
    'reaction_forward': REACTION_FORWARD_DEFAULT,
    'pinger': PINGER_DEFAULT
}

def initialize_settings():
    """Initialize default settings for all modules."""
    logger.info("Initializing default settings...")
    
    # Create settings directory if it doesn't exist
    os.makedirs(SETTINGS_DIR, exist_ok=True)
    logger.info(f"Settings directory: {SETTINGS_DIR}")
    
    # Initialize each module's settings
    for module_name, default_settings in MODULE_SETTINGS.items():
        settings_file = os.path.join(SETTINGS_DIR, f"{module_name}.json")
        
        try:
            # Make any necessary modifications to sets/iterables for JSON serialization
            serializable_settings = prepare_for_serialization(default_settings)
            
            # Write settings to file
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_settings, f, indent=2)
                
            logger.info(f"Initialized settings for {module_name}")
        except Exception as e:
            logger.error(f"Error initializing settings for {module_name}: {e}")

def prepare_for_serialization(settings):
    """
    Prepare settings for JSON serialization by converting non-serializable types
    (like sets) to serializable ones (like lists).
    
    Args:
        settings: Settings dictionary
        
    Returns:
        Dictionary with serializable values
    """
    result = {}
    
    for key, value in settings.items():
        if isinstance(value, set):
            # Convert sets to lists
            result[key] = list(value)
        elif isinstance(value, dict):
            # Recursively process nested dictionaries
            result[key] = prepare_for_serialization(value)
        else:
            # Keep other values as-is
            result[key] = value
            
    return result

if __name__ == "__main__":
    initialize_settings()
    logger.info("Settings initialization complete!") 