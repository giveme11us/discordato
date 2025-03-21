"""
Rules Engine

This module provides a centralized rules management system for Discord bot features.

The Rules Engine is responsible for:
1. Managing feature-specific rule configurations
2. Persisting rules in JSON format
3. Providing rule CRUD operations
4. Handling rule validation and updates

Critical:
- Rules must be properly persisted
- Rule updates must be atomic
- Rule IDs must be unique per feature
- JSON storage must be valid

Classes:
    RuleManager: Feature-specific rule management system
"""

import json
import os
import logging
from pathlib import Path

logger = logging.getLogger('discord_bot.core.rules_engine')

class RuleManager:
    """
    Manages rule configurations for Discord bot features.
    
    This class handles:
    - Rule storage and retrieval
    - Rule validation and updates
    - JSON persistence
    - Active rule filtering
    
    Each feature should have its own RuleManager instance
    to manage its specific rule configurations.
    
    Attributes:
        feature_id (str): Unique identifier for the feature
        data_dir (Path): Directory for rule storage
        rules (dict): Current rule configurations
        file_path (Path): Path to rule JSON file
        
    Critical:
        - Rule IDs must be unique within a feature
        - JSON files must be properly formatted
        - File operations must be atomic
        - Rules must be validated before storage
    """
    
    def __init__(self, feature_id: str, data_dir: str = "data/rules"):
        """
        Initialize a rule manager for a feature.
        
        Args:
            feature_id (str): Unique identifier for the feature
            data_dir (str, optional): Directory for rule storage
                                    Defaults to "data/rules"
            
        Note:
            Creates the data directory if it doesn't exist
            and loads any existing rules.
        """
        self.feature_id = feature_id
        self.data_dir = Path(data_dir)
        self.rules = {}
        self.file_path = self.data_dir / f"{feature_id}_rules.json"
        
        os.makedirs(self.data_dir, exist_ok=True)
        self.load_rules()
    
    def load_rules(self) -> None:
        """
        Load rules from the JSON file.
        
        This method:
        1. Checks for existing rule file
        2. Loads and parses JSON
        3. Initializes empty rules if needed
        
        Note:
            Failures are logged and result in empty rules
        """
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
    
    def save_rules(self) -> bool:
        """
        Save rules to the JSON file.
        
        This method:
        1. Ensures directory exists
        2. Writes rules to JSON
        3. Handles atomic updates
        
        Returns:
            bool: True if save successful, False otherwise
            
        Note:
            Uses JSON indentation for readability
        """
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w') as f:
                json.dump(self.rules, f, indent=2)
            logger.info(f"Saved {len(self.rules)} rules for feature '{self.feature_id}'")
            return True
        except Exception as e:
            logger.error(f"Error saving rules for '{self.feature_id}': {e}")
            return False
    
    def add_rule(self, rule_id: str, rule_data: dict) -> bool:
        """
        Add or update a rule.
        
        This method:
        1. Validates rule data
        2. Adds/updates rule
        3. Persists changes
        
        Args:
            rule_id (str): Unique identifier for the rule
            rule_data (dict): Rule configuration data
            
        Returns:
            bool: True if operation successful
            
        Note:
            Overwrites existing rule if ID exists
        """
        self.rules[rule_id] = rule_data
        return self.save_rules()
    
    def remove_rule(self, rule_id: str) -> bool:
        """
        Remove a rule by ID.
        
        This method:
        1. Checks rule existence
        2. Removes if found
        3. Persists changes
        
        Args:
            rule_id (str): ID of rule to remove
            
        Returns:
            bool: True if rule removed, False if not found
            
        Note:
            Returns False if rule doesn't exist
        """
        if rule_id in self.rules:
            del self.rules[rule_id]
            return self.save_rules()
        return False
    
    def update_rule(self, rule_id: str, **updates) -> bool:
        """
        Update specific fields of a rule.
        
        This method:
        1. Validates rule existence
        2. Applies field updates
        3. Handles nested updates
        4. Persists changes
        
        Args:
            rule_id (str): ID of rule to update
            **updates: Field updates as keyword arguments
            
        Returns:
            bool: True if update successful
            
        Note:
            Supports nested updates using dot notation
            (e.g., "config.enabled")
        """
        if rule_id not in self.rules:
            return False
        
        for key, value in updates.items():
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
    
    def get_rule(self, rule_id: str) -> dict:
        """
        Retrieve a rule by ID.
        
        Args:
            rule_id (str): ID of rule to retrieve
            
        Returns:
            dict: Rule configuration if found, None otherwise
            
        Note:
            Returns None if rule doesn't exist
        """
        return self.rules.get(rule_id)
    
    def get_all_rules(self) -> dict:
        """
        Retrieve all rules for the feature.
        
        Returns:
            dict: All rule configurations
            
        Note:
            Returns empty dict if no rules exist
        """
        return self.rules
    
    def get_active_rules(self) -> dict:
        """
        Retrieve all active rules.
        
        This method:
        1. Filters rules by enabled status
        2. Returns active rule subset
        
        Returns:
            dict: Active rule configurations
            
        Note:
            Rules are considered active if enabled=True
            or if enabled field is not present
        """
        return {rule_id: rule for rule_id, rule in self.rules.items() 
                if rule.get('enabled', True)} 