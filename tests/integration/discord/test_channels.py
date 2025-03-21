"""
Integration tests for Discord channel management.
"""
import pytest
import discord
from unittest.mock import AsyncMock, patch, call
from core.bot import DiscordBot
from core.channel_handler import ChannelHandler

@pytest.mark.integration
class TestChannelHandling:
    """Integration test suite for Discord channel management."""
    
    @pytest.fixture
    async def bot(self):
        """Fixture to provide a bot instance."""
        intents = discord.Intents.default()
        intents.guilds = True
        bot = DiscordBot(command_prefix="!", intents=intents)
        await bot._async_setup()
        yield bot
        await bot._async_cleanup()
        
    @pytest.fixture
    async def channel_handler(self, bot):
        """Fixture to provide a channel handler instance."""
        return ChannelHandler(bot)
        
    @pytest.fixture
    async def guild(self):
        """Fixture to provide a mock guild."""
        guild = AsyncMock(spec=discord.Guild)
        guild.id = 123456789
        return guild
        
    @pytest.fixture
    async def text_channel(self, guild):
        """Fixture to provide a mock text channel."""
        channel = AsyncMock(spec=discord.TextChannel)
        channel.guild = guild
        channel.id = 987654321
        channel.name = "test-text-channel"
        return channel
        
    @pytest.fixture
    async def voice_channel(self, guild):
        """Fixture to provide a mock voice channel."""
        channel = AsyncMock(spec=discord.VoiceChannel)
        channel.guild = guild
        channel.id = 456789123
        channel.name = "Test Voice Channel"
        return channel
        
    @pytest.fixture
    async def category(self, guild):
        """Fixture to provide a mock category."""
        category = AsyncMock(spec=discord.CategoryChannel)
        category.guild = guild
        category.id = 789123456
        category.name = "Test Category"
        return category
        
    @pytest.fixture
    async def member(self, guild):
        """Fixture to provide a mock member."""
        member = AsyncMock(spec=discord.Member)
        member.guild = guild
        member.id = 111222333
        member.name = "TestUser"
        return member
        
    async def test_create_text_channel(self, channel_handler, guild, category):
        """Test creating a text channel."""
        # Setup
        channel_name = "new-text-channel"
        topic = "Test channel topic"
        
        # Test
        channel = await channel_handler.create_text_channel(
            guild,
            name=channel_name,
            category=category,
            topic=topic,
            slowmode_delay=10,
            nsfw=False
        )
        
        # Verify
        guild.create_text_channel.assert_called_once_with(
            name=channel_name,
            category=category,
            topic=topic,
            slowmode_delay=10,
            nsfw=False
        )
        
    async def test_create_voice_channel(self, channel_handler, guild, category):
        """Test creating a voice channel."""
        # Setup
        channel_name = "New Voice Channel"
        
        # Test
        channel = await channel_handler.create_voice_channel(
            guild,
            name=channel_name,
            category=category,
            user_limit=10,
            bitrate=64000
        )
        
        # Verify
        guild.create_voice_channel.assert_called_once_with(
            name=channel_name,
            category=category,
            user_limit=10,
            bitrate=64000
        )
        
    async def test_create_category(self, channel_handler, guild):
        """Test creating a category."""
        # Setup
        category_name = "New Category"
        
        # Test
        category = await channel_handler.create_category(
            guild,
            name=category_name,
            position=0
        )
        
        # Verify
        guild.create_category.assert_called_once_with(
            name=category_name,
            position=0
        )
        
    async def test_delete_channel(self, channel_handler, text_channel):
        """Test deleting a channel."""
        # Test
        await channel_handler.delete_channel(text_channel)
        
        # Verify
        text_channel.delete.assert_called_once()
        
    async def test_modify_channel(self, channel_handler, text_channel):
        """Test modifying channel properties."""
        # Setup
        new_name = "updated-channel"
        new_topic = "Updated topic"
        
        # Test
        await channel_handler.modify_channel(
            text_channel,
            name=new_name,
            topic=new_topic,
            slowmode_delay=20
        )
        
        # Verify
        text_channel.edit.assert_called_once_with(
            name=new_name,
            topic=new_topic,
            slowmode_delay=20
        )
        
    async def test_channel_permissions(self, channel_handler, text_channel, member):
        """Test channel permission management."""
        # Setup
        overwrites = discord.PermissionOverwrite(
            read_messages=True,
            send_messages=True
        )
        
        # Test
        await channel_handler.set_permissions(
            text_channel,
            member,
            overwrites
        )
        
        # Verify
        text_channel.set_permissions.assert_called_once_with(
            member,
            overwrite=overwrites
        )
        
    async def test_move_channel(self, channel_handler, text_channel, category):
        """Test moving a channel to a category."""
        # Test
        await channel_handler.move_to_category(text_channel, category)
        
        # Verify
        text_channel.edit.assert_called_once_with(category=category)
        
    async def test_sync_permissions(self, channel_handler, text_channel):
        """Test syncing channel permissions with category."""
        # Test
        await channel_handler.sync_permissions(text_channel)
        
        # Verify
        text_channel.sync_permissions.assert_called_once()
        
    async def test_channel_position(self, channel_handler, text_channel):
        """Test changing channel position."""
        # Setup
        new_position = 5
        
        # Test
        await channel_handler.set_position(text_channel, new_position)
        
        # Verify
        text_channel.edit.assert_called_once_with(position=new_position)
        
    async def test_bulk_channel_delete(self, channel_handler, guild):
        """Test bulk channel deletion."""
        # Setup
        channels = [
            AsyncMock(spec=discord.TextChannel) for _ in range(3)
        ]
        
        # Test
        await channel_handler.bulk_delete_channels(channels)
        
        # Verify
        for channel in channels:
            channel.delete.assert_called_once()
            
    async def test_channel_clone(self, channel_handler, text_channel):
        """Test cloning a channel."""
        # Test
        await channel_handler.clone_channel(text_channel)
        
        # Verify
        text_channel.clone.assert_called_once()
        
    async def test_channel_webhooks(self, channel_handler, text_channel):
        """Test webhook management."""
        # Setup
        webhook_name = "Test Webhook"
        
        # Test create webhook
        await channel_handler.create_webhook(
            text_channel,
            name=webhook_name
        )
        text_channel.create_webhook.assert_called_once_with(
            name=webhook_name
        )
        
        # Test get webhooks
        await channel_handler.get_webhooks(text_channel)
        text_channel.webhooks.assert_called_once()
        
    async def test_channel_invites(self, channel_handler, text_channel):
        """Test invite management."""
        # Setup
        max_age = 3600
        max_uses = 10
        
        # Test create invite
        await channel_handler.create_invite(
            text_channel,
            max_age=max_age,
            max_uses=max_uses
        )
        text_channel.create_invite.assert_called_once_with(
            max_age=max_age,
            max_uses=max_uses
        )
        
        # Test get invites
        await channel_handler.get_invites(text_channel)
        text_channel.invites.assert_called_once()
        
    async def test_channel_slowmode(self, channel_handler, text_channel):
        """Test slowmode management."""
        # Setup
        delay = 30
        
        # Test
        await channel_handler.set_slowmode(text_channel, delay)
        
        # Verify
        text_channel.edit.assert_called_once_with(
            slowmode_delay=delay
        )
        
    async def test_channel_topic(self, channel_handler, text_channel):
        """Test channel topic management."""
        # Setup
        topic = "New channel topic"
        
        # Test
        await channel_handler.set_topic(text_channel, topic)
        
        # Verify
        text_channel.edit.assert_called_once_with(topic=topic)
        
    async def test_channel_nsfw(self, channel_handler, text_channel):
        """Test NSFW status management."""
        # Test enable NSFW
        await channel_handler.set_nsfw(text_channel, True)
        text_channel.edit.assert_called_with(nsfw=True)
        
        # Reset mock
        text_channel.edit.reset_mock()
        
        # Test disable NSFW
        await channel_handler.set_nsfw(text_channel, False)
        text_channel.edit.assert_called_with(nsfw=False)
        
    async def test_voice_channel_settings(self, channel_handler, voice_channel):
        """Test voice channel specific settings."""
        # Setup
        bitrate = 96000
        user_limit = 20
        
        # Test
        await channel_handler.set_voice_settings(
            voice_channel,
            bitrate=bitrate,
            user_limit=user_limit
        )
        
        # Verify
        voice_channel.edit.assert_called_once_with(
            bitrate=bitrate,
            user_limit=user_limit
        )
        
    async def test_category_management(self, channel_handler, category, text_channel):
        """Test category management."""
        # Test add to category
        await channel_handler.add_to_category(text_channel, category)
        text_channel.edit.assert_called_with(category=category)
        
        # Reset mock
        text_channel.edit.reset_mock()
        
        # Test remove from category
        await channel_handler.remove_from_category(text_channel)
        text_channel.edit.assert_called_with(category=None)
        
    async def test_channel_error_handling(self, channel_handler, guild):
        """Test channel-related error handling."""
        # Setup
        error_channel_name = "invalid-channel"
        guild.create_text_channel.side_effect = discord.Forbidden(
            response=None,
            message="Missing Permissions"
        )
        
        # Test
        with pytest.raises(discord.Forbidden):
            await channel_handler.create_text_channel(
                guild,
                name=error_channel_name
            ) 