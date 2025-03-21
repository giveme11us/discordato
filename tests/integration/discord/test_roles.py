"""
Integration tests for Discord role and permission management.
"""
import pytest
import discord
from unittest.mock import AsyncMock, patch, call
from core.bot import DiscordBot
from core.role_handler import RoleHandler

@pytest.mark.integration
class TestRoleHandling:
    """Integration test suite for Discord role management."""
    
    @pytest.fixture
    async def bot(self):
        """Fixture to provide a bot instance."""
        intents = discord.Intents.default()
        intents.guild_members = True
        intents.guilds = True
        bot = DiscordBot(command_prefix="!", intents=intents)
        await bot._async_setup()
        yield bot
        await bot._async_cleanup()
        
    @pytest.fixture
    async def role_handler(self, bot):
        """Fixture to provide a role handler instance."""
        return RoleHandler(bot)
        
    @pytest.fixture
    async def guild(self):
        """Fixture to provide a mock guild."""
        guild = AsyncMock(spec=discord.Guild)
        guild.id = 123456789
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
        
    async def test_role_creation(self, role_handler, guild):
        """Test creating a new role."""
        # Setup
        role_name = "NewRole"
        permissions = discord.Permissions(
            send_messages=True,
            read_messages=True
        )
        color = discord.Color.blue()
        
        # Test
        role = await role_handler.create_role(
            guild,
            name=role_name,
            permissions=permissions,
            color=color,
            hoist=True,
            mentionable=True
        )
        
        # Verify
        guild.create_role.assert_called_once_with(
            name=role_name,
            permissions=permissions,
            color=color,
            hoist=True,
            mentionable=True
        )
        
    async def test_role_deletion(self, role_handler, role):
        """Test deleting a role."""
        # Test
        await role_handler.delete_role(role)
        
        # Verify
        role.delete.assert_called_once()
        
    async def test_role_modification(self, role_handler, role):
        """Test modifying role properties."""
        # Setup
        new_name = "UpdatedRole"
        new_permissions = discord.Permissions(administrator=True)
        new_color = discord.Color.red()
        
        # Test
        await role_handler.modify_role(
            role,
            name=new_name,
            permissions=new_permissions,
            color=new_color,
            hoist=False,
            mentionable=False
        )
        
        # Verify
        role.edit.assert_called_once_with(
            name=new_name,
            permissions=new_permissions,
            color=new_color,
            hoist=False,
            mentionable=False
        )
        
    async def test_role_assignment(self, role_handler, member, role):
        """Test assigning roles to members."""
        # Test add role
        await role_handler.add_role(member, role)
        member.add_roles.assert_called_once_with(role)
        
        # Test remove role
        await role_handler.remove_role(member, role)
        member.remove_roles.assert_called_once_with(role)
        
    async def test_role_hierarchy(self, role_handler, guild, role):
        """Test role hierarchy management."""
        # Setup
        positions = {role: 5}
        
        # Test
        await role_handler.set_role_positions(guild, positions)
        
        # Verify
        guild.edit_role_positions.assert_called_once_with(positions)
        
    async def test_role_permissions(self, role_handler, role):
        """Test role permission management."""
        # Setup
        permissions = discord.Permissions(
            manage_messages=True,
            kick_members=True
        )
        
        # Test
        await role_handler.set_permissions(role, permissions)
        
        # Verify
        role.edit.assert_called_once_with(permissions=permissions)
        
    async def test_role_color(self, role_handler, role):
        """Test role color management."""
        # Setup
        color = discord.Color.green()
        
        # Test
        await role_handler.set_color(role, color)
        
        # Verify
        role.edit.assert_called_once_with(color=color)
        
    async def test_role_mentionable(self, role_handler, role):
        """Test role mentionable status."""
        # Test enable mentionable
        await role_handler.set_mentionable(role, True)
        role.edit.assert_called_with(mentionable=True)
        
        # Reset mock
        role.edit.reset_mock()
        
        # Test disable mentionable
        await role_handler.set_mentionable(role, False)
        role.edit.assert_called_with(mentionable=False)
        
    async def test_role_hoisting(self, role_handler, role):
        """Test role hoisting (display separately)."""
        # Test enable hoisting
        await role_handler.set_hoisted(role, True)
        role.edit.assert_called_with(hoist=True)
        
        # Reset mock
        role.edit.reset_mock()
        
        # Test disable hoisting
        await role_handler.set_hoisted(role, False)
        role.edit.assert_called_with(hoist=False)
        
    async def test_role_bulk_assignment(self, role_handler, member):
        """Test bulk role assignment."""
        # Setup
        roles = [
            AsyncMock(spec=discord.Role) for _ in range(3)
        ]
        
        # Test add roles
        await role_handler.bulk_add_roles(member, roles)
        member.add_roles.assert_called_once_with(*roles)
        
        # Test remove roles
        await role_handler.bulk_remove_roles(member, roles)
        member.remove_roles.assert_called_once_with(*roles)
        
    async def test_role_sync(self, role_handler, guild):
        """Test role synchronization."""
        # Setup
        template_roles = [
            {
                "name": "Admin",
                "permissions": discord.Permissions(administrator=True),
                "color": discord.Color.red()
            },
            {
                "name": "Moderator",
                "permissions": discord.Permissions(manage_messages=True),
                "color": discord.Color.blue()
            }
        ]
        
        # Test
        await role_handler.sync_roles(guild, template_roles)
        
        # Verify
        assert guild.create_role.call_count == len(template_roles)
        
    async def test_role_cleanup(self, role_handler, guild):
        """Test role cleanup operations."""
        # Setup
        unused_roles = [
            AsyncMock(spec=discord.Role) for _ in range(2)
        ]
        guild.roles = unused_roles
        
        # Test
        await role_handler.cleanup_unused_roles(guild)
        
        # Verify
        for role in unused_roles:
            role.delete.assert_called_once()
            
    async def test_role_info(self, role_handler, role):
        """Test role information retrieval."""
        # Test
        info = await role_handler.get_role_info(role)
        
        # Verify
        assert info["id"] == role.id
        assert info["name"] == role.name
        assert info["permissions"] == role.permissions
        assert info["color"] == role.color
        assert info["hoist"] == role.hoist
        assert info["mentionable"] == role.mentionable
        
    async def test_role_member_list(self, role_handler, role, guild):
        """Test retrieving members with a specific role."""
        # Setup
        members = [
            AsyncMock(spec=discord.Member) for _ in range(3)
        ]
        role.members = members
        
        # Test
        result = await role_handler.get_role_members(role)
        
        # Verify
        assert len(result) == len(members)
        assert all(member in result for member in members)
        
    async def test_role_permission_check(self, role_handler, member, role):
        """Test permission checking for roles."""
        # Setup
        permission = "manage_messages"
        role.permissions.manage_messages = True
        member.roles = [role]
        
        # Test
        has_permission = await role_handler.check_permission(
            member,
            permission
        )
        
        # Verify
        assert has_permission
        
    async def test_role_error_handling(self, role_handler, guild):
        """Test role-related error handling."""
        # Setup
        error_role_name = "NonexistentRole"
        guild.create_role.side_effect = discord.Forbidden(
            response=None,
            message="Missing Permissions"
        )
        
        # Test
        with pytest.raises(discord.Forbidden):
            await role_handler.create_role(guild, name=error_role_name) 