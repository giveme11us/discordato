"""
Configuration package for the Discord bot.
Exposes all configuration modules and their instances.
"""

from config.core.base_config import BaseConfig
from config.features.embed_config import embed
from config.features.moderation import mod as mod_config
from config.features.reactions import forward as forward_config, link as link_config
from config.features.redeye_config import redeye as redeye_config

__all__ = [
    'BaseConfig',
    'embed',
    'mod_config',
    'forward_config',
    'link_config',
    'redeye_config'
]
