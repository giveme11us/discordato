"""
Unit tests for command registration system.
"""
import pytest
from discord import app_commands
from core.command_sync import register_command, is_command_registered

@pytest.mark.unit
class TestCommandRegistration:
    """Test suite for command registration functionality."""
    
    def test_command_registration(self, mock_client):
        """Test that commands can be registered successfully."""
        # Setup
        command_name = "test_command"
        registered_commands = set()
        
        # Test registration
        @register_command(mock_client, registered_commands)
        @app_commands.command(name=command_name, description="Test command")
        async def test_command(interaction):
            await interaction.response.send_message("Test response")
            
        # Verify
        assert command_name in registered_commands
        assert is_command_registered(command_name, registered_commands)
        
    def test_duplicate_command_registration(self, mock_client):
        """Test that duplicate commands are handled properly."""
        # Setup
        command_name = "duplicate_command"
        registered_commands = set()
        
        # Register first command
        @register_command(mock_client, registered_commands)
        @app_commands.command(name=command_name, description="First command")
        async def first_command(interaction):
            await interaction.response.send_message("First response")
            
        # Try to register duplicate command
        with pytest.raises(ValueError, match=f"Command '{command_name}' is already registered"):
            @register_command(mock_client, registered_commands)
            @app_commands.command(name=command_name, description="Second command")
            async def second_command(interaction):
                await interaction.response.send_message("Second response")
                
    def test_command_registration_tracking(self, mock_client):
        """Test that command registration tracking works correctly."""
        # Setup
        registered_commands = set()
        commands = [
            ("cmd1", "First command"),
            ("cmd2", "Second command"),
            ("cmd3", "Third command")
        ]
        
        # Register multiple commands
        for name, desc in commands:
            @register_command(mock_client, registered_commands)
            @app_commands.command(name=name, description=desc)
            async def command(interaction):
                await interaction.response.send_message(f"Response from {name}")
                
        # Verify all commands are tracked
        for name, _ in commands:
            assert name in registered_commands
            assert is_command_registered(name, registered_commands)
            
        # Verify count
        assert len(registered_commands) == len(commands) 