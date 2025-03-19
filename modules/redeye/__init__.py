"""
Redeye Module

This module provides functionality for viewing and managing CSV profiles for
redeye operations.
"""

import logging
logger = logging.getLogger('discord_bot.modules.redeye')

from modules.redeye.profile_cmd import setup_profile_cmd

__all__ = ["setup_profile_cmd"] 