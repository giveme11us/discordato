"""
Integration tests for Discord voice channel interactions.
"""
import pytest
import discord
from unittest.mock import AsyncMock, patch, call
from core.bot import DiscordBot
from core.voice_handler import VoiceHandler

@pytest.mark.integration
class TestVoiceHandling:
    """Integration test suite for Discord voice channel handling."""
    
    @pytest.fixture
    async def bot(self):
        """Fixture to provide a bot instance."""
        intents = discord.Intents.default()
        intents.voice_states = True
        bot = DiscordBot(command_prefix="!", intents=intents)
        await bot._async_setup()
        yield bot
        await bot._async_cleanup()
        
    @pytest.fixture
    async def voice_handler(self, bot):
        """Fixture to provide a voice handler instance."""
        return VoiceHandler(bot)
        
    @pytest.fixture
    async def guild(self):
        """Fixture to provide a mock guild."""
        guild = AsyncMock(spec=discord.Guild)
        guild.id = 123456789
        return guild
        
    @pytest.fixture
    async def voice_channel(self, guild):
        """Fixture to provide a mock voice channel."""
        channel = AsyncMock(spec=discord.VoiceChannel)
        channel.guild = guild
        channel.id = 987654321
        channel.name = "Test Voice Channel"
        return channel
        
    @pytest.fixture
    async def member(self, guild):
        """Fixture to provide a mock member."""
        member = AsyncMock(spec=discord.Member)
        member.guild = guild
        member.id = 111222333
        member.name = "TestUser"
        return member
        
    @pytest.fixture
    async def voice_client(self, guild, voice_channel):
        """Fixture to provide a mock voice client."""
        voice_client = AsyncMock(spec=discord.VoiceClient)
        voice_client.guild = guild
        voice_client.channel = voice_channel
        return voice_client
        
    async def test_voice_connect(self, voice_handler, voice_channel):
        """Test connecting to a voice channel."""
        # Test
        voice_client = await voice_handler.connect(voice_channel)
        
        # Verify
        assert voice_client.channel == voice_channel
        voice_channel.connect.assert_called_once()
        
    async def test_voice_disconnect(self, voice_handler, voice_client):
        """Test disconnecting from a voice channel."""
        # Setup
        voice_handler.voice_clients[voice_client.guild.id] = voice_client
        
        # Test
        await voice_handler.disconnect(voice_client.guild)
        
        # Verify
        voice_client.disconnect.assert_called_once()
        assert voice_client.guild.id not in voice_handler.voice_clients
        
    async def test_voice_move(self, voice_handler, voice_client, voice_channel):
        """Test moving between voice channels."""
        # Setup
        new_channel = AsyncMock(spec=discord.VoiceChannel)
        new_channel.id = 444555666
        new_channel.name = "New Voice Channel"
        new_channel.guild = voice_client.guild
        
        voice_handler.voice_clients[voice_client.guild.id] = voice_client
        
        # Test
        await voice_handler.move_to(voice_client.guild, new_channel)
        
        # Verify
        voice_client.move_to.assert_called_once_with(new_channel)
        
    async def test_voice_play_audio(self, voice_handler, voice_client):
        """Test playing audio in a voice channel."""
        # Setup
        audio_source = AsyncMock(spec=discord.AudioSource)
        
        # Test
        await voice_handler.play_audio(voice_client.guild, audio_source)
        
        # Verify
        voice_client.play.assert_called_once_with(
            audio_source,
            after=voice_handler.on_playback_finished
        )
        
    async def test_voice_pause_resume(self, voice_handler, voice_client):
        """Test pausing and resuming audio playback."""
        # Setup
        voice_handler.voice_clients[voice_client.guild.id] = voice_client
        
        # Test pause
        await voice_handler.pause(voice_client.guild)
        voice_client.pause.assert_called_once()
        
        # Test resume
        await voice_handler.resume(voice_client.guild)
        voice_client.resume.assert_called_once()
        
    async def test_voice_stop(self, voice_handler, voice_client):
        """Test stopping audio playback."""
        # Setup
        voice_handler.voice_clients[voice_client.guild.id] = voice_client
        
        # Test
        await voice_handler.stop(voice_client.guild)
        
        # Verify
        voice_client.stop.assert_called_once()
        
    async def test_voice_volume(self, voice_handler, voice_client):
        """Test volume control."""
        # Setup
        voice_handler.voice_clients[voice_client.guild.id] = voice_client
        new_volume = 0.5
        
        # Test
        await voice_handler.set_volume(voice_client.guild, new_volume)
        
        # Verify
        assert voice_client.source.volume == new_volume
        
    async def test_voice_effects(self, voice_handler, voice_client):
        """Test audio effects application."""
        # Setup
        voice_handler.voice_clients[voice_client.guild.id] = voice_client
        effect = "echo"
        
        # Test
        await voice_handler.apply_effect(voice_client.guild, effect)
        
        # Verify
        voice_client.source.set_effect.assert_called_once_with(effect)
        
    async def test_voice_queue(self, voice_handler, voice_client):
        """Test audio queue management."""
        # Setup
        guild_id = voice_client.guild.id
        voice_handler.voice_clients[guild_id] = voice_client
        
        audio_sources = [
            AsyncMock(spec=discord.AudioSource) for _ in range(3)
        ]
        
        # Test queue operations
        for source in audio_sources:
            await voice_handler.queue_audio(guild_id, source)
            
        assert len(voice_handler.get_queue(guild_id)) == 3
        
        # Test skip
        await voice_handler.skip(guild_id)
        voice_client.stop.assert_called_once()
        
        # Test clear queue
        await voice_handler.clear_queue(guild_id)
        assert len(voice_handler.get_queue(guild_id)) == 0
        
    async def test_voice_filters(self, voice_handler, voice_client):
        """Test audio filter application."""
        # Setup
        voice_handler.voice_clients[voice_client.guild.id] = voice_client
        filter_settings = {
            "bass": 1.5,
            "treble": 0.8,
            "normalize": True
        }
        
        # Test
        await voice_handler.apply_filters(
            voice_client.guild,
            filter_settings
        )
        
        # Verify
        voice_client.source.set_filter.assert_called_once_with(
            filter_settings
        )
        
    async def test_voice_recording(self, voice_handler, voice_client, member):
        """Test voice recording functionality."""
        # Setup
        voice_handler.voice_clients[voice_client.guild.id] = voice_client
        
        # Test start recording
        await voice_handler.start_recording(voice_client.guild, member)
        voice_client.start_recording.assert_called_once()
        
        # Test stop recording
        recording = await voice_handler.stop_recording(voice_client.guild)
        voice_client.stop_recording.assert_called_once()
        assert recording is not None
        
    async def test_voice_state_tracking(self, voice_handler, voice_client, member):
        """Test voice state change tracking."""
        # Setup
        guild_id = voice_client.guild.id
        voice_handler.voice_clients[guild_id] = voice_client
        
        # Test member join
        await voice_handler.on_voice_state_update(
            member,
            None,
            AsyncMock(spec=discord.VoiceState, channel=voice_client.channel)
        )
        assert member.id in voice_handler.get_voice_members(guild_id)
        
        # Test member leave
        await voice_handler.on_voice_state_update(
            member,
            AsyncMock(spec=discord.VoiceState, channel=voice_client.channel),
            AsyncMock(spec=discord.VoiceState, channel=None)
        )
        assert member.id not in voice_handler.get_voice_members(guild_id)
        
    async def test_voice_activity(self, voice_handler, voice_client, member):
        """Test voice activity detection."""
        # Setup
        voice_handler.voice_clients[voice_client.guild.id] = voice_client
        
        # Test
        await voice_handler.on_voice_activity(member, True)
        voice_client.on_voice_activity.assert_called_once_with(member, True)
        
    async def test_voice_error_handling(self, voice_handler, voice_client):
        """Test voice-related error handling."""
        # Setup
        guild_id = voice_client.guild.id
        voice_handler.voice_clients[guild_id] = voice_client
        error = Exception("Test error")
        
        # Test
        await voice_handler.on_voice_error(guild_id, error)
        
        # Verify error was handled and connection cleaned up
        assert guild_id not in voice_handler.voice_clients
        voice_client.disconnect.assert_called_once() 