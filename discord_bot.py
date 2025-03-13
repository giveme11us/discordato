#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Bot - Main Entry Point

This script initializes and runs the Discord bot system.
It handles command-line arguments and configuration loading.
"""

import os
import sys
import argparse
import logging

from core.bot_manager import BotManager
from config.environment import load_environment

def main():
    """
    Main entry point for the Discord bot application.
    Parses command-line arguments, loads configuration, and starts the bot.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Discord Bot')
    parser.add_argument('--config', type=str, default='.env',
                        help='Path to the configuration file')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode')
    args = parser.parse_args()

    # Load environment variables
    load_environment(args.config)

    # Configure logging
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger('discord_bot')
    logger.info("Starting Discord Bot")
    
    # Override log level if debug flag is provided
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    try:
        # Initialize the bot manager
        bot_manager = BotManager()
        
        # Start the bots
        bot_manager.start()
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()