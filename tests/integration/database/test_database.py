"""
Integration tests for database operations.
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from core.database import DatabaseHandler
from core.models import (
    User,
    Guild,
    Channel,
    Role,
    Message,
    VoiceState,
    CustomCommand,
    AutoResponse,
    Reminder,
    Warning,
    Statistics
)

@pytest.mark.integration
class TestDatabaseOperations:
    """Integration test suite for database operations."""
    
    @pytest.fixture
    async def db_handler(self):
        """Fixture to provide a database handler instance."""
        handler = DatabaseHandler(
            host="localhost",
            port=5432,
            database="test_db",
            user="test_user",
            password="test_password"
        )
        await handler.connect()
        await handler.setup_tables()
        yield handler
        await handler.cleanup_tables()
        await handler.disconnect()
        
    async def test_user_operations(self, db_handler):
        """Test user-related database operations."""
        # Setup
        user_data = {
            "id": 123456789,
            "name": "TestUser",
            "discriminator": "1234",
            "created_at": datetime.utcnow(),
            "bot": False
        }
        
        # Test create
        user = await db_handler.create_user(user_data)
        assert user.id == user_data["id"]
        
        # Test read
        retrieved_user = await db_handler.get_user(user.id)
        assert retrieved_user.name == user_data["name"]
        
        # Test update
        updated_name = "UpdatedUser"
        await db_handler.update_user(user.id, {"name": updated_name})
        updated_user = await db_handler.get_user(user.id)
        assert updated_user.name == updated_name
        
        # Test delete
        await db_handler.delete_user(user.id)
        deleted_user = await db_handler.get_user(user.id)
        assert deleted_user is None
        
    async def test_guild_operations(self, db_handler):
        """Test guild-related database operations."""
        # Setup
        guild_data = {
            "id": 987654321,
            "name": "Test Guild",
            "owner_id": 123456789,
            "created_at": datetime.utcnow(),
            "region": "us-west"
        }
        
        # Test create
        guild = await db_handler.create_guild(guild_data)
        assert guild.id == guild_data["id"]
        
        # Test read
        retrieved_guild = await db_handler.get_guild(guild.id)
        assert retrieved_guild.name == guild_data["name"]
        
        # Test update
        updated_name = "Updated Guild"
        await db_handler.update_guild(guild.id, {"name": updated_name})
        updated_guild = await db_handler.get_guild(guild.id)
        assert updated_guild.name == updated_name
        
        # Test delete
        await db_handler.delete_guild(guild.id)
        deleted_guild = await db_handler.get_guild(guild.id)
        assert deleted_guild is None
        
    async def test_channel_operations(self, db_handler):
        """Test channel-related database operations."""
        # Setup
        channel_data = {
            "id": 111222333,
            "guild_id": 987654321,
            "name": "test-channel",
            "type": "text",
            "position": 0,
            "created_at": datetime.utcnow()
        }
        
        # Test create
        channel = await db_handler.create_channel(channel_data)
        assert channel.id == channel_data["id"]
        
        # Test read
        retrieved_channel = await db_handler.get_channel(channel.id)
        assert retrieved_channel.name == channel_data["name"]
        
        # Test update
        updated_name = "updated-channel"
        await db_handler.update_channel(channel.id, {"name": updated_name})
        updated_channel = await db_handler.get_channel(channel.id)
        assert updated_channel.name == updated_name
        
        # Test delete
        await db_handler.delete_channel(channel.id)
        deleted_channel = await db_handler.get_channel(channel.id)
        assert deleted_channel is None
        
    async def test_role_operations(self, db_handler):
        """Test role-related database operations."""
        # Setup
        role_data = {
            "id": 444555666,
            "guild_id": 987654321,
            "name": "Test Role",
            "color": 0xFF0000,
            "position": 1,
            "permissions": 0
        }
        
        # Test create
        role = await db_handler.create_role(role_data)
        assert role.id == role_data["id"]
        
        # Test read
        retrieved_role = await db_handler.get_role(role.id)
        assert retrieved_role.name == role_data["name"]
        
        # Test update
        updated_name = "Updated Role"
        await db_handler.update_role(role.id, {"name": updated_name})
        updated_role = await db_handler.get_role(role.id)
        assert updated_role.name == updated_name
        
        # Test delete
        await db_handler.delete_role(role.id)
        deleted_role = await db_handler.get_role(role.id)
        assert deleted_role is None
        
    async def test_message_operations(self, db_handler):
        """Test message-related database operations."""
        # Setup
        message_data = {
            "id": 777888999,
            "channel_id": 111222333,
            "author_id": 123456789,
            "content": "Test message",
            "created_at": datetime.utcnow()
        }
        
        # Test create
        message = await db_handler.create_message(message_data)
        assert message.id == message_data["id"]
        
        # Test read
        retrieved_message = await db_handler.get_message(message.id)
        assert retrieved_message.content == message_data["content"]
        
        # Test update
        updated_content = "Updated message"
        await db_handler.update_message(message.id, {"content": updated_content})
        updated_message = await db_handler.get_message(message.id)
        assert updated_message.content == updated_content
        
        # Test delete
        await db_handler.delete_message(message.id)
        deleted_message = await db_handler.get_message(message.id)
        assert deleted_message is None
        
    async def test_custom_command_operations(self, db_handler):
        """Test custom command-related database operations."""
        # Setup
        command_data = {
            "guild_id": 987654321,
            "name": "testcmd",
            "response": "Test response",
            "created_by": 123456789,
            "created_at": datetime.utcnow()
        }
        
        # Test create
        command = await db_handler.create_custom_command(command_data)
        assert command.name == command_data["name"]
        
        # Test read
        retrieved_command = await db_handler.get_custom_command(
            command_data["guild_id"],
            command_data["name"]
        )
        assert retrieved_command.response == command_data["response"]
        
        # Test update
        updated_response = "Updated response"
        await db_handler.update_custom_command(
            command_data["guild_id"],
            command_data["name"],
            {"response": updated_response}
        )
        updated_command = await db_handler.get_custom_command(
            command_data["guild_id"],
            command_data["name"]
        )
        assert updated_command.response == updated_response
        
        # Test delete
        await db_handler.delete_custom_command(
            command_data["guild_id"],
            command_data["name"]
        )
        deleted_command = await db_handler.get_custom_command(
            command_data["guild_id"],
            command_data["name"]
        )
        assert deleted_command is None
        
    async def test_auto_response_operations(self, db_handler):
        """Test auto-response-related database operations."""
        # Setup
        response_data = {
            "guild_id": 987654321,
            "trigger": "test trigger",
            "response": "Test response",
            "created_by": 123456789,
            "created_at": datetime.utcnow()
        }
        
        # Test create
        response = await db_handler.create_auto_response(response_data)
        assert response.trigger == response_data["trigger"]
        
        # Test read
        retrieved_response = await db_handler.get_auto_response(
            response_data["guild_id"],
            response_data["trigger"]
        )
        assert retrieved_response.response == response_data["response"]
        
        # Test update
        updated_response = "Updated response"
        await db_handler.update_auto_response(
            response_data["guild_id"],
            response_data["trigger"],
            {"response": updated_response}
        )
        updated_auto_response = await db_handler.get_auto_response(
            response_data["guild_id"],
            response_data["trigger"]
        )
        assert updated_auto_response.response == updated_response
        
        # Test delete
        await db_handler.delete_auto_response(
            response_data["guild_id"],
            response_data["trigger"]
        )
        deleted_response = await db_handler.get_auto_response(
            response_data["guild_id"],
            response_data["trigger"]
        )
        assert deleted_response is None
        
    async def test_reminder_operations(self, db_handler):
        """Test reminder-related database operations."""
        # Setup
        reminder_data = {
            "user_id": 123456789,
            "channel_id": 111222333,
            "message": "Test reminder",
            "remind_at": datetime.utcnow() + timedelta(hours=1),
            "created_at": datetime.utcnow()
        }
        
        # Test create
        reminder = await db_handler.create_reminder(reminder_data)
        assert reminder.message == reminder_data["message"]
        
        # Test read
        retrieved_reminder = await db_handler.get_reminder(reminder.id)
        assert retrieved_reminder.message == reminder_data["message"]
        
        # Test update
        updated_message = "Updated reminder"
        await db_handler.update_reminder(
            reminder.id,
            {"message": updated_message}
        )
        updated_reminder = await db_handler.get_reminder(reminder.id)
        assert updated_reminder.message == updated_message
        
        # Test delete
        await db_handler.delete_reminder(reminder.id)
        deleted_reminder = await db_handler.get_reminder(reminder.id)
        assert deleted_reminder is None
        
    async def test_warning_operations(self, db_handler):
        """Test warning-related database operations."""
        # Setup
        warning_data = {
            "guild_id": 987654321,
            "user_id": 123456789,
            "moderator_id": 999888777,
            "reason": "Test warning",
            "created_at": datetime.utcnow()
        }
        
        # Test create
        warning = await db_handler.create_warning(warning_data)
        assert warning.reason == warning_data["reason"]
        
        # Test read
        retrieved_warning = await db_handler.get_warning(warning.id)
        assert retrieved_warning.reason == warning_data["reason"]
        
        # Test update
        updated_reason = "Updated warning"
        await db_handler.update_warning(
            warning.id,
            {"reason": updated_reason}
        )
        updated_warning = await db_handler.get_warning(warning.id)
        assert updated_warning.reason == updated_reason
        
        # Test delete
        await db_handler.delete_warning(warning.id)
        deleted_warning = await db_handler.get_warning(warning.id)
        assert deleted_warning is None
        
    async def test_statistics_operations(self, db_handler):
        """Test statistics-related database operations."""
        # Setup
        stats_data = {
            "guild_id": 987654321,
            "messages_sent": 100,
            "commands_used": 50,
            "voice_minutes": 120,
            "date": datetime.utcnow().date()
        }
        
        # Test create
        stats = await db_handler.create_statistics(stats_data)
        assert stats.messages_sent == stats_data["messages_sent"]
        
        # Test read
        retrieved_stats = await db_handler.get_statistics(
            stats_data["guild_id"],
            stats_data["date"]
        )
        assert retrieved_stats.messages_sent == stats_data["messages_sent"]
        
        # Test update
        updated_messages = 150
        await db_handler.update_statistics(
            stats_data["guild_id"],
            stats_data["date"],
            {"messages_sent": updated_messages}
        )
        updated_stats = await db_handler.get_statistics(
            stats_data["guild_id"],
            stats_data["date"]
        )
        assert updated_stats.messages_sent == updated_messages
        
        # Test delete
        await db_handler.delete_statistics(
            stats_data["guild_id"],
            stats_data["date"]
        )
        deleted_stats = await db_handler.get_statistics(
            stats_data["guild_id"],
            stats_data["date"]
        )
        assert deleted_stats is None
        
    async def test_bulk_operations(self, db_handler):
        """Test bulk database operations."""
        # Setup
        users = [
            {
                "id": i,
                "name": f"User{i}",
                "discriminator": "0000",
                "created_at": datetime.utcnow(),
                "bot": False
            }
            for i in range(1, 4)
        ]
        
        # Test bulk create
        created_users = await db_handler.bulk_create_users(users)
        assert len(created_users) == len(users)
        
        # Test bulk read
        user_ids = [user["id"] for user in users]
        retrieved_users = await db_handler.bulk_get_users(user_ids)
        assert len(retrieved_users) == len(users)
        
        # Test bulk update
        updates = [
            {"id": user["id"], "name": f"Updated{user['name']}"}
            for user in users
        ]
        await db_handler.bulk_update_users(updates)
        updated_users = await db_handler.bulk_get_users(user_ids)
        assert all(
            user.name.startswith("Updated")
            for user in updated_users
        )
        
        # Test bulk delete
        await db_handler.bulk_delete_users(user_ids)
        remaining_users = await db_handler.bulk_get_users(user_ids)
        assert len(remaining_users) == 0
        
    async def test_transaction_operations(self, db_handler):
        """Test database transaction operations."""
        async with db_handler.transaction():
            # Create user
            user_data = {
                "id": 123456789,
                "name": "TransactionUser",
                "discriminator": "1234",
                "created_at": datetime.utcnow(),
                "bot": False
            }
            user = await db_handler.create_user(user_data)
            
            # Create guild
            guild_data = {
                "id": 987654321,
                "name": "Transaction Guild",
                "owner_id": user.id,
                "created_at": datetime.utcnow(),
                "region": "us-west"
            }
            guild = await db_handler.create_guild(guild_data)
            
            # Verify both exist
            assert await db_handler.get_user(user.id) is not None
            assert await db_handler.get_guild(guild.id) is not None
            
        # Test transaction rollback
        try:
            async with db_handler.transaction():
                # Create valid user
                await db_handler.create_user(user_data)
                
                # Attempt invalid operation to trigger rollback
                await db_handler.create_user({"invalid": "data"})
        except:
            pass
            
        # Verify rollback occurred
        assert await db_handler.get_user(user_data["id"]) is None 