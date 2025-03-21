"""
Monitoring Module

This module implements system monitoring, health checks, and metrics collection.
It tracks bot performance, resource usage, and provides alerts for potential issues.
"""

import os
import time
import psutil
import logging
import asyncio
import discord
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from discord.ext import tasks
from config.features.monitoring_config import monitoring_config

logger = logging.getLogger(__name__)

class MonitoringModule:
    """
    Handles system monitoring, health checks, and metrics collection.
    """
    
    def __init__(self, bot: discord.Client):
        """
        Initialize the monitoring module.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
        self.metrics = {}
        self.health_status = {}
        self.start_time = time.time()
        self.command_counts = {}
        self.error_counts = {}
        self.response_times = []
        
        # Initialize metrics storage
        self._init_metrics_storage()
    
    def _init_metrics_storage(self):
        """Initialize the metrics storage structures."""
        self.metrics = {
            'command_usage': {},
            'error_rates': {},
            'response_times': [],
            'memory_usage': [],
            'cpu_usage': [],
            'api_latency': []
        }
    
    async def start_monitoring(self):
        """Start the monitoring tasks."""
        if monitoring_config.ENABLED:
            self.health_check_task.start()
            self.collect_metrics_task.start()
            logger.info("Monitoring tasks started")
    
    async def stop_monitoring(self):
        """Stop the monitoring tasks."""
        self.health_check_task.cancel()
        self.collect_metrics_task.cancel()
        logger.info("Monitoring tasks stopped")
    
    @tasks.loop(seconds=monitoring_config.HEALTH_CHECK_INTERVAL)
    async def health_check_task(self):
        """Perform regular health checks."""
        try:
            await self._check_system_health()
            await self._check_bot_health()
            await self._check_api_health()
            await self._process_health_alerts()
        except Exception as e:
            logger.error(f"Error in health check task: {e}")
    
    @tasks.loop(seconds=monitoring_config.METRICS_COLLECTION_INTERVAL)
    async def collect_metrics_task(self):
        """Collect and store system metrics."""
        try:
            await self._collect_system_metrics()
            await self._collect_bot_metrics()
            await self._process_metrics_alerts()
            await self._cleanup_old_metrics()
        except Exception as e:
            logger.error(f"Error in metrics collection task: {e}")
    
    async def _check_system_health(self):
        """Check system resource health."""
        try:
            # Get system metrics
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('/')
            
            # Update health status
            self.health_status.update({
                'memory_usage_percent': memory.percent,
                'cpu_usage_percent': cpu_percent,
                'disk_usage_percent': disk.percent,
                'last_check_time': datetime.now()
            })
            
            logger.debug(f"System health check completed: {self.health_status}")
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
    
    async def _check_bot_health(self):
        """Check bot's operational health."""
        try:
            # Check bot's connection status
            is_connected = self.bot.is_ready()
            latency = self.bot.latency * 1000  # Convert to milliseconds
            
            # Update health status
            self.health_status.update({
                'bot_connected': is_connected,
                'bot_latency_ms': latency,
                'uptime_seconds': time.time() - self.start_time
            })
            
            logger.debug(f"Bot health check completed: {self.health_status}")
        except Exception as e:
            logger.error(f"Error checking bot health: {e}")
    
    async def _check_api_health(self):
        """Check Discord API health."""
        try:
            # Perform a simple API test by fetching the bot's user info
            start_time = time.time()
            await self.bot.fetch_user(self.bot.user.id)
            api_latency = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Update health status
            self.health_status.update({
                'api_latency_ms': api_latency,
                'api_operational': True
            })
            
            logger.debug(f"API health check completed: {self.health_status}")
        except Exception as e:
            logger.error(f"Error checking API health: {e}")
            self.health_status.update({
                'api_operational': False,
                'api_error': str(e)
            })
    
    async def _process_health_alerts(self):
        """Process health check results and send alerts if needed."""
        try:
            alerts = []
            thresholds = monitoring_config.ALERT_THRESHOLDS
            
            # Check memory usage
            if self.health_status.get('memory_usage_percent', 0) > thresholds.get('memory_usage_percent', 90):
                alerts.append(f"⚠️ High memory usage: {self.health_status['memory_usage_percent']}%")
            
            # Check CPU usage
            if self.health_status.get('cpu_usage_percent', 0) > thresholds.get('cpu_usage_percent', 80):
                alerts.append(f"⚠️ High CPU usage: {self.health_status['cpu_usage_percent']}%")
            
            # Check API latency
            if self.health_status.get('api_latency_ms', 0) > thresholds.get('response_time_ms', 1000):
                alerts.append(f"⚠️ High API latency: {self.health_status['api_latency_ms']}ms")
            
            # Send alerts if any
            if alerts and monitoring_config.NOTIFICATION_CHANNEL_ID:
                channel = self.bot.get_channel(monitoring_config.NOTIFICATION_CHANNEL_ID)
                if channel:
                    alert_message = "**Health Check Alerts**\n" + "\n".join(alerts)
                    await channel.send(alert_message)
        except Exception as e:
            logger.error(f"Error processing health alerts: {e}")
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics."""
        try:
            metrics = monitoring_config.METRICS_TO_COLLECT
            
            if metrics.get('memory_usage', True):
                memory = psutil.virtual_memory()
                self.metrics['memory_usage'].append({
                    'timestamp': datetime.now(),
                    'value': memory.percent
                })
            
            if metrics.get('cpu_usage', True):
                cpu_percent = psutil.cpu_percent(interval=1)
                self.metrics['cpu_usage'].append({
                    'timestamp': datetime.now(),
                    'value': cpu_percent
                })
            
            logger.debug("System metrics collected successfully")
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def _collect_bot_metrics(self):
        """Collect bot-specific metrics."""
        try:
            metrics = monitoring_config.METRICS_TO_COLLECT
            
            if metrics.get('api_latency', True):
                self.metrics['api_latency'].append({
                    'timestamp': datetime.now(),
                    'value': self.bot.latency * 1000
                })
            
            if metrics.get('command_usage', True):
                self.metrics['command_usage'] = self.command_counts
            
            if metrics.get('error_rates', True):
                self.metrics['error_rates'] = self.error_counts
            
            if metrics.get('response_times', True):
                self.metrics['response_times'] = self.response_times[-100:]  # Keep last 100 responses
            
            logger.debug("Bot metrics collected successfully")
        except Exception as e:
            logger.error(f"Error collecting bot metrics: {e}")
    
    async def _process_metrics_alerts(self):
        """Process collected metrics and send alerts if needed."""
        try:
            alerts = []
            thresholds = monitoring_config.ALERT_THRESHOLDS
            
            # Calculate error rate
            total_commands = sum(self.command_counts.values())
            total_errors = sum(self.error_counts.values())
            if total_commands > 0:
                error_rate = total_errors / total_commands
                if error_rate > thresholds.get('error_rate', 0.1):
                    alerts.append(f"⚠️ High error rate: {error_rate:.2%}")
            
            # Calculate average response time
            if self.response_times:
                avg_response_time = sum(self.response_times) / len(self.response_times)
                if avg_response_time > thresholds.get('response_time_ms', 1000):
                    alerts.append(f"⚠️ High average response time: {avg_response_time:.2f}ms")
            
            # Send alerts if any
            if alerts and monitoring_config.NOTIFICATION_CHANNEL_ID:
                channel = self.bot.get_channel(monitoring_config.NOTIFICATION_CHANNEL_ID)
                if channel:
                    alert_message = "**Metrics Alerts**\n" + "\n".join(alerts)
                    await channel.send(alert_message)
        except Exception as e:
            logger.error(f"Error processing metrics alerts: {e}")
    
    async def _cleanup_old_metrics(self):
        """Clean up metrics older than the retention period."""
        try:
            retention_date = datetime.now() - timedelta(days=monitoring_config.RETENTION_DAYS)
            
            # Clean up time-series metrics
            for metric_type in ['memory_usage', 'cpu_usage', 'api_latency']:
                self.metrics[metric_type] = [
                    m for m in self.metrics[metric_type]
                    if m['timestamp'] > retention_date
                ]
            
            # Reset counters periodically
            if datetime.now().hour == 0 and datetime.now().minute == 0:
                self.command_counts = {}
                self.error_counts = {}
                self.response_times = []
            
            logger.debug("Old metrics cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up old metrics: {e}")
    
    def record_command_usage(self, command_name: str):
        """
        Record usage of a command.
        
        Args:
            command_name: Name of the command used
        """
        self.command_counts[command_name] = self.command_counts.get(command_name, 0) + 1
    
    def record_error(self, command_name: str):
        """
        Record an error occurrence for a command.
        
        Args:
            command_name: Name of the command that errored
        """
        self.error_counts[command_name] = self.error_counts.get(command_name, 0) + 1
    
    def record_response_time(self, response_time_ms: float):
        """
        Record a command response time.
        
        Args:
            response_time_ms: Response time in milliseconds
        """
        self.response_times.append(response_time_ms)
        if len(self.response_times) > 1000:  # Keep last 1000 response times
            self.response_times = self.response_times[-1000:]

# Global monitoring instance
monitoring: Optional[MonitoringModule] = None

def setup(bot: discord.Client) -> None:
    """
    Set up the monitoring module.
    
    Args:
        bot: The Discord bot instance
    """
    global monitoring
    
    if not monitoring_config.ENABLED:
        logger.info("Monitoring module is disabled")
        return
    
    try:
        monitoring = MonitoringModule(bot)
        asyncio.create_task(monitoring.start_monitoring())
        logger.info("Monitoring module initialized successfully")
    except Exception as e:
        logger.error(f"Error setting up monitoring module: {e}")

def teardown(bot: discord.Client) -> None:
    """
    Clean up the monitoring module.
    
    Args:
        bot: The Discord bot instance
    """
    global monitoring
    
    if monitoring:
        asyncio.create_task(monitoring.stop_monitoring())
        monitoring = None
        logger.info("Monitoring module shut down successfully") 