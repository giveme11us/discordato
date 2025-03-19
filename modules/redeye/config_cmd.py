"""
Redeye Configuration Command

Provides a slash command interface for configuring the Redeye module features.
"""

import discord
from discord import app_commands
import logging
from config import redeye_config
from config import embed_config
from utils.permissions import redeye_only
import typing

logger = logging.getLogger('discord_bot.modules.redeye.config_cmd')

async def handle_redeye_config(interaction, setting=None, action=None, value=None):
    """
    Handle the redeye-config command.
    
    Args:
        interaction: The Discord interaction
        setting: The setting to view or modify
        action: The action to perform
        value: The value for the action
    """
    if not setting:
        # Show general configuration
        embed = discord.Embed(
            title="Redeye Configuration",
            description="Configure waitlists and role-based access for the Redeye module."
        )
        
        # Get current settings
        enabled = redeye_config.settings_manager.get("ENABLED", False)
        waitlists = redeye_config.settings_manager.get("WAITLISTS", {})
        role_requirements = redeye_config.settings_manager.get("ROLE_REQUIREMENTS", {})
        
        # Add status field
        embed.add_field(
            name="Status",
            value=f"{'✅ Enabled' if enabled else '❌ Disabled'}",
            inline=False
        )
        
        # Add waitlists field
        if waitlists:
            waitlist_text = "\n".join([f"• **{name}**: {data.get('description', 'No description')}" 
                                      for name, data in waitlists.items()])
        else:
            waitlist_text = "No waitlists configured."
            
        embed.add_field(
            name=f"Waitlists ({len(waitlists)})",
            value=waitlist_text,
            inline=False
        )
        
        # Add role requirements field
        if role_requirements:
            role_text = "\n".join([f"• **{waitlist_id}**: {len(roles)} role(s) configured" 
                                  for waitlist_id, roles in role_requirements.items()])
        else:
            role_text = "No role requirements configured."
            
        embed.add_field(
            name="Role Requirements",
            value=role_text,
            inline=False
        )
        
        # Add command help
        embed.add_field(
            name="Available Commands",
            value=(
                "• `/redeye-config` - Show current configuration\n"
                "• `/redeye-config enable:true/false` - Enable/disable the module\n"
                "• `/redeye-config waitlist:add/remove/view [name]` - Manage waitlists\n"
                "• `/redeye-config roles:add/remove/view [waitlist] [role]` - Manage role requirements"
            ),
            inline=False
        )
        
        # Apply styling from embed_config
        embed = embed_config.apply_default_styling(embed)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
        
    # Handle enable/disable
    if setting.lower() == "enable":
        if value is None:
            await interaction.response.send_message(
                "Please specify 'true' or 'false' to enable or disable the module.",
                ephemeral=True
            )
            return
            
        enable_value = value.lower() in ('true', '1', 't', 'yes', 'y', 'on')
        redeye_config.settings_manager.set("ENABLED", enable_value)
        
        if redeye_config.settings_manager.save_settings():
            await interaction.response.send_message(
                f"{'✅ Redeye module enabled.' if enable_value else '❌ Redeye module disabled.'}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Failed to save settings.",
                ephemeral=True
            )
        return
    
    # Here would be additional command handling for waitlists, roles, etc.
    # Structure in place, no implementation yet
    
    await interaction.response.send_message(
        f"The setting '{setting}' with action '{action}' and value '{value}' is not implemented yet.",
        ephemeral=True
    )

def setup_config_cmd(bot):
    """
    Register the redeye-config command.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Registering /redeye-config command")
    
    try:
        # Access settings directly from settings manager for environment checks only
        # The actual permission check will be handled by the decorator
        import os
        
        # Import the config module with a different name to avoid conflicts
        from config import redeye_config as redeye_config_module
        
        @app_commands.command(
            name="redeye-config",
            description="Configure the redeye module"
        )
        @app_commands.describe(
            action="The action to perform",
            waitlist_id="ID of the waitlist to configure (if applicable)",
            notification_channel="Channel for notifications (if applicable)",
            role_id="Role ID to associate with a waitlist (if applicable)"
        )
        @redeye_only()
        async def redeye_config_command(
            interaction: discord.Interaction,
            action: typing.Literal["enable", "disable", "status", "add-waitlist", "remove-waitlist", "list-waitlists", "set-notification-channel"],
            waitlist_id: str = None,
            notification_channel: discord.TextChannel = None,
            role_id: str = None
        ):
            """Configure the redeye module"""
            # No need for internal permission check - the decorator handles it
            
            # Process the action
            if action == "enable":
                redeye_config_module.settings_manager.set("ENABLED", True)
                redeye_config_module.save_config()
                await interaction.response.send_message("✅ Redeye module enabled", ephemeral=True)
            
            elif action == "disable":
                redeye_config_module.settings_manager.set("ENABLED", False)
                redeye_config_module.save_config()
                await interaction.response.send_message("✅ Redeye module disabled", ephemeral=True)
            
            elif action == "status":
                # Get current settings
                enabled = redeye_config_module.settings_manager.get("ENABLED", False)
                waitlists = redeye_config_module.settings_manager.get("WAITLISTS", {})
                role_requirements = redeye_config_module.settings_manager.get("ROLE_REQUIREMENTS", {})
                notification_channel_id = redeye_config_module.settings_manager.get("NOTIFICATION_CHANNEL_ID")
                
                # Create embed
                embed = discord.Embed(
                    title="Redeye Module Status",
                    description=f"Enabled: {'✅' if enabled else '❌'}",
                    color=discord.Color.green() if enabled else discord.Color.red()
                )
                
                # Add notification channel
                embed.add_field(
                    name="Notification Channel",
                    value=f"<#{notification_channel_id}>" if notification_channel_id else "Not set",
                    inline=False
                )
                
                # Add waitlists
                waitlist_text = ""
                if waitlists:
                    for wl_id, wl_info in waitlists.items():
                        role_text = ""
                        if wl_id in role_requirements:
                            for role_id in role_requirements[wl_id]:
                                role_text += f"<@&{role_id}> "
                        
                        waitlist_text += f"• {wl_id}: {len(wl_info.get('users', []))} users, Roles: {role_text or 'None'}\n"
                else:
                    waitlist_text = "No waitlists configured"
                
                embed.add_field(
                    name="Waitlists",
                    value=waitlist_text,
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            
            elif action == "add-waitlist":
                if not waitlist_id:
                    await interaction.response.send_message("❌ Please provide a waitlist ID", ephemeral=True)
                    return
                
                # Get current waitlists and role requirements
                waitlists = redeye_config_module.settings_manager.get("WAITLISTS", {})
                role_requirements = redeye_config_module.settings_manager.get("ROLE_REQUIREMENTS", {})
                
                # Add or update waitlist
                if waitlist_id not in waitlists:
                    waitlists[waitlist_id] = {"users": []}
                
                # Update role if provided
                if role_id:
                    try:
                        role_id_int = int(role_id)
                        if waitlist_id not in role_requirements:
                            role_requirements[waitlist_id] = []
                        
                        if role_id_int not in role_requirements[waitlist_id]:
                            role_requirements[waitlist_id].append(role_id_int)
                    except ValueError:
                        await interaction.response.send_message("❌ Invalid role ID format", ephemeral=True)
                        return
                
                # Save updated settings
                redeye_config_module.settings_manager.set("WAITLISTS", waitlists)
                redeye_config_module.settings_manager.set("ROLE_REQUIREMENTS", role_requirements)
                redeye_config_module.save_config()
                
                await interaction.response.send_message(f"✅ Waitlist '{waitlist_id}' added or updated", ephemeral=True)
            
            elif action == "remove-waitlist":
                if not waitlist_id:
                    await interaction.response.send_message("❌ Please provide a waitlist ID", ephemeral=True)
                    return
                
                # Get current waitlists and role requirements
                waitlists = redeye_config_module.settings_manager.get("WAITLISTS", {})
                role_requirements = redeye_config_module.settings_manager.get("ROLE_REQUIREMENTS", {})
                
                # Remove waitlist and role requirements
                if waitlist_id in waitlists:
                    waitlists.pop(waitlist_id)
                
                if waitlist_id in role_requirements:
                    role_requirements.pop(waitlist_id)
                
                # Save updated settings
                redeye_config_module.settings_manager.set("WAITLISTS", waitlists)
                redeye_config_module.settings_manager.set("ROLE_REQUIREMENTS", role_requirements)
                redeye_config_module.save_config()
                
                await interaction.response.send_message(f"✅ Waitlist '{waitlist_id}' removed", ephemeral=True)
            
            elif action == "list-waitlists":
                waitlists = redeye_config_module.settings_manager.get("WAITLISTS", {})
                
                if not waitlists:
                    await interaction.response.send_message("No waitlists configured", ephemeral=True)
                    return
                
                # Create text listing of waitlists
                waitlist_text = "📋 **Configured Waitlists**\n\n"
                for wl_id, wl_info in waitlists.items():
                    users_count = len(wl_info.get("users", []))
                    waitlist_text += f"• **{wl_id}**: {users_count} users\n"
                
                await interaction.response.send_message(waitlist_text, ephemeral=True)
            
            elif action == "set-notification-channel":
                if not notification_channel:
                    await interaction.response.send_message("❌ Please specify a notification channel", ephemeral=True)
                    return
                
                # Save notification channel ID
                redeye_config_module.settings_manager.set("NOTIFICATION_CHANNEL_ID", notification_channel.id)
                redeye_config_module.save_config()
                
                await interaction.response.send_message(f"✅ Notification channel set to {notification_channel.mention}", ephemeral=True)
        
        # Add command to bot tree
        bot.tree.add_command(redeye_config_command)
        logger.info("Successfully registered /redeye-config command")
    
    except Exception as e:
        logger.error(f"Error registering /redeye-config command: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise 