"""
Unit tests for permission system.
"""
import pytest
from unittest.mock import Mock, patch
from discord import Member, Role, Permissions as DiscordPermissions
from core.permissions import PermissionManager, PermissionError, Permission

@pytest.mark.unit
class TestPermissionSystem:
    """Test suite for permission management functionality."""
    
    @pytest.fixture
    def permission_manager(self):
        """Fixture to provide a permission manager instance."""
        return PermissionManager()
        
    @pytest.fixture
    def mock_member(self):
        """Fixture to provide a mock Discord member."""
        member = Mock(spec=Member)
        member.guild_permissions = DiscordPermissions()
        member.roles = []
        return member
        
    @pytest.fixture
    def mock_role(self):
        """Fixture to provide a mock Discord role."""
        role = Mock(spec=Role)
        role.permissions = DiscordPermissions()
        role.id = 123456789
        return role
        
    def test_permission_registration(self, permission_manager):
        """Test permission registration."""
        # Setup
        permission = Permission("test.permission", "Test permission")
        
        # Test
        permission_manager.register_permission(permission)
        
        # Verify
        assert permission.name in permission_manager.permissions
        assert permission_manager.permissions[permission.name] == permission
        
    def test_duplicate_permission_registration(self, permission_manager):
        """Test handling of duplicate permission registration."""
        # Setup
        permission = Permission("test.permission", "Test permission")
        
        # Register first time
        permission_manager.register_permission(permission)
        
        # Test registering again
        with pytest.raises(PermissionError, match="Permission already registered"):
            permission_manager.register_permission(permission)
            
    def test_role_permission_assignment(self, permission_manager, mock_role):
        """Test assigning permissions to roles."""
        # Setup
        permission = Permission("test.permission", "Test permission")
        permission_manager.register_permission(permission)
        
        # Test
        permission_manager.assign_role_permission(mock_role.id, permission.name)
        
        # Verify
        assert permission.name in permission_manager.role_permissions.get(mock_role.id, set())
        
    def test_member_permission_check(self, permission_manager, mock_member, mock_role):
        """Test checking member permissions."""
        # Setup
        permission = Permission("test.permission", "Test permission")
        permission_manager.register_permission(permission)
        mock_member.roles = [mock_role]
        
        # Assign permission to role
        permission_manager.assign_role_permission(mock_role.id, permission.name)
        
        # Test
        assert permission_manager.has_permission(mock_member, permission.name)
        
    def test_permission_inheritance(self, permission_manager, mock_member, mock_role):
        """Test permission inheritance system."""
        # Setup
        parent_perm = Permission("admin", "Admin permission")
        child_perm = Permission("admin.user", "User management permission")
        grandchild_perm = Permission("admin.user.create", "User creation permission")
        
        permission_manager.register_permission(parent_perm)
        permission_manager.register_permission(child_perm)
        permission_manager.register_permission(grandchild_perm)
        
        mock_member.roles = [mock_role]
        
        # Assign parent permission to role
        permission_manager.assign_role_permission(mock_role.id, parent_perm.name)
        
        # Test
        assert permission_manager.has_permission(mock_member, parent_perm.name)
        assert permission_manager.has_permission(mock_member, child_perm.name)
        assert permission_manager.has_permission(mock_member, grandchild_perm.name)
        
    def test_permission_wildcards(self, permission_manager, mock_member, mock_role):
        """Test wildcard permission handling."""
        # Setup
        permission_manager.register_permission(Permission("module.*", "All module permissions"))
        mock_member.roles = [mock_role]
        
        # Assign wildcard permission
        permission_manager.assign_role_permission(mock_role.id, "module.*")
        
        # Test various permissions under the wildcard
        assert permission_manager.has_permission(mock_member, "module.create")
        assert permission_manager.has_permission(mock_member, "module.delete")
        assert permission_manager.has_permission(mock_member, "module.modify")
        
    def test_discord_permission_integration(self, permission_manager, mock_member):
        """Test integration with Discord's permission system."""
        # Setup
        mock_member.guild_permissions.administrator = True
        
        # Test
        assert permission_manager.has_permission(mock_member, "any.permission")
        
    def test_temporary_permissions(self, permission_manager, mock_member, mock_role):
        """Test temporary permission assignments."""
        # Setup
        permission = Permission("temp.permission", "Temporary permission")
        permission_manager.register_permission(permission)
        mock_member.roles = [mock_role]
        
        # Test
        permission_manager.assign_temporary_permission(
            mock_role.id,
            permission.name,
            duration_seconds=1
        )
        
        # Verify immediate access
        assert permission_manager.has_permission(mock_member, permission.name)
        
        # Verify expiration
        import asyncio
        asyncio.run(asyncio.sleep(1.1))
        assert not permission_manager.has_permission(mock_member, permission.name)
        
    def test_permission_revocation(self, permission_manager, mock_member, mock_role):
        """Test permission revocation."""
        # Setup
        permission = Permission("test.permission", "Test permission")
        permission_manager.register_permission(permission)
        mock_member.roles = [mock_role]
        
        # Assign permission
        permission_manager.assign_role_permission(mock_role.id, permission.name)
        assert permission_manager.has_permission(mock_member, permission.name)
        
        # Test revocation
        permission_manager.revoke_role_permission(mock_role.id, permission.name)
        assert not permission_manager.has_permission(mock_member, permission.name)
        
    def test_permission_conflicts(self, permission_manager, mock_member):
        """Test handling of permission conflicts between roles."""
        # Setup
        permission = Permission("test.permission", "Test permission")
        permission_manager.register_permission(permission)
        
        allow_role = Mock(spec=Role, id=1)
        deny_role = Mock(spec=Role, id=2)
        mock_member.roles = [allow_role, deny_role]
        
        # Assign conflicting permissions
        permission_manager.assign_role_permission(allow_role.id, permission.name)
        permission_manager.deny_role_permission(deny_role.id, permission.name)
        
        # Test (deny should take precedence)
        assert not permission_manager.has_permission(mock_member, permission.name)
        
    def test_bulk_permission_operations(self, permission_manager, mock_role):
        """Test bulk permission operations."""
        # Setup
        permissions = [
            Permission("test.create", "Create permission"),
            Permission("test.read", "Read permission"),
            Permission("test.update", "Update permission"),
            Permission("test.delete", "Delete permission")
        ]
        
        # Test bulk registration
        permission_manager.register_permissions(permissions)
        
        # Verify all permissions are registered
        for permission in permissions:
            assert permission.name in permission_manager.permissions
            
        # Test bulk assignment
        permission_names = [p.name for p in permissions]
        permission_manager.assign_role_permissions(mock_role.id, permission_names)
        
        # Verify all permissions are assigned
        role_perms = permission_manager.role_permissions.get(mock_role.id, set())
        assert all(name in role_perms for name in permission_names)
        
    def test_permission_validation(self, permission_manager):
        """Test permission validation."""
        # Test invalid permission name
        with pytest.raises(PermissionError, match="Invalid permission name"):
            Permission("", "Empty permission name")
            
        with pytest.raises(PermissionError, match="Invalid permission name"):
            Permission("invalid.*.permission", "Invalid wildcard usage")
            
        # Test invalid permission description
        with pytest.raises(PermissionError, match="Permission description required"):
            Permission("test.permission", "") 