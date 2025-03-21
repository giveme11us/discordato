"""
Integration tests for Discord event handling.
"""
import pytest
import discord
from unittest.mock import AsyncMock, patch, call
from core.bot import DiscordBot
from core.event_handler import EventHandler

@pytest.mark.integration
class TestEventHandling:
    """Integration test suite for Discord event handling."""
    
    @pytest.fixture
    async def bot(self):
        """Fixture to provide a bot instance."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        bot = DiscordBot(command_prefix="!", intents=intents)
        await bot._async_setup()
        yield bot
        await bot._async_cleanup()
        
    @pytest.fixture
    async def guild(self):
        """Fixture to provide a mock guild."""
        guild = AsyncMock(spec=discord.Guild)
        guild.id = 123456789
        return guild
        
    @pytest.fixture
    async def channel(self, guild):
        """Fixture to provide a mock channel."""
        channel = AsyncMock(spec=discord.TextChannel)
        channel.guild = guild
        channel.id = 987654321
        return channel
        
    @pytest.fixture
    async def member(self, guild):
        """Fixture to provide a mock member."""
        member = AsyncMock(spec=discord.Member)
        member.guild = guild
        member.id = 111222333
        member.name = "TestUser"
        return member
        
    async def test_message_event(self, bot, member, channel):
        """Test message event handling."""
        # Setup
        received_messages = []
        
        @bot.event
        async def on_message(message):
            received_messages.append(message)
            
        # Create mock message
        message = AsyncMock(spec=discord.Message)
        message.author = member
        message.channel = channel
        message.content = "Test message"
        message.guild = channel.guild
        
        # Test
        await bot.process_message(message)
        
        # Verify
        assert len(received_messages) == 1
        assert received_messages[0] == message
        
    async def test_member_join_event(self, bot, member, guild):
        """Test member join event handling."""
        # Setup
        join_events = []
        
        @bot.event
        async def on_member_join(member):
            join_events.append(member)
            
        # Test
        await bot.dispatch("member_join", member)
        
        # Verify
        assert len(join_events) == 1
        assert join_events[0] == member
        
    async def test_reaction_add_event(self, bot, member, channel):
        """Test reaction add event handling."""
        # Setup
        reaction_events = []
        
        @bot.event
        async def on_reaction_add(reaction, user):
            reaction_events.append((reaction, user))
            
        # Create mock reaction
        message = AsyncMock(spec=discord.Message)
        message.channel = channel
        message.guild = channel.guild
        
        reaction = AsyncMock(spec=discord.Reaction)
        reaction.message = message
        reaction.emoji = "👍"
        
        # Test
        await bot.dispatch("reaction_add", reaction, member)
        
        # Verify
        assert len(reaction_events) == 1
        assert reaction_events[0] == (reaction, member)
        
    async def test_multiple_event_handlers(self, bot, member, channel):
        """Test multiple handlers for the same event."""
        # Setup
        handler1_calls = []
        handler2_calls = []
        
        @bot.event
        async def on_message(message):
            handler1_calls.append(message)
            
        @bot.listen()
        async def on_message(message):
            handler2_calls.append(message)
            
        # Create mock message
        message = AsyncMock(spec=discord.Message)
        message.author = member
        message.channel = channel
        message.content = "Test message"
        message.guild = channel.guild
        
        # Test
        await bot.process_message(message)
        
        # Verify both handlers were called
        assert len(handler1_calls) == 1
        assert len(handler2_calls) == 1
        assert handler1_calls[0] == message
        assert handler2_calls[0] == message
        
    async def test_error_event_handling(self, bot):
        """Test error event handling."""
        # Setup
        error_events = []
        
        @bot.event
        async def on_error(event_name, *args, **kwargs):
            error_events.append((event_name, args, kwargs))
            
        # Test - trigger an error in message handling
        await bot.dispatch("message", None)  # This should cause an error
        
        # Verify
        assert len(error_events) == 1
        assert error_events[0][0] == "message"
        
    async def test_raw_event_handling(self, bot, channel):
        """Test raw event handling."""
        # Setup
        raw_events = []
        
        @bot.event
        async def on_raw_reaction_add(payload):
            raw_events.append(payload)
            
        # Create mock payload
        payload = discord.RawReactionActionEvent(
            data={
                "message_id": 123456789,
                "user_id": 111222333,
                "channel_id": channel.id,
                "guild_id": channel.guild.id,
                "emoji": {"name": "👍"}
            },
            emoji=discord.PartialEmoji(name="👍")
        )
        
        # Test
        await bot.dispatch("raw_reaction_add", payload)
        
        # Verify
        assert len(raw_events) == 1
        assert raw_events[0] == payload
        
    async def test_event_wait_for(self, bot, member, channel):
        """Test wait_for functionality."""
        # Setup
        message = AsyncMock(spec=discord.Message)
        message.author = member
        message.channel = channel
        message.content = "Test message"
        message.guild = channel.guild
        
        # Test
        def check(m):
            return m.author == member
            
        # Start waiting for message
        wait_task = bot.loop.create_task(
            bot.wait_for("message", check=check, timeout=1.0)
        )
        
        # Dispatch message event
        await bot.dispatch("message", message)
        
        # Get result
        received_message = await wait_task
        
        # Verify
        assert received_message == message
        
    async def test_event_propagation(self, bot, member, channel):
        """Test event propagation through multiple systems."""
        # Setup
        message_events = []
        command_events = []
        
        @bot.event
        async def on_message(message):
            message_events.append(message)
            
        @bot.tree.command(name="test")
        async def test_command(interaction):
            command_events.append(interaction)
            
        await bot.tree.sync()
        
        # Create mock message and interaction
        message = AsyncMock(spec=discord.Message)
        message.author = member
        message.channel = channel
        message.content = "/test"
        message.guild = channel.guild
        
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.user = member
        interaction.channel = channel
        interaction.guild = channel.guild
        
        # Test message event
        await bot.process_message(message)
        
        # Test command event
        command = bot.tree.get_command("test")
        await command.callback(interaction)
        
        # Verify
        assert len(message_events) == 1
        assert len(command_events) == 1
        assert message_events[0] == message
        assert command_events[0] == interaction
        
    async def test_custom_event_handling(self, bot):
        """Test handling of custom events."""
        # Setup
        custom_events = []
        
        @bot.event
        async def on_custom_event(data):
            custom_events.append(data)
            
        # Test
        custom_data = {"key": "value"}
        await bot.dispatch("custom_event", custom_data)
        
        # Verify
        assert len(custom_events) == 1
        assert custom_events[0] == custom_data 