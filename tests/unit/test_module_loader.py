"""
Unit tests for module loading system.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from core.module_loader import ModuleLoader, ModuleError

@pytest.mark.unit
class TestModuleLoader:
    """Test suite for module loading functionality."""
    
    @pytest.fixture
    def bot(self):
        """Fixture to provide a mock bot instance."""
        mock_bot = Mock()
        mock_bot.registered_commands = set()
        return mock_bot
        
    @pytest.fixture
    def module_loader(self, bot):
        """Fixture to provide a module loader instance."""
        return ModuleLoader(bot)
        
    def test_module_discovery(self, module_loader):
        """Test module discovery in modules directory."""
        with patch('os.listdir') as mock_listdir:
            # Setup mock directory structure
            mock_listdir.return_value = ['test_module', 'another_module', 'not_a_module.txt']
            
            # Test
            modules = module_loader.discover_modules()
            
            # Verify
            assert 'test_module' in modules
            assert 'another_module' in modules
            assert 'not_a_module.txt' not in modules
            
    async def test_module_loading(self, module_loader, bot):
        """Test loading of a module."""
        # Setup mock module
        mock_module = MagicMock()
        mock_module.setup = MagicMock()
        
        with patch('importlib.import_module', return_value=mock_module):
            # Test
            await module_loader.load_module('test_module')
            
            # Verify
            mock_module.setup.assert_called_once_with(bot, bot.registered_commands)
            assert 'test_module' in module_loader.loaded_modules
            
    async def test_module_unloading(self, module_loader, bot):
        """Test unloading of a module."""
        # Setup mock module
        mock_module = MagicMock()
        mock_module.teardown = MagicMock()
        
        # Load module first
        with patch('importlib.import_module', return_value=mock_module):
            await module_loader.load_module('test_module')
            
        # Test unloading
        await module_loader.unload_module('test_module')
        
        # Verify
        mock_module.teardown.assert_called_once_with(bot)
        assert 'test_module' not in module_loader.loaded_modules
        
    async def test_module_reload(self, module_loader, bot):
        """Test reloading of a module."""
        # Setup mock modules
        old_module = MagicMock()
        new_module = MagicMock()
        
        with patch('importlib.import_module') as mock_import:
            # Load initial module
            mock_import.return_value = old_module
            await module_loader.load_module('test_module')
            
            # Reload module
            mock_import.return_value = new_module
            await module_loader.reload_module('test_module')
            
            # Verify
            old_module.teardown.assert_called_once_with(bot)
            new_module.setup.assert_called_once_with(bot, bot.registered_commands)
            assert module_loader.loaded_modules['test_module'] == new_module
            
    async def test_invalid_module_loading(self, module_loader):
        """Test handling of invalid module loading."""
        # Test loading non-existent module
        with pytest.raises(ModuleError, match="Module not found"):
            await module_loader.load_module('nonexistent_module')
            
        # Test loading module without setup function
        mock_module = MagicMock()
        mock_module.setup = None
        
        with patch('importlib.import_module', return_value=mock_module):
            with pytest.raises(ModuleError, match="Module missing required setup function"):
                await module_loader.load_module('invalid_module')
                
    async def test_module_dependency_loading(self, module_loader, bot):
        """Test loading of modules with dependencies."""
        # Setup mock modules
        dependency_module = MagicMock()
        dependent_module = MagicMock()
        dependent_module.DEPENDENCIES = ['dependency_module']
        
        with patch('importlib.import_module') as mock_import:
            # Setup import to return different modules
            def import_side_effect(name):
                if name.endswith('dependency_module'):
                    return dependency_module
                return dependent_module
                
            mock_import.side_effect = import_side_effect
            
            # Test
            await module_loader.load_module('dependent_module')
            
            # Verify dependency was loaded first
            assert 'dependency_module' in module_loader.loaded_modules
            assert 'dependent_module' in module_loader.loaded_modules
            
    async def test_circular_dependency_detection(self, module_loader):
        """Test detection of circular dependencies."""
        # Setup mock modules with circular dependency
        module_a = MagicMock()
        module_a.DEPENDENCIES = ['module_b']
        module_b = MagicMock()
        module_b.DEPENDENCIES = ['module_a']
        
        with patch('importlib.import_module') as mock_import:
            def import_side_effect(name):
                if name.endswith('module_a'):
                    return module_a
                return module_b
                
            mock_import.side_effect = import_side_effect
            
            # Test
            with pytest.raises(ModuleError, match="Circular dependency detected"):
                await module_loader.load_module('module_a')
                
    async def test_module_load_order(self, module_loader, bot):
        """Test that modules are loaded in correct order based on priority."""
        # Setup mock modules with different priorities
        high_priority = MagicMock()
        high_priority.PRIORITY = 3
        medium_priority = MagicMock()
        medium_priority.PRIORITY = 2
        low_priority = MagicMock()
        low_priority.PRIORITY = 1
        
        modules = {
            'high': high_priority,
            'medium': medium_priority,
            'low': low_priority
        }
        
        with patch('importlib.import_module') as mock_import:
            mock_import.side_effect = lambda name: modules[name.split('.')[-1]]
            
            # Test loading all modules
            await module_loader.load_all_modules(['high', 'medium', 'low'])
            
            # Verify load order through setup call order
            setup_calls = [call[0][0] for call in bot.mock_calls]
            assert setup_calls.index('high') < setup_calls.index('medium')
            assert setup_calls.index('medium') < setup_calls.index('low')
            
    async def test_module_error_handling(self, module_loader, bot):
        """Test error handling during module operations."""
        # Setup mock module that raises error during setup
        error_module = MagicMock()
        error_module.setup.side_effect = Exception("Setup error")
        
        with patch('importlib.import_module', return_value=error_module):
            # Test
            with pytest.raises(ModuleError, match="Failed to setup module"):
                await module_loader.load_module('error_module')
                
            # Verify module was not loaded
            assert 'error_module' not in module_loader.loaded_modules
            
        # Test error during unload
        loaded_module = MagicMock()
        loaded_module.teardown.side_effect = Exception("Teardown error")
        
        module_loader.loaded_modules['test_module'] = loaded_module
        
        with pytest.raises(ModuleError, match="Failed to teardown module"):
            await module_loader.unload_module('test_module') 