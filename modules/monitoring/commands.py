"""
Monitoring Commands

This module implements the commands for the monitoring system.
"""

import discord
from discord import app_commands
from typing import Optional, Literal
from datetime import datetime, timedelta
from .module import monitoring
from config.features.monitoring_config import monitoring_config
from .utils.permissions import require_monitoring_role

def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds to a human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        str: Formatted duration string
    """
    days, remainder = divmod(int(seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)

def format_bytes(bytes: int) -> str:
    """
    Format bytes to a human-readable string.
    
    Args:
        bytes: Number of bytes
        
    Returns:
        str: Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f}{unit}"
        bytes /= 1024
    return f"{bytes:.1f}TB"

def register_commands(bot: discord.Client, registered_commands: set) -> None:
    """
    Register monitoring commands.
    
    Args:
        bot: The Discord bot instance
        registered_commands: Set of registered command names
    """
    
    @bot.tree.command(
        name="monitor-status",
        description="Show current system status and health metrics"
    )
    @require_monitoring_role()
    async def status_command(interaction: discord.Interaction):
        """Display current system status and health metrics."""
        if not monitoring:
            await interaction.response.send_message("Monitoring system is not active.", ephemeral=True)
            return
        
        # Create status embed
        embed = discord.Embed(
            title="System Status",
            description="Current system health and metrics",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        # System Health
        health_status = monitoring.health_status
        memory_usage = health_status.get('memory_usage_percent', 0)
        cpu_usage = health_status.get('cpu_usage_percent', 0)
        disk_usage = health_status.get('disk_usage_percent', 0)
        
        embed.add_field(
            name="System Health",
            value=f"Memory: {memory_usage:.1f}%\n"
                  f"CPU: {cpu_usage:.1f}%\n"
                  f"Disk: {disk_usage:.1f}%",
            inline=True
        )
        
        # Bot Health
        uptime = format_duration(health_status.get('uptime_seconds', 0))
        bot_latency = health_status.get('bot_latency_ms', 0)
        api_latency = health_status.get('api_latency_ms', 0)
        
        embed.add_field(
            name="Bot Health",
            value=f"Uptime: {uptime}\n"
                  f"Bot Latency: {bot_latency:.1f}ms\n"
                  f"API Latency: {api_latency:.1f}ms",
            inline=True
        )
        
        # Command Stats
        total_commands = sum(monitoring.command_counts.values())
        total_errors = sum(monitoring.error_counts.values())
        error_rate = (total_errors / total_commands * 100) if total_commands > 0 else 0
        
        embed.add_field(
            name="Command Statistics",
            value=f"Total Commands: {total_commands}\n"
                  f"Total Errors: {total_errors}\n"
                  f"Error Rate: {error_rate:.1f}%",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(
        name="monitor-config",
        description="Configure the monitoring system"
    )
    @require_monitoring_role()
    @app_commands.describe(
        setting="The setting to configure",
        value="The new value for the setting"
    )
    async def config_command(
        interaction: discord.Interaction,
        setting: Literal["health_interval", "metrics_interval", "notification_channel", "retention_days"],
        value: str
    ):
        """Configure monitoring system settings."""
        try:
            if setting == "health_interval":
                interval = int(value)
                if interval < 60:
                    await interaction.response.send_message("Health check interval must be at least 60 seconds.", ephemeral=True)
                    return
                monitoring_config.HEALTH_CHECK_INTERVAL = interval
                await interaction.response.send_message(f"Health check interval set to {interval} seconds.", ephemeral=True)
            
            elif setting == "metrics_interval":
                interval = int(value)
                if interval < 30:
                    await interaction.response.send_message("Metrics collection interval must be at least 30 seconds.", ephemeral=True)
                    return
                monitoring_config.METRICS_COLLECTION_INTERVAL = interval
                await interaction.response.send_message(f"Metrics collection interval set to {interval} seconds.", ephemeral=True)
            
            elif setting == "notification_channel":
                if value.lower() == "none":
                    monitoring_config.NOTIFICATION_CHANNEL_ID = None
                    await interaction.response.send_message("Notification channel disabled.", ephemeral=True)
                else:
                    try:
                        channel_id = int(value)
                        channel = interaction.guild.get_channel(channel_id)
                        if not channel:
                            await interaction.response.send_message("Invalid channel ID.", ephemeral=True)
                            return
                        monitoring_config.NOTIFICATION_CHANNEL_ID = channel_id
                        await interaction.response.send_message(f"Notification channel set to {channel.mention}.", ephemeral=True)
                    except ValueError:
                        await interaction.response.send_message("Invalid channel ID format.", ephemeral=True)
            
            elif setting == "retention_days":
                days = int(value)
                if days < 1:
                    await interaction.response.send_message("Retention period must be at least 1 day.", ephemeral=True)
                    return
                monitoring_config.RETENTION_DAYS = days
                await interaction.response.send_message(f"Metrics retention period set to {days} days.", ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("Invalid value format.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error updating configuration: {str(e)}", ephemeral=True)
    
    @bot.tree.command(
        name="monitor-metrics",
        description="Show detailed metrics for a specific aspect of the system"
    )
    @require_monitoring_role()
    @app_commands.describe(
        metric_type="The type of metric to view",
        timeframe="The timeframe to view (in hours)"
    )
    async def metrics_command(
        interaction: discord.Interaction,
        metric_type: Literal["memory", "cpu", "commands", "errors", "latency"],
        timeframe: Optional[int] = 24
    ):
        """Display detailed metrics for a specific aspect."""
        if not monitoring:
            await interaction.response.send_message("Monitoring system is not active.", ephemeral=True)
            return
        
        try:
            # Validate timeframe
            if timeframe < 1 or timeframe > 168:  # Max 1 week
                await interaction.response.send_message("Timeframe must be between 1 and 168 hours.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title=f"{metric_type.title()} Metrics",
                description=f"Last {timeframe} hours",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            cutoff_time = datetime.now() - timedelta(hours=timeframe)
            
            if metric_type == "memory":
                # Memory usage metrics
                recent_memory = [m for m in monitoring.metrics['memory_usage'] if m['timestamp'] > cutoff_time]
                if recent_memory:
                    avg_memory = sum(m['value'] for m in recent_memory) / len(recent_memory)
                    max_memory = max(m['value'] for m in recent_memory)
                    embed.add_field(
                        name="Memory Usage",
                        value=f"Average: {avg_memory:.1f}%\n"
                              f"Maximum: {max_memory:.1f}%\n"
                              f"Samples: {len(recent_memory)}",
                        inline=False
                    )
                else:
                    embed.add_field(name="Memory Usage", value="No data available", inline=False)
            
            elif metric_type == "cpu":
                # CPU usage metrics
                recent_cpu = [m for m in monitoring.metrics['cpu_usage'] if m['timestamp'] > cutoff_time]
                if recent_cpu:
                    avg_cpu = sum(m['value'] for m in recent_cpu) / len(recent_cpu)
                    max_cpu = max(m['value'] for m in recent_cpu)
                    embed.add_field(
                        name="CPU Usage",
                        value=f"Average: {avg_cpu:.1f}%\n"
                              f"Maximum: {max_cpu:.1f}%\n"
                              f"Samples: {len(recent_cpu)}",
                        inline=False
                    )
                else:
                    embed.add_field(name="CPU Usage", value="No data available", inline=False)
            
            elif metric_type == "commands":
                # Command usage metrics
                total_commands = sum(monitoring.command_counts.values())
                if total_commands > 0:
                    # Sort commands by usage
                    sorted_commands = sorted(
                        monitoring.command_counts.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )
                    # Show top 10 commands
                    command_stats = "\n".join(
                        f"{cmd}: {count} ({count/total_commands*100:.1f}%)"
                        for cmd, count in sorted_commands[:10]
                    )
                    embed.add_field(
                        name="Command Usage (Top 10)",
                        value=command_stats,
                        inline=False
                    )
                else:
                    embed.add_field(name="Command Usage", value="No commands recorded", inline=False)
            
            elif metric_type == "errors":
                # Error metrics
                total_errors = sum(monitoring.error_counts.values())
                if total_errors > 0:
                    # Sort errors by frequency
                    sorted_errors = sorted(
                        monitoring.error_counts.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )
                    # Show top 10 errors
                    error_stats = "\n".join(
                        f"{cmd}: {count} errors"
                        for cmd, count in sorted_errors[:10]
                    )
                    embed.add_field(
                        name="Error Distribution (Top 10)",
                        value=error_stats,
                        inline=False
                    )
                else:
                    embed.add_field(name="Errors", value="No errors recorded", inline=False)
            
            elif metric_type == "latency":
                # Latency metrics
                recent_latency = [m for m in monitoring.metrics['api_latency'] if m['timestamp'] > cutoff_time]
                if recent_latency:
                    avg_latency = sum(m['value'] for m in recent_latency) / len(recent_latency)
                    max_latency = max(m['value'] for m in recent_latency)
                    min_latency = min(m['value'] for m in recent_latency)
                    embed.add_field(
                        name="API Latency",
                        value=f"Average: {avg_latency:.1f}ms\n"
                              f"Maximum: {max_latency:.1f}ms\n"
                              f"Minimum: {min_latency:.1f}ms\n"
                              f"Samples: {len(recent_latency)}",
                        inline=False
                    )
                else:
                    embed.add_field(name="API Latency", value="No data available", inline=False)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"Error retrieving metrics: {str(e)}", ephemeral=True)
    
    # Register commands
    registered_commands.add("monitor-status")
    registered_commands.add("monitor-config")
    registered_commands.add("monitor-metrics") 