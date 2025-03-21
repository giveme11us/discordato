import pytest
import discord
from discord.ext import commands
import os
import dotenv

@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load environment variables before running tests."""
    dotenv.load_dotenv()

@pytest.fixture
def mock_bot():
    """Create a mock bot instance for testing."""
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)
    return bot

@pytest.fixture
def mock_interaction():
    """Create a mock Discord interaction for testing commands."""
    class MockInteraction:
        async def response(self, content):
            self.response_content = content
            
        async def respond(self, content, ephemeral=False):
            self.response_content = content
            self.ephemeral = ephemeral
            
    return MockInteraction() 