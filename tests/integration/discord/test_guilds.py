"""
Integration tests for Discord guild management.
"""
import pytest
import discord
from unittest.mock import AsyncMock, patch, call
from core.bot import DiscordBot
from core.guild_handler import GuildHandler

@pytest.mark.integration
class TestGuildHandling:
    """Integration test suite for Discord guild management."""
    
    @pytest.fixture
    async def bot(self):
        """Fixture to provide a bot instance."""
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        bot = DiscordBot(command_prefix="!", intents=intents)
        await bot._async_setup()
        yield bot
        await bot._async_cleanup()
        
    @pytest.fixture
    async def guild_handler(self, bot):
        """Fixture to provide a guild handler instance."""
        return GuildHandler(bot)
        
    @pytest.fixture
    async def guild(self):
        """Fixture to provide a mock guild."""
        guild = AsyncMock(spec=discord.Guild)
        guild.id = 123456789
        guild.name = "Test Guild"
        return guild
        
    @pytest.fixture
    async def member(self, guild):
        """Fixture to provide a mock member."""
        member = AsyncMock(spec=discord.Member)
        member.guild = guild
        member.id = 111222333
        member.name = "TestUser"
        return member
        
    @pytest.fixture
    async def role(self, guild):
        """Fixture to provide a mock role."""
        role = AsyncMock(spec=discord.Role)
        role.guild = guild
        role.id = 444555666
        role.name = "TestRole"
        return role
        
    async def test_guild_info(self, guild_handler, guild):
        """Test retrieving guild information."""
        # Test
        info = await guild_handler.get_guild_info(guild)
        
        # Verify
        assert info["id"] == guild.id
        assert info["name"] == guild.name
        assert info["member_count"] == guild.member_count
        assert info["owner"] == guild.owner
        assert info["region"] == guild.region
        
    async def test_guild_settings(self, guild_handler, guild):
        """Test modifying guild settings."""
        # Setup
        new_name = "Updated Guild"
        new_region = "us-west"
        
        # Test
        await guild_handler.modify_guild(
            guild,
            name=new_name,
            region=new_region,
            verification_level=discord.VerificationLevel.high
        )
        
        # Verify
        guild.edit.assert_called_once_with(
            name=new_name,
            region=new_region,
            verification_level=discord.VerificationLevel.high
        )
        
    async def test_guild_bans(self, guild_handler, guild, member):
        """Test guild ban management."""
        # Test ban member
        reason = "Test ban reason"
        await guild_handler.ban_member(guild, member, reason=reason)
        guild.ban.assert_called_once_with(
            member,
            reason=reason,
            delete_message_days=0
        )
        
        # Test unban member
        await guild_handler.unban_member(guild, member)
        guild.unban.assert_called_once_with(member)
        
        # Test get bans
        await guild_handler.get_bans(guild)
        guild.bans.assert_called_once()
        
    async def test_guild_kicks(self, guild_handler, guild, member):
        """Test guild kick management."""
        # Setup
        reason = "Test kick reason"
        
        # Test
        await guild_handler.kick_member(guild, member, reason=reason)
        
        # Verify
        guild.kick.assert_called_once_with(
            member,
            reason=reason
        )
        
    async def test_guild_members(self, guild_handler, guild):
        """Test guild member management."""
        # Setup
        members = [
            AsyncMock(spec=discord.Member) for _ in range(3)
        ]
        guild.members = members
        
        # Test get members
        result = await guild_handler.get_members(guild)
        assert len(result) == len(members)
        
        # Test member search
        search_query = "test"
        await guild_handler.search_members(guild, search_query)
        guild.search_members.assert_called_once_with(search_query)
        
    async def test_guild_channels(self, guild_handler, guild):
        """Test guild channel management."""
        # Setup
        channels = [
            AsyncMock(spec=discord.TextChannel) for _ in range(3)
        ]
        guild.channels = channels
        
        # Test get channels
        result = await guild_handler.get_channels(guild)
        assert len(result) == len(channels)
        
        # Test channel cleanup
        await guild_handler.cleanup_channels(guild)
        for channel in channels:
            channel.delete.assert_called_once()
            
    async def test_guild_roles(self, guild_handler, guild):
        """Test guild role management."""
        # Setup
        roles = [
            AsyncMock(spec=discord.Role) for _ in range(3)
        ]
        guild.roles = roles
        
        # Test get roles
        result = await guild_handler.get_roles(guild)
        assert len(result) == len(roles)
        
        # Test role cleanup
        await guild_handler.cleanup_roles(guild)
        for role in roles:
            role.delete.assert_called_once()
            
    async def test_guild_emojis(self, guild_handler, guild):
        """Test guild emoji management."""
        # Setup
        emoji_name = "test_emoji"
        emoji_image = b"test_image_data"
        
        # Test create emoji
        await guild_handler.create_emoji(
            guild,
            name=emoji_name,
            image=emoji_image
        )
        guild.create_custom_emoji.assert_called_once_with(
            name=emoji_name,
            image=emoji_image
        )
        
        # Test get emojis
        await guild_handler.get_emojis(guild)
        assert guild.emojis is not None
        
    async def test_guild_invites(self, guild_handler, guild):
        """Test guild invite management."""
        # Setup
        max_age = 3600
        max_uses = 10
        
        # Test create invite
        await guild_handler.create_invite(
            guild,
            max_age=max_age,
            max_uses=max_uses
        )
        guild.create_invite.assert_called_once_with(
            max_age=max_age,
            max_uses=max_uses
        )
        
        # Test get invites
        await guild_handler.get_invites(guild)
        guild.invites.assert_called_once()
        
    async def test_guild_webhooks(self, guild_handler, guild):
        """Test guild webhook management."""
        # Test get webhooks
        await guild_handler.get_webhooks(guild)
        guild.webhooks.assert_called_once()
        
    async def test_guild_audit_logs(self, guild_handler, guild):
        """Test guild audit log access."""
        # Setup
        limit = 10
        action = discord.AuditLogAction.ban
        
        # Test
        await guild_handler.get_audit_logs(
            guild,
            limit=limit,
            action=action
        )
        
        # Verify
        guild.audit_logs.assert_called_once_with(
            limit=limit,
            action=action
        )
        
    async def test_guild_voice_regions(self, guild_handler, guild):
        """Test guild voice region management."""
        # Test get voice regions
        await guild_handler.get_voice_regions(guild)
        guild.voice_regions.assert_called_once()
        
    async def test_guild_verification_level(self, guild_handler, guild):
        """Test guild verification level management."""
        # Setup
        level = discord.VerificationLevel.high
        
        # Test
        await guild_handler.set_verification_level(guild, level)
        
        # Verify
        guild.edit.assert_called_once_with(
            verification_level=level
        )
        
    async def test_guild_system_channel(self, guild_handler, guild):
        """Test guild system channel management."""
        # Setup
        channel = AsyncMock(spec=discord.TextChannel)
        
        # Test
        await guild_handler.set_system_channel(guild, channel)
        
        # Verify
        guild.edit.assert_called_once_with(
            system_channel=channel
        )
        
    async def test_guild_features(self, guild_handler, guild):
        """Test guild feature management."""
        # Test get features
        features = await guild_handler.get_features(guild)
        assert features == guild.features
        
    async def test_guild_integrations(self, guild_handler, guild):
        """Test guild integration management."""
        # Test get integrations
        await guild_handler.get_integrations(guild)
        guild.integrations.assert_called_once()
        
    async def test_guild_widget(self, guild_handler, guild):
        """Test guild widget management."""
        # Setup
        enabled = True
        channel = AsyncMock(spec=discord.TextChannel)
        
        # Test
        await guild_handler.set_widget(guild, enabled, channel)
        
        # Verify
        guild.edit_widget.assert_called_once_with(
            enabled=enabled,
            channel=channel
        )
        
    async def test_guild_error_handling(self, guild_handler, guild, member):
        """Test guild-related error handling."""
        # Setup
        guild.ban.side_effect = discord.Forbidden(
            response=None,
            message="Missing Permissions"
        )
        
        # Test
        with pytest.raises(discord.Forbidden):
            await guild_handler.ban_member(
                guild,
                member,
                reason="Test error"
            ) 