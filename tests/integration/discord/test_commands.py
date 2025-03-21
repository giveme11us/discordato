"""
Integration tests for Discord command interactions.
"""
import pytest
import discord
from discord import app_commands
from unittest.mock import AsyncMock, patch
from core.bot import DiscordBot
from core.command_sync import register_command

@pytest.mark.integration
class TestCommandInteractions:
    """Integration test suite for Discord command interactions."""
    
    @pytest.fixture
    async def bot(self):
        """Fixture to provide a bot instance."""
        intents = discord.Intents.default()
        intents.message_content = True
        bot = DiscordBot(command_prefix="!", intents=intents)
        await bot._async_setup()  # Initialize bot systems
        yield bot
        await bot._async_cleanup()  # Cleanup
        
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
    async def user(self):
        """Fixture to provide a mock user."""
        user = AsyncMock(spec=discord.User)
        user.id = 111222333
        user.name = "TestUser"
        return user
        
    @pytest.fixture
    async def member(self, user, guild):
        """Fixture to provide a mock guild member."""
        member = AsyncMock(spec=discord.Member)
        member.id = user.id
        member.name = user.name
        member.guild = guild
        member.guild_permissions = discord.Permissions(administrator=True)
        return member
        
    async def test_command_registration(self, bot):
        """Test command registration and syncing."""
        # Setup
        @bot.tree.command(
            name="test_command",
            description="Test command description"
        )
        async def test_command(interaction: discord.Interaction):
            await interaction.response.send_message("Test response")
            
        # Test
        commands = await bot.tree.sync()
        
        # Verify
        assert any(cmd.name == "test_command" for cmd in commands)
        assert "test_command" in bot.tree._commands
        
    async def test_command_execution(self, bot, member, channel):
        """Test command execution and response."""
        # Setup
        response_content = "Test command executed"
        
        @bot.tree.command(
            name="execute_test",
            description="Test command execution"
        )
        async def execute_test(interaction: discord.Interaction):
            await interaction.response.send_message(response_content)
            
        await bot.tree.sync()
        
        # Create mock interaction
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.user = member
        interaction.channel = channel
        interaction.guild = channel.guild
        
        # Test
        command = bot.tree.get_command("execute_test")
        await command.callback(interaction)
        
        # Verify
        interaction.response.send_message.assert_called_once_with(response_content)
        
    async def test_command_parameters(self, bot, member, channel):
        """Test command parameter handling."""
        # Setup
        @bot.tree.command(
            name="param_test",
            description="Test command parameters"
        )
        @app_commands.describe(
            text="A text parameter",
            number="A number parameter"
        )
        async def param_test(
            interaction: discord.Interaction,
            text: str,
            number: int
        ):
            await interaction.response.send_message(
                f"Received: text='{text}', number={number}"
            )
            
        await bot.tree.sync()
        
        # Create mock interaction
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.user = member
        interaction.channel = channel
        interaction.guild = channel.guild
        
        # Test
        command = bot.tree.get_command("param_test")
        await command.callback(interaction, text="test", number=42)
        
        # Verify
        interaction.response.send_message.assert_called_once_with(
            "Received: text='test', number=42"
        )
        
    async def test_command_permissions(self, bot, member, channel):
        """Test command permission handling."""
        # Setup
        @bot.tree.command(
            name="admin_command",
            description="Admin only command"
        )
        @app_commands.checks.has_permissions(administrator=True)
        async def admin_command(interaction: discord.Interaction):
            await interaction.response.send_message("Admin command executed")
            
        await bot.tree.sync()
        
        # Test with admin permissions
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.user = member
        interaction.channel = channel
        interaction.guild = channel.guild
        
        command = bot.tree.get_command("admin_command")
        await command.callback(interaction)
        
        # Verify success
        interaction.response.send_message.assert_called_once_with(
            "Admin command executed"
        )
        
        # Test with non-admin permissions
        member.guild_permissions = discord.Permissions(administrator=False)
        
        # Verify permission error
        with pytest.raises(app_commands.errors.MissingPermissions):
            await command.callback(interaction)
            
    async def test_command_cooldowns(self, bot, member, channel):
        """Test command cooldown functionality."""
        # Setup
        @bot.tree.command(
            name="cooldown_test",
            description="Test command cooldowns"
        )
        @app_commands.checks.cooldown(1, 60)  # 1 use per 60 seconds
        async def cooldown_test(interaction: discord.Interaction):
            await interaction.response.send_message("Command executed")
            
        await bot.tree.sync()
        
        # Create mock interaction
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.user = member
        interaction.channel = channel
        interaction.guild = channel.guild
        
        # Test first execution
        command = bot.tree.get_command("cooldown_test")
        await command.callback(interaction)
        
        # Verify success
        interaction.response.send_message.assert_called_once_with(
            "Command executed"
        )
        
        # Test second execution
        with pytest.raises(app_commands.errors.CommandOnCooldown):
            await command.callback(interaction)
            
    async def test_command_error_handling(self, bot, member, channel):
        """Test command error handling."""
        # Setup
        @bot.tree.command(
            name="error_test",
            description="Test error handling"
        )
        async def error_test(interaction: discord.Interaction):
            raise ValueError("Test error")
            
        @bot.tree.error
        async def on_command_error(
            interaction: discord.Interaction,
            error: app_commands.AppCommandError
        ):
            await interaction.response.send_message(
                f"Error: {str(error)}", ephemeral=True
            )
            
        await bot.tree.sync()
        
        # Create mock interaction
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.user = member
        interaction.channel = channel
        interaction.guild = channel.guild
        
        # Test
        command = bot.tree.get_command("error_test")
        await command.callback(interaction)
        
        # Verify error handling
        interaction.response.send_message.assert_called_once_with(
            "Error: Test error",
            ephemeral=True
        )
        
    async def test_command_groups(self, bot, member, channel):
        """Test command group functionality."""
        # Setup
        group = app_commands.Group(
            name="test_group",
            description="Test command group"
        )
        
        @group.command(name="subcommand")
        async def group_subcommand(interaction: discord.Interaction):
            await interaction.response.send_message("Subcommand executed")
            
        bot.tree.add_command(group)
        await bot.tree.sync()
        
        # Create mock interaction
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.user = member
        interaction.channel = channel
        interaction.guild = channel.guild
        
        # Test
        command = bot.tree.get_command("test_group subcommand")
        await command.callback(interaction)
        
        # Verify
        interaction.response.send_message.assert_called_once_with(
            "Subcommand executed"
        ) 