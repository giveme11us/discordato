"""
Rules Engine

A central rules management system for various features.
Each feature can create a RuleManager instance to manage its own rule configurations.
Rules are stored as JSON files in the data/rules directory.
"""

import json
import os
import logging
from pathlib import Path

logger = logging.getLogger('discord_bot.core.rules_engine')

class RuleManager:
    """Manages rule configurations for various features."""
    
    def __init__(self, feature_id, data_dir="data/rules"):
        self.feature_id = feature_id
        self.data_dir = Path(data_dir)
        self.rules = {}
        self.file_path = self.data_dir / f"{feature_id}_rules.json"
        
        # Create directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load existing rules
        self.load_rules()
    
    def load_rules(self):
        """Load rules from the JSON file."""
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as f:
                    self.rules = json.load(f)
                logger.info(f"Loaded {len(self.rules)} rules for feature '{self.feature_id}'")
            except Exception as e:
                logger.error(f"Error loading rules for '{self.feature_id}': {e}")
                self.rules = {}
        else:
            logger.info(f"No existing rules file for '{self.feature_id}', starting empty")
            self.rules = {}
    
    def save_rules(self):
        """Save rules to the JSON file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w') as f:
                json.dump(self.rules, f, indent=2)
            logger.info(f"Saved {len(self.rules)} rules for feature '{self.feature_id}'")
            return True
        except Exception as e:
            logger.error(f"Error saving rules for '{self.feature_id}': {e}")
            return False
    
    def add_rule(self, rule_id, rule_data):
        """Add a new rule or update an existing one."""
        self.rules[rule_id] = rule_data
        return self.save_rules()
    
    def remove_rule(self, rule_id):
        """Remove a rule by ID."""
        if rule_id in self.rules:
            del self.rules[rule_id]
            return self.save_rules()
        return False
    
    def update_rule(self, rule_id, **updates):
        """Update specific fields of an existing rule."""
        if rule_id not in self.rules:
            return False
        
        for key, value in updates.items():
            # Handle nested dict updates with dot notation (e.g., "config.enabled")
            if '.' in key:
                parts = key.split('.')
                target = self.rules[rule_id]
                for part in parts[:-1]:
                    if part not in target:
                        target[part] = {}
                    target = target[part]
                target[parts[-1]] = value
            else:
                self.rules[rule_id][key] = value
        
        return self.save_rules()
    
    def get_rule(self, rule_id):
        """Get a rule by ID."""
        return self.rules.get(rule_id)
    
    def get_all_rules(self):
        """Get all rules for this feature."""
        return self.rules
    
    def get_active_rules(self):
        """Get all active rules (where enabled is True)."""
        return {rule_id: rule for rule_id, rule in self.rules.items() 
                if rule.get('enabled', True)} 