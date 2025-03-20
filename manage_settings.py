#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Settings Management Script

This script provides utilities for managing settings:
- Exporting all settings to a single file
- Importing settings from a file
- Validating settings structure
- Listing current settings
"""

import os
import sys
import json
import argparse
import logging
from dotenv import load_dotenv
from typing import Dict, Any, List
from config.features.moderation import filter as keyword_filter_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('manage_settings')

# Load environment variables
load_dotenv()

# Directory where settings are stored
SETTINGS_DIR = os.path.join('data', 'settings')

# Modules with settings
MODULES = [
    'keyword_filter',
    'link_reaction',
    'reaction_forward',
    'pinger'
]

def export_settings(output_file: str) -> bool:
    """
    Export all settings to a single JSON file.
    
    Args:
        output_file: Path to the output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create a dictionary to hold all settings
        all_settings = {}
        
        # Load settings for each module
        for module in MODULES:
            settings_file = os.path.join(SETTINGS_DIR, f"{module}.json")
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    module_settings = json.load(f)
                    all_settings[module] = module_settings
            else:
                logger.warning(f"Settings file for {module} not found")
                all_settings[module] = {}
        
        # Write all settings to the output file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_settings, f, indent=2)
            
        logger.info(f"Exported settings to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error exporting settings: {e}")
        return False

def import_settings(input_file: str, module: str = None) -> bool:
    """
    Import settings from a JSON file.
    
    Args:
        input_file: Path to the input file
        module: Optional module name to import only specific settings
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read settings from input file
        with open(input_file, 'r', encoding='utf-8') as f:
            imported_settings = json.load(f)
        
        # Determine which modules to import
        if module:
            if module not in imported_settings:
                logger.error(f"Module {module} not found in imported settings")
                return False
            modules_to_import = [module]
        else:
            modules_to_import = list(imported_settings.keys())
        
        # Import settings for each module
        for module_name in modules_to_import:
            if module_name not in MODULES:
                logger.warning(f"Unknown module: {module_name}, skipping")
                continue
                
            settings_file = os.path.join(SETTINGS_DIR, f"{module_name}.json")
            
            # Check if settings file exists
            if os.path.exists(settings_file):
                # Backup existing settings
                backup_file = f"{settings_file}.bak"
                os.rename(settings_file, backup_file)
                logger.info(f"Backed up {settings_file} to {backup_file}")
            
            # Write new settings
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(imported_settings[module_name], f, indent=2)
                
            logger.info(f"Imported settings for {module_name}")
        
        return True
    except Exception as e:
        logger.error(f"Error importing settings: {e}")
        return False

def list_settings(module: str = None) -> None:
    """
    List current settings.
    
    Args:
        module: Optional module name to list only specific settings
    """
    try:
        # Determine which modules to list
        modules_to_list = [module] if module else MODULES
        
        # List settings for each module
        for module_name in modules_to_list:
            if module_name not in MODULES:
                logger.warning(f"Unknown module: {module_name}, skipping")
                continue
                
            settings_file = os.path.join(SETTINGS_DIR, f"{module_name}.json")
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    module_settings = json.load(f)
                
                print(f"\n=== {module_name.upper()} ===")
                print(json.dumps(module_settings, indent=2))
            else:
                print(f"\n=== {module_name.upper()} ===")
                print("No settings file found.")
    except Exception as e:
        logger.error(f"Error listing settings: {e}")

def validate_settings() -> None:
    """
    Validate settings structure for all modules.
    """
    try:
        # Import config modules to use their default settings as schema
        import config.link_reaction_config as link_reaction_config
        import config.reaction_forward_config as reaction_forward_config
        import config.pinger_config as pinger_config
        
        # Validate settings for each module
        for module in MODULES:
            settings_file = os.path.join(SETTINGS_DIR, f"{module}.json")
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    module_settings = json.load(f)
                
                # Get the default settings for this module
                default_settings = {
                    'keyword_filter': keyword_filter_config.DEFAULT_CONFIG,
                    'link_reaction': link_reaction_config.DEFAULT_CONFIG,
                    'reaction_forward': reaction_forward_config.DEFAULT_CONFIG,
                    'pinger': pinger_config.DEFAULT_CONFIG
                }.get(module, {})
                
                # Check if all required keys are present
                missing_keys = []
                for key in default_settings:
                    if key not in module_settings:
                        missing_keys.append(key)
                
                if missing_keys:
                    print(f"\n=== {module.upper()} ===")
                    print(f"WARNING: Missing required keys: {missing_keys}")
                else:
                    print(f"\n=== {module.upper()} ===")
                    print("All required keys are present.")
            else:
                print(f"\n=== {module.upper()} ===")
                print("No settings file found.")
    except Exception as e:
        logger.error(f"Error validating settings: {e}")

def reset_settings(module: str = None) -> bool:
    """
    Reset settings to defaults.
    
    Args:
        module: Optional module name to reset only specific settings
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Import config modules to get default settings
        if module:
            if module not in MODULES:
                logger.error(f"Unknown module: {module}")
                return False
            modules_to_reset = [module]
        else:
            modules_to_reset = MODULES
            
        # Reset settings for each module
        for module_name in modules_to_reset:
            settings_file = os.path.join(SETTINGS_DIR, f"{module_name}.json")
            
            # Backup existing settings if they exist
            if os.path.exists(settings_file):
                backup_file = f"{settings_file}.bak"
                os.rename(settings_file, backup_file)
                logger.info(f"Backed up {settings_file} to {backup_file}")
            
            # Use the module's reset_config function
            if module_name == 'keyword_filter':
                import config.keyword_filter_config as keyword_filter_config
                keyword_filter_config.reset_config()
            elif module_name == 'link_reaction':
                import config.link_reaction_config as link_reaction_config
                link_reaction_config.reset_config()
            elif module_name == 'reaction_forward':
                import config.reaction_forward_config as reaction_forward_config
                reaction_forward_config.reset_config()
            elif module_name == 'pinger':
                import config.pinger_config as pinger_config
                pinger_config.reset_config()
                
            logger.info(f"Reset settings for {module_name}")
        
        return True
    except Exception as e:
        logger.error(f"Error resetting settings: {e}")
        return False

def main():
    """Main function for the settings management script."""
    parser = argparse.ArgumentParser(description='Manage Discord bot settings')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export settings to a file')
    export_parser.add_argument('file', help='Output file path')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import settings from a file')
    import_parser.add_argument('file', help='Input file path')
    import_parser.add_argument('--module', help='Import only specific module settings')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List current settings')
    list_parser.add_argument('--module', help='List only specific module settings')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate settings structure')
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset settings to defaults')
    reset_parser.add_argument('--module', help='Reset only specific module settings')
    
    args = parser.parse_args()
    
    if args.command == 'export':
        export_settings(args.file)
    elif args.command == 'import':
        import_settings(args.file, args.module)
    elif args.command == 'list':
        list_settings(args.module)
    elif args.command == 'validate':
        validate_settings()
    elif args.command == 'reset':
        reset_settings(args.module)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 