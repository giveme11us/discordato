import pytest
import discord
from discord.ext import commands
from core.commands.base import BaseCommand
from core.command_registry import CommandRegistry

class TestPingCommand(BaseCommand):
    def __init__(self):
        super().__init__(
            name="test_ping",
            description="Test ping command"
        )
    
    async def execute(self, interaction, **kwargs):
        return "Pong!"

@pytest.fixture
def command_registry():
    return CommandRegistry()

@pytest.fixture
def test_command():
    return TestPingCommand()

def test_command_registration(command_registry, test_command):
    command_registry.register_command(test_command)
    assert test_command.name in command_registry.commands
    assert command_registry.commands[test_command.name] == test_command

@pytest.mark.asyncio
async def test_command_execution(test_command):
    # Create a mock interaction
    class MockInteraction:
        async def response(self, content):
            self.response_content = content
            
    interaction = MockInteraction()
    
    # Execute the command
    result = await test_command.execute(interaction)
    assert result == "Pong!"

def test_command_properties(test_command):
    assert test_command.name == "test_ping"
    assert test_command.description == "Test ping command"
    assert isinstance(test_command, BaseCommand) 