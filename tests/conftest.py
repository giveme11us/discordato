"""
Global pytest configuration and fixtures.
"""
import os
import pytest
import discord
from discord.ext import commands
from typing import Generator, Any
import dotenv

@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load environment variables before running tests."""
    dotenv.load_dotenv()

class MockDiscordClient(discord.Client):
    """Mock Discord client for testing."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages_sent = []
        self.last_message = None

    async def send_message(self, content: str, channel_id: int = None) -> None:
        """Mock sending a message."""
        self.messages_sent.append({
            'content': content,
            'channel_id': channel_id
        })
        self.last_message = content

@pytest.fixture
def mock_client() -> Generator[MockDiscordClient, Any, None]:
    """Fixture that provides a mock Discord client."""
    intents = discord.Intents.default()
    intents.message_content = True
    client = MockDiscordClient(intents=intents)
    yield client

@pytest.fixture
def mock_interaction() -> Generator[discord.Interaction, Any, None]:
    """Fixture that provides a mock Discord interaction."""
    class MockInteraction:
        def __init__(self):
            self.response_sent = False
            self.response_content = None
            self.deferred = False
            self.ephemeral = False

        async def response_send_message(self, content, ephemeral=False):
            self.response_sent = True
            self.response_content = content
            self.ephemeral = ephemeral

        async def defer(self, ephemeral=False):
            self.deferred = True
            self.ephemeral = ephemeral

    interaction = MockInteraction()
    yield interaction

@pytest.fixture
def test_config() -> dict:
    """Fixture that provides test configuration."""
    return {
        'DISCORD_BOT_TOKEN': 'mock_token',
        'APPLICATION_ID': 'mock_app_id',
        'GUILD_IDS': '123456789,987654321',
        'ENABLED_MODULES': 'mod,online,instore,redeye'
    }

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Automatically set up test environment variables."""
    monkeypatch.setenv('TESTING', 'true')
    monkeypatch.setenv('DISCORD_BOT_TOKEN', 'mock_token')
    monkeypatch.setenv('APPLICATION_ID', 'mock_app_id') 