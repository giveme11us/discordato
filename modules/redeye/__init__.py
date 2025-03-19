"""
Redeye Module

This module provides functionality for managing role-based waitlists and
related features for redeye operations.
"""

import logging
logger = logging.getLogger('discord_bot.modules.redeye')

from modules.redeye.redeye import setup_redeye

__all__ = ["setup_redeye"] 