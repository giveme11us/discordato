"""
Bot Manager Tests

This module contains tests for the bot manager.
"""

import unittest
import os
from unittest.mock import patch, MagicMock

from core.bot_manager import BotManager

class TestBotManager(unittest.TestCase):
    """
    Tests for the BotManager class.
    """
    
    @patch('core.bot_manager.get_token')
    @patch('core.bot_manager.ModuleLoader')
    def test_determine_scenario_single(self, mock_module_loader, mock_get_token):
        """
        Test the _determine_scenario method for single bot mode.
        """
        # Set up mocks
        mock_get_token.return_value = 'test_token'
        mock_module_loader_instance = MagicMock()
        mock_module_loader_instance.discover_modules.return_value = ['mod', 'online', 'instore']
        mock_module_loader.return_value = mock_module_loader_instance
        
        # Create bot manager
        bot_manager = BotManager()
        
        # Check scenario
        self.assertEqual(bot_manager.scenario, 'single')
    
    @patch('core.bot_manager.get_token')
    @patch('core.bot_manager.ModuleLoader')
    def test_determine_scenario_multi(self, mock_module_loader, mock_get_token):
        """
        Test the _determine_scenario method for multi bot mode.
        """
        # Set up mocks
        mock_get_token.side_effect = lambda module_name=None: 'main_token' if module_name is None else f'{module_name}_token'
        mock_module_loader_instance = MagicMock()
        mock_module_loader_instance.discover_modules.return_value = ['mod', 'online', 'instore']
        mock_module_loader.return_value = mock_module_loader_instance
        
        # Create bot manager
        bot_manager = BotManager()
        
        # Check scenario
        self.assertEqual(bot_manager.scenario, 'multi')
    
    @patch('core.bot_manager.get_token')
    @patch('core.bot_manager.ModuleLoader')
    def test_determine_scenario_partial(self, mock_module_loader, mock_get_token):
        """
        Test the _determine_scenario method for partial mode.
        """
        # Set up mocks
        def mock_token(module_name=None):
            if module_name is None:
                return 'main_token'
            elif module_name == 'mod':
                return 'mod_token'
            elif module_name == 'online':
                return None
            else:
                return 'main_token'
        
        mock_get_token.side_effect = mock_token
        mock_module_loader_instance = MagicMock()
        mock_module_loader_instance.discover_modules.return_value = ['mod', 'online', 'instore']
        mock_module_loader.return_value = mock_module_loader_instance
        
        # Create bot manager
        bot_manager = BotManager()
        
        # Check scenario
        self.assertEqual(bot_manager.scenario, 'partial')
    
    @patch('core.bot_manager.get_token')
    @patch('core.bot_manager.ModuleLoader')
    @patch('core.bot_manager.commands.Bot')
    def test_initialize_bots_single(self, mock_bot, mock_module_loader, mock_get_token):
        """
        Test the _initialize_bots method for single bot mode.
        """
        # Set up mocks
        mock_get_token.return_value = 'test_token'
        mock_module_loader_instance = MagicMock()
        mock_module_loader_instance.discover_modules.return_value = ['mod', 'online', 'instore']
        mock_module_loader.return_value = mock_module_loader_instance
        
        # Create bot manager
        bot_manager = BotManager()
        
        # Check bots
        self.assertEqual(len(bot_manager.bots), 1)
        self.assertIn('main', bot_manager.bots)
        
        # Check module loading
        self.assertEqual(mock_module_loader_instance.load_module.call_count, 3)

if __name__ == '__main__':
    unittest.main() 