"""
Unit tests for error handling system.
"""
import pytest
from discord import app_commands
from core.error_handler import handle_command_error, ErrorResponse

@pytest.mark.unit
class TestErrorHandling:
    """Test suite for error handling functionality."""
    
    async def test_basic_error_handling(self, mock_interaction):
        """Test basic error handling for commands."""
        # Setup
        error = Exception("Test error")
        
        # Test
        await handle_command_error(mock_interaction, error)
        
        # Verify
        assert mock_interaction.response_sent
        assert "An error occurred" in mock_interaction.response_content
        assert mock_interaction.ephemeral  # Error messages should be ephemeral
        
    async def test_custom_error_handling(self, mock_interaction):
        """Test handling of custom command errors."""
        # Setup
        class CustomCommandError(app_commands.AppCommandError):
            pass
            
        error = CustomCommandError("Custom error message")
        
        # Test
        await handle_command_error(mock_interaction, error)
        
        # Verify
        assert mock_interaction.response_sent
        assert "Custom error message" in mock_interaction.response_content
        assert mock_interaction.ephemeral
        
    async def test_permission_error_handling(self, mock_interaction):
        """Test handling of permission errors."""
        # Setup
        error = app_commands.MissingPermissions(["manage_messages"])
        
        # Test
        await handle_command_error(mock_interaction, error)
        
        # Verify
        assert mock_interaction.response_sent
        assert "You don't have permission" in mock_interaction.response_content
        assert "manage_messages" in mock_interaction.response_content.lower()
        assert mock_interaction.ephemeral
        
    async def test_error_response_formatting(self, mock_interaction):
        """Test error response formatting."""
        # Setup
        test_cases = [
            (Exception("Generic error"), ErrorResponse.GENERIC),
            (ValueError("Invalid value"), ErrorResponse.INVALID_INPUT),
            (app_commands.CommandOnCooldown(retry_after=5), ErrorResponse.COOLDOWN),
        ]
        
        # Test each case
        for error, expected_type in test_cases:
            # Reset mock
            mock_interaction.response_sent = False
            mock_interaction.response_content = None
            
            # Test
            await handle_command_error(mock_interaction, error)
            
            # Verify
            assert mock_interaction.response_sent
            assert expected_type.value in mock_interaction.response_content
            assert mock_interaction.ephemeral
            
    async def test_error_logging(self, mock_interaction, caplog):
        """Test that errors are properly logged."""
        # Setup
        error = Exception("Test error for logging")
        
        # Test
        with caplog.at_level("ERROR"):
            await handle_command_error(mock_interaction, error)
            
        # Verify
        assert "Test error for logging" in caplog.text
        assert "ERROR" in caplog.text 