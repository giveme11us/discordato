"""
Integration tests for Discord member management.
"""
import pytest
import discord
from unittest.mock import AsyncMock, patch, call
from core.bot import DiscordBot
from core.member_handler import MemberHandler

@pytest.mark.integration
class TestMemberHandling:
    """Integration test suite for Discord member management."""
    
    @pytest.fixture
    async def bot(self):
        """Fixture to provide a bot instance."""
        intents = discord.Intents.default()
        intents.members = True
        intents.guilds = True
        bot = DiscordBot(command_prefix="!", intents=intents)
        await bot._async_setup()
        yield bot
        await bot._async_cleanup()
        
    @pytest.fixture
    async def member_handler(self, bot):
        """Fixture to provide a member handler instance."""
        return MemberHandler(bot)
        
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
        member.display_name = "Test User"
        member.nick = None
        return member
        
    @pytest.fixture
    async def role(self, guild):
        """Fixture to provide a mock role."""
        role = AsyncMock(spec=discord.Role)
        role.guild = guild
        role.id = 444555666
        role.name = "TestRole"
        return role
        
    async def test_member_info(self, member_handler, member):
        """Test retrieving member information."""
        # Test
        info = await member_handler.get_member_info(member)
        
        # Verify
        assert info["id"] == member.id
        assert info["name"] == member.name
        assert info["display_name"] == member.display_name
        assert info["nick"] == member.nick
        assert info["roles"] == member.roles
        assert info["joined_at"] == member.joined_at
        
    async def test_member_nickname(self, member_handler, member):
        """Test member nickname management."""
        # Setup
        new_nick = "New Nickname"
        
        # Test set nickname
        await member_handler.set_nickname(member, new_nick)
        member.edit.assert_called_once_with(nick=new_nick)
        
        # Reset mock
        member.edit.reset_mock()
        
        # Test remove nickname
        await member_handler.remove_nickname(member)
        member.edit.assert_called_once_with(nick=None)
        
    async def test_member_roles(self, member_handler, member, role):
        """Test member role management."""
        # Test add role
        await member_handler.add_role(member, role)
        member.add_roles.assert_called_once_with(role)
        
        # Test remove role
        await member_handler.remove_role(member, role)
        member.remove_roles.assert_called_once_with(role)
        
        # Test bulk add roles
        roles = [AsyncMock(spec=discord.Role) for _ in range(3)]
        await member_handler.bulk_add_roles(member, roles)
        member.add_roles.assert_called_with(*roles)
        
        # Test bulk remove roles
        await member_handler.bulk_remove_roles(member, roles)
        member.remove_roles.assert_called_with(*roles)
        
    async def test_member_permissions(self, member_handler, member):
        """Test member permission management."""
        # Setup
        permission = discord.Permissions(
            send_messages=True,
            read_messages=True
        )
        
        # Test check permission
        result = await member_handler.check_permissions(member, permission)
        assert isinstance(result, bool)
        
        # Test get permissions
        perms = await member_handler.get_permissions(member)
        assert isinstance(perms, discord.Permissions)
        
    async def test_member_timeout(self, member_handler, member):
        """Test member timeout management."""
        # Setup
        duration = 3600  # 1 hour in seconds
        reason = "Test timeout"
        
        # Test timeout member
        await member_handler.timeout_member(member, duration, reason)
        member.timeout.assert_called_once_with(
            duration=duration,
            reason=reason
        )
        
        # Test remove timeout
        await member_handler.remove_timeout(member)
        member.timeout.assert_called_with(None)
        
    async def test_member_voice_state(self, member_handler, member):
        """Test member voice state management."""
        # Setup
        voice_channel = AsyncMock(spec=discord.VoiceChannel)
        
        # Test move to channel
        await member_handler.move_to_voice_channel(member, voice_channel)
        member.move_to.assert_called_once_with(voice_channel)
        
        # Test disconnect from voice
        await member_handler.disconnect_from_voice(member)
        member.move_to.assert_called_with(None)
        
    async def test_member_dm(self, member_handler, member):
        """Test direct message management."""
        # Setup
        message_content = "Test DM"
        
        # Test send DM
        await member_handler.send_dm(member, message_content)
        member.send.assert_called_once_with(message_content)
        
    async def test_member_activity(self, member_handler, member):
        """Test member activity tracking."""
        # Test get activities
        activities = await member_handler.get_activities(member)
        assert activities == member.activities
        
        # Test get status
        status = await member_handler.get_status(member)
        assert status == member.status
        
    async def test_member_avatar(self, member_handler, member):
        """Test member avatar management."""
        # Setup
        avatar_bytes = b"test_avatar_data"
        
        # Test set avatar
        await member_handler.set_avatar(member, avatar_bytes)
        member.edit.assert_called_once_with(avatar=avatar_bytes)
        
        # Test get avatar URL
        avatar_url = await member_handler.get_avatar_url(member)
        assert avatar_url == member.avatar.url
        
    async def test_member_ban_kick(self, member_handler, member):
        """Test member ban and kick operations."""
        # Setup
        reason = "Test reason"
        
        # Test ban
        await member_handler.ban_member(member, reason=reason)
        member.ban.assert_called_once_with(reason=reason)
        
        # Test kick
        await member_handler.kick_member(member, reason=reason)
        member.kick.assert_called_once_with(reason=reason)
        
    async def test_member_mute(self, member_handler, member):
        """Test member mute management."""
        # Test server mute
        await member_handler.server_mute(member, True)
        member.edit.assert_called_with(mute=True)
        
        # Reset mock
        member.edit.reset_mock()
        
        # Test server unmute
        await member_handler.server_mute(member, False)
        member.edit.assert_called_with(mute=False)
        
    async def test_member_deafen(self, member_handler, member):
        """Test member deafen management."""
        # Test server deafen
        await member_handler.server_deafen(member, True)
        member.edit.assert_called_with(deafen=True)
        
        # Reset mock
        member.edit.reset_mock()
        
        # Test server undeafen
        await member_handler.server_deafen(member, False)
        member.edit.assert_called_with(deafen=False)
        
    async def test_member_history(self, member_handler, member):
        """Test member message history retrieval."""
        # Setup
        limit = 100
        
        # Test
        await member_handler.get_message_history(member, limit)
        member.history.assert_called_once_with(limit=limit)
        
    async def test_member_presence(self, member_handler, member):
        """Test member presence information."""
        # Test get presence
        presence = await member_handler.get_presence(member)
        assert presence == member.presence
        
        # Test get platform
        platform = await member_handler.get_platform(member)
        assert platform == member.desktop_status or member.mobile_status or member.web_status
        
    async def test_member_roles_hierarchy(self, member_handler, member, role):
        """Test member role hierarchy checks."""
        # Setup
        member.top_role = role
        
        # Test
        result = await member_handler.can_manage_role(member, role)
        assert isinstance(result, bool)
        
    async def test_member_search(self, member_handler, guild):
        """Test member search functionality."""
        # Setup
        query = "test"
        limit = 10
        
        # Test
        await member_handler.search_members(guild, query, limit)
        guild.search_members.assert_called_once_with(query, limit=limit)
        
    async def test_member_error_handling(self, member_handler, member):
        """Test member-related error handling."""
        # Setup
        member.edit.side_effect = discord.Forbidden(
            response=None,
            message="Missing Permissions"
        )
        
        # Test
        with pytest.raises(discord.Forbidden):
            await member_handler.set_nickname(
                member,
                "New Nick"
            ) 