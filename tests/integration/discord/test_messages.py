"""
Integration tests for Discord message handling.
"""
import pytest
import discord
from unittest.mock import AsyncMock, patch, call
from core.bot import DiscordBot
from core.message_handler import MessageHandler

@pytest.mark.integration
class TestMessageHandling:
    """Integration test suite for Discord message handling."""
    
    @pytest.fixture
    async def bot(self):
        """Fixture to provide a bot instance."""
        intents = discord.Intents.default()
        intents.message_content = True
        bot = DiscordBot(command_prefix="!", intents=intents)
        await bot._async_setup()
        yield bot
        await bot._async_cleanup()
        
    @pytest.fixture
    async def message_handler(self, bot):
        """Fixture to provide a message handler instance."""
        return MessageHandler(bot)
        
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
        
    async def test_message_sending(self, message_handler, channel):
        """Test sending messages."""
        # Test
        content = "Test message"
        message = await message_handler.send_message(channel, content)
        
        # Verify
        channel.send.assert_called_once_with(content)
        
    async def test_message_editing(self, message_handler, channel, member):
        """Test editing messages."""
        # Setup
        original_content = "Original message"
        new_content = "Edited message"
        
        message = AsyncMock(spec=discord.Message)
        message.channel = channel
        message.author = member
        message.content = original_content
        
        # Test
        await message_handler.edit_message(message, new_content)
        
        # Verify
        message.edit.assert_called_once_with(content=new_content)
        
    async def test_message_deletion(self, message_handler, channel, member):
        """Test message deletion."""
        # Setup
        message = AsyncMock(spec=discord.Message)
        message.channel = channel
        message.author = member
        
        # Test
        await message_handler.delete_message(message)
        
        # Verify
        message.delete.assert_called_once()
        
    async def test_bulk_message_deletion(self, message_handler, channel):
        """Test bulk message deletion."""
        # Setup
        messages = [
            AsyncMock(spec=discord.Message) for _ in range(3)
        ]
        
        # Test
        await message_handler.bulk_delete_messages(channel, messages)
        
        # Verify
        channel.delete_messages.assert_called_once_with(messages)
        
    async def test_message_pinning(self, message_handler, channel, member):
        """Test message pinning operations."""
        # Setup
        message = AsyncMock(spec=discord.Message)
        message.channel = channel
        message.author = member
        
        # Test pin
        await message_handler.pin_message(message)
        message.pin.assert_called_once()
        
        # Test unpin
        await message_handler.unpin_message(message)
        message.unpin.assert_called_once()
        
    async def test_message_history(self, message_handler, channel):
        """Test message history retrieval."""
        # Setup
        mock_messages = [
            AsyncMock(spec=discord.Message) for _ in range(5)
        ]
        channel.history.return_value.flatten = AsyncMock(
            return_value=mock_messages
        )
        
        # Test
        messages = await message_handler.get_message_history(
            channel, limit=5
        )
        
        # Verify
        assert len(messages) == 5
        channel.history.assert_called_once_with(limit=5)
        
    async def test_message_reactions(self, message_handler, member):
        """Test message reaction handling."""
        # Setup
        message = AsyncMock(spec=discord.Message)
        emoji = "👍"
        
        # Test add reaction
        await message_handler.add_reaction(message, emoji)
        message.add_reaction.assert_called_once_with(emoji)
        
        # Test remove reaction
        await message_handler.remove_reaction(message, emoji, member)
        message.remove_reaction.assert_called_once_with(emoji, member)
        
    async def test_message_embeds(self, message_handler, channel):
        """Test sending messages with embeds."""
        # Setup
        embed = discord.Embed(
            title="Test Embed",
            description="Test description"
        )
        
        # Test
        await message_handler.send_embed(channel, embed)
        
        # Verify
        channel.send.assert_called_once_with(embed=embed)
        
    async def test_message_files(self, message_handler, channel):
        """Test sending messages with files."""
        # Setup
        file = AsyncMock(spec=discord.File)
        
        # Test
        await message_handler.send_file(channel, file)
        
        # Verify
        channel.send.assert_called_once_with(file=file)
        
    async def test_message_reference(self, message_handler, channel, member):
        """Test message references and replies."""
        # Setup
        reference_message = AsyncMock(spec=discord.Message)
        reference_message.channel = channel
        reference_message.author = member
        
        content = "Reply message"
        
        # Test
        await message_handler.reply_to_message(
            reference_message,
            content
        )
        
        # Verify
        reference_message.reply.assert_called_once_with(content)
        
    async def test_message_content_parsing(self, message_handler, channel, member):
        """Test message content parsing."""
        # Setup
        content = "Hello @TestUser and #general"
        
        message = AsyncMock(spec=discord.Message)
        message.channel = channel
        message.author = member
        message.content = content
        message.mentions = [member]
        message.channel_mentions = [channel]
        
        # Test
        parsed = await message_handler.parse_message_content(message)
        
        # Verify
        assert parsed["mentions"] == [member]
        assert parsed["channel_mentions"] == [channel]
        assert parsed["content"] == content
        
    async def test_message_filtering(self, message_handler, channel, member):
        """Test message content filtering."""
        # Setup
        filtered_words = ["bad", "words"]
        message_handler.set_filtered_words(filtered_words)
        
        clean_content = "Hello world"
        bad_content = "Hello bad words"
        
        # Test clean message
        clean_message = AsyncMock(spec=discord.Message)
        clean_message.content = clean_content
        assert await message_handler.is_clean_message(clean_message)
        
        # Test filtered message
        bad_message = AsyncMock(spec=discord.Message)
        bad_message.content = bad_content
        assert not await message_handler.is_clean_message(bad_message)
        
    async def test_message_quotas(self, message_handler, channel, member):
        """Test message quota enforcement."""
        # Setup
        quota = 3
        interval = 60  # seconds
        message_handler.set_quota(quota, interval)
        
        message = AsyncMock(spec=discord.Message)
        message.author = member
        
        # Test
        for _ in range(quota):
            assert await message_handler.check_quota(member)
            
        # Should exceed quota
        assert not await message_handler.check_quota(member)
        
    async def test_message_formatting(self, message_handler):
        """Test message formatting utilities."""
        # Test various formatting options
        bold = message_handler.format_bold("text")
        italic = message_handler.format_italic("text")
        code = message_handler.format_code("text")
        underline = message_handler.format_underline("text")
        
        assert bold == "**text**"
        assert italic == "*text*"
        assert code == "`text`"
        assert underline == "__text__"
        
    async def test_message_components(self, message_handler, channel):
        """Test message components (buttons, selects)."""
        # Setup
        components = [
            discord.Button(label="Test Button"),
            discord.SelectMenu(
                custom_id="test_select",
                options=[
                    discord.SelectOption(label="Option 1"),
                    discord.SelectOption(label="Option 2")
                ]
            )
        ]
        
        # Test
        await message_handler.send_with_components(
            channel,
            "Test message",
            components
        )
        
        # Verify
        channel.send.assert_called_once_with(
            "Test message",
            components=components
        ) 