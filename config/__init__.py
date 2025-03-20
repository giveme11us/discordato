"""
Configuration package for the Discord bot.
Exposes all configuration modules and their instances.
"""

from config.core.base_config import BaseConfig
from config.features.pinger_config import pinger_config
from config.features.moderation import filter as filter_config, mod as mod_config
from config.features.reactions import forward as forward_config, link as link_config
from config.features.redeye_config import redeye as redeye_config
from config.features.embed_config import embed as embed_config

__all__ = [
    'BaseConfig',
    'pinger_config',
    'filter_config',
    'mod_config',
    'forward_config',
    'link_config',
    'redeye_config',
    'embed_config'
]
