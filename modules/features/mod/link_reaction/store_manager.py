"""
Store Manager for Link Reaction Feature

Manages store configurations for the link reaction feature.
Uses the rule engine to store and retrieve store configurations.
"""

import os
import logging
import re
from core.rules_engine import RuleManager

logger = logging.getLogger('discord_bot.modules.mod.link_reaction.store_manager')

class StoreManager:
    """Manages store configurations for link reaction feature."""
    
    def __init__(self):
        self.rule_manager = RuleManager("link_reaction_stores")
        
        # Initialize default stores if needed
        if not self.rule_manager.get_all_rules():
            self._initialize_default_stores()
    
    def _initialize_default_stores(self):
        """Set up default store configurations."""
        
        # Add LUISAVIAROMA as default store
        self.rule_manager.add_rule("luisaviaroma", {
            "enabled": True,
            "name": "LUISAVIAROMA",
            "description": "Extract product IDs from LUISAVIAROMA embeds",
            "file_path": os.getenv("luisaviaroma_drops_urls_path", "data/luisaviaroma_drop_urls.txt"),
            "detection": {
                "type": "author_name",
                "value": "LUISAVIAROMA"
            },
            "extraction": {
                "primary": "url",
                "pattern": r'\/[^\/]+\/([^\/]+)$',
                "fallback": "field_pid"
            }
        })
        
        logger.info("Initialized default store configuration for LUISAVIAROMA")
    
    def get_store(self, store_id):
        """Get store configuration by ID."""
        return self.rule_manager.get_rule(store_id)
    
    def get_all_stores(self):
        """Get all store configurations."""
        return self.rule_manager.get_all_rules()
    
    def get_active_stores(self):
        """Get active store configurations."""
        return self.rule_manager.get_active_rules()
    
    def add_store(self, store_id, name, file_path, detection_type, detection_value, 
                  extraction_primary, extraction_pattern=None, description=None, enabled=True):
        """Add a new store configuration."""
        return self.rule_manager.add_rule(store_id, {
            "enabled": enabled,
            "name": name,
            "description": description or f"Extract product IDs from {name} embeds",
            "file_path": file_path,
            "detection": {
                "type": detection_type,
                "value": detection_value
            },
            "extraction": {
                "primary": extraction_primary,
                "pattern": extraction_pattern,
                "fallback": "field_pid"  # Default fallback
            }
        })
    
    def remove_store(self, store_id):
        """Remove a store configuration."""
        return self.rule_manager.remove_rule(store_id)
    
    def update_store(self, store_id, **updates):
        """Update a store configuration."""
        return self.rule_manager.update_rule(store_id, **updates)

# Create a global instance of the store manager
store_manager = StoreManager() 