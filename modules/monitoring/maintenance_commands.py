"""
Maintenance Commands

This module implements commands for system maintenance tasks.
"""

import discord
from discord import app_commands
from typing import Optional, Literal
from datetime import datetime
import logging
from .utils.maintenance import MaintenanceUtils
from .module import monitoring
from .utils.permissions import require_monitoring_role

logger = logging.getLogger(__name__)

# Initialize maintenance utilities
maintenance = MaintenanceUtils()

def register_maintenance_commands(bot: discord.Client, registered_commands: set) -> None:
    """
    Register maintenance commands.
    
    Args:
        bot: The Discord bot instance
        registered_commands: Set of registered command names
    """
    logger.info("Registering maintenance commands")
    
    @bot.tree.command(
        name="maintenance-backup",
        description="Create or manage configuration backups"
    )
    @require_monitoring_role()
    @app_commands.describe(
        action="The backup action to perform",
        backup_file="The backup file to restore from (for restore action)"
    )
    async def backup_command(
        interaction: discord.Interaction,
        action: Literal["create", "list", "restore", "cleanup"],
        backup_file: Optional[str] = None
    ):
        """Manage configuration backups."""
        try:
            if action == "create":
                # Create new backup
                backup_path = maintenance.backup_config()
                if backup_path:
                    await interaction.response.send_message(
                        f"Created backup: `{backup_path}`",
                        ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        "Failed to create backup. Check logs for details.",
                        ephemeral=True
                    )
            
            elif action == "list":
                # List available backups
                backups = maintenance.list_backups()
                if backups:
                    # Create embed with backup information
                    embed = discord.Embed(
                        title="Configuration Backups",
                        description="Available backup files",
                        color=discord.Color.blue()
                    )
                    
                    for backup in backups[:10]:  # Show latest 10 backups
                        size_mb = backup['size_bytes'] / (1024 * 1024)
                        embed.add_field(
                            name=backup['filename'],
                            value=f"Size: {size_mb:.1f}MB\n"
                                  f"Created: {backup['created_at'].strftime('%Y-%m-%d %H:%M:%S')}",
                            inline=False
                        )
                    
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    await interaction.response.send_message(
                        "No backup files found.",
                        ephemeral=True
                    )
            
            elif action == "restore":
                if not backup_file:
                    await interaction.response.send_message(
                        "Please specify a backup file to restore from.",
                        ephemeral=True
                    )
                    return
                
                # Restore from backup
                success = maintenance.restore_config(backup_file)
                if success:
                    await interaction.response.send_message(
                        f"Successfully restored configuration from `{backup_file}`",
                        ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        "Failed to restore configuration. Check logs for details.",
                        ephemeral=True
                    )
            
            elif action == "cleanup":
                # Clean up old backups
                removed = maintenance.cleanup_old_backups()
                await interaction.response.send_message(
                    f"Cleaned up {removed} old backup files.",
                    ephemeral=True
                )
            
        except Exception as e:
            await interaction.response.send_message(
                f"Error performing backup action: {str(e)}",
                ephemeral=True
            )
    
    @bot.tree.command(
        name="maintenance-logs",
        description="Manage log files"
    )
    @require_monitoring_role()
    @app_commands.describe(
        action="The log management action to perform",
        max_size="Maximum log file size in MB (for rotate action)",
        max_files="Maximum number of backup files to keep (for rotate action)"
    )
    async def logs_command(
        interaction: discord.Interaction,
        action: Literal["rotate", "status"],
        max_size: Optional[int] = 10,
        max_files: Optional[int] = 5
    ):
        """Manage log files."""
        try:
            if action == "rotate":
                # Rotate log files
                maintenance.rotate_logs(max_size, max_files)
                await interaction.response.send_message(
                    f"Rotated logs (max size: {max_size}MB, max files: {max_files})",
                    ephemeral=True
                )
            
            elif action == "status":
                # Get disk usage information
                usage = maintenance.get_disk_usage()
                if 'logs' in usage:
                    log_usage = usage['logs']
                    size_mb = log_usage['size_bytes'] / (1024 * 1024)
                    
                    embed = discord.Embed(
                        title="Log Files Status",
                        color=discord.Color.blue()
                    )
                    
                    embed.add_field(
                        name="Storage Usage",
                        value=f"Size: {size_mb:.1f}MB\n"
                              f"Files: {log_usage['file_count']}",
                        inline=False
                    )
                    
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    await interaction.response.send_message(
                        "Failed to get log status. Check logs for details.",
                        ephemeral=True
                    )
            
        except Exception as e:
            await interaction.response.send_message(
                f"Error managing logs: {str(e)}",
                ephemeral=True
            )
    
    @bot.tree.command(
        name="maintenance-cleanup",
        description="Clean up temporary files and old data"
    )
    @require_monitoring_role()
    @app_commands.describe(
        target="What to clean up",
        max_age="Maximum age of files to keep (in days)"
    )
    async def cleanup_command(
        interaction: discord.Interaction,
        target: Literal["temp", "all"],
        max_age: Optional[int] = 7
    ):
        """Clean up temporary files and old data."""
        try:
            cleanup_results = []
            
            if target in ["temp", "all"]:
                # Clean up temp files
                temp_files = maintenance.cleanup_temp_files(max_age)
                cleanup_results.append(f"Cleaned up {temp_files} temporary files")
            
            if target == "all":
                # Clean up old backups
                old_backups = maintenance.cleanup_old_backups()
                cleanup_results.append(f"Cleaned up {old_backups} old backup files")
                
                # Clean up old metrics if monitoring is active
                if monitoring:
                    await monitoring._cleanup_old_metrics()
                    cleanup_results.append("Cleaned up old metrics data")
            
            await interaction.response.send_message(
                "Cleanup Results:\n" + "\n".join(cleanup_results),
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.response.send_message(
                f"Error during cleanup: {str(e)}",
                ephemeral=True
            )
    
    @bot.tree.command(
        name="maintenance-status",
        description="Show system maintenance status"
    )
    @require_monitoring_role()
    async def status_command(interaction: discord.Interaction):
        """Show system maintenance status."""
        logger.debug(f"User {interaction.user} ({interaction.user.id}) attempting to use maintenance-status command")
        logger.debug(f"User roles: {[role.name for role in interaction.user.roles]}")
        
        try:
            # Get disk usage information
            usage = maintenance.get_disk_usage()
            
            embed = discord.Embed(
                title="System Maintenance Status",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            # Storage Usage
            total_size = sum(data['size_bytes'] for data in usage.values())
            total_files = sum(data['file_count'] for data in usage.values())
            
            embed.add_field(
                name="Storage Overview",
                value=f"Total Size: {total_size / (1024*1024):.1f}MB\n"
                      f"Total Files: {total_files}",
                inline=False
            )
            
            # Detailed Usage
            for category, data in usage.items():
                size_mb = data['size_bytes'] / (1024 * 1024)
                embed.add_field(
                    name=f"{category.title()} Usage",
                    value=f"Size: {size_mb:.1f}MB\n"
                          f"Files: {data['file_count']}",
                    inline=True
                )
            
            # Backup Status
            backups = maintenance.list_backups()
            latest_backup = backups[0] if backups else None
            
            if latest_backup:
                time_since = datetime.now() - latest_backup['created_at']
                embed.add_field(
                    name="Latest Backup",
                    value=f"File: {latest_backup['filename']}\n"
                          f"Age: {time_since.days}d {time_since.seconds//3600}h ago",
                    inline=False
                )
            else:
                embed.add_field(
                    name="Latest Backup",
                    value="No backups found",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            logger.debug(f"Successfully displayed maintenance status for user {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error getting maintenance status: {e}", exc_info=True)
            await interaction.response.send_message(
                f"Error getting maintenance status: {str(e)}",
                ephemeral=True
            )
    
    # Register commands
    registered_commands.add("maintenance-backup")
    registered_commands.add("maintenance-logs")
    registered_commands.add("maintenance-cleanup")
    registered_commands.add("maintenance-status") 