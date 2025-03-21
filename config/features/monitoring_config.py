"""
Configuration for the monitoring module.
Handles settings for health checks and metrics collection.
"""
import os
from typing import Dict, Any, List
import logging
from config.core.base_config import BaseConfig

logger = logging.getLogger(__name__)

# Default settings
DEFAULT_CONFIG = {
    "ENABLED": True,
    "HEALTH_CHECK_INTERVAL": 300,  # 5 minutes
    "METRICS_COLLECTION_INTERVAL": 60,  # 1 minute
    "NOTIFICATION_CHANNEL_ID": None,
    "ALERT_THRESHOLDS": {
        "memory_usage_percent": 90,  # Alert when memory usage is above 90%
        "cpu_usage_percent": 80,     # Alert when CPU usage is above 80%
        "error_rate": 0.1,           # Alert when error rate is above 10%
        "response_time_ms": 1000     # Alert when response time is above 1000ms
    },
    "METRICS_TO_COLLECT": {
        "command_usage": True,
        "error_rates": True,
        "response_times": True,
        "memory_usage": True,
        "cpu_usage": True,
        "api_latency": True
    },
    "RETENTION_DAYS": 30  # How long to keep metrics data
}

class MonitoringConfig(BaseConfig):
    """
    Configuration class for the monitoring module.
    Handles settings for system monitoring and metrics collection.
    """
    
    def __init__(self):
        """Initialize the monitoring configuration."""
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'data',
            'monitoring_config.json'
        )
        super().__init__(config_path, DEFAULT_CONFIG, version="1.0.0")
    
    @property
    def ENABLED(self) -> bool:
        """Whether the monitoring module is enabled."""
        return self.get("ENABLED", True)
    
    @ENABLED.setter
    def ENABLED(self, value: bool) -> None:
        """Set whether the monitoring module is enabled."""
        self.set("ENABLED", value)
    
    @property
    def HEALTH_CHECK_INTERVAL(self) -> int:
        """Get the health check interval in seconds."""
        return self.get("HEALTH_CHECK_INTERVAL", 300)
    
    @HEALTH_CHECK_INTERVAL.setter
    def HEALTH_CHECK_INTERVAL(self, value: int) -> None:
        """Set the health check interval in seconds."""
        self.set("HEALTH_CHECK_INTERVAL", value)
    
    @property
    def METRICS_COLLECTION_INTERVAL(self) -> int:
        """Get the metrics collection interval in seconds."""
        return self.get("METRICS_COLLECTION_INTERVAL", 60)
    
    @METRICS_COLLECTION_INTERVAL.setter
    def METRICS_COLLECTION_INTERVAL(self, value: int) -> None:
        """Set the metrics collection interval in seconds."""
        self.set("METRICS_COLLECTION_INTERVAL", value)
    
    @property
    def NOTIFICATION_CHANNEL_ID(self) -> int:
        """Get the notification channel ID."""
        return self.get("NOTIFICATION_CHANNEL_ID")
    
    @NOTIFICATION_CHANNEL_ID.setter
    def NOTIFICATION_CHANNEL_ID(self, value: int) -> None:
        """Set the notification channel ID."""
        self.set("NOTIFICATION_CHANNEL_ID", value)
    
    @property
    def ALERT_THRESHOLDS(self) -> Dict[str, float]:
        """Get the alert thresholds."""
        return self.get("ALERT_THRESHOLDS", {})
    
    @ALERT_THRESHOLDS.setter
    def ALERT_THRESHOLDS(self, value: Dict[str, float]) -> None:
        """Set the alert thresholds."""
        self.set("ALERT_THRESHOLDS", value)
    
    @property
    def METRICS_TO_COLLECT(self) -> Dict[str, bool]:
        """Get the metrics collection settings."""
        return self.get("METRICS_TO_COLLECT", {})
    
    @METRICS_TO_COLLECT.setter
    def METRICS_TO_COLLECT(self, value: Dict[str, bool]) -> None:
        """Set the metrics collection settings."""
        self.set("METRICS_TO_COLLECT", value)
    
    @property
    def RETENTION_DAYS(self) -> int:
        """Get the metrics retention period in days."""
        return self.get("RETENTION_DAYS", 30)
    
    @RETENTION_DAYS.setter
    def RETENTION_DAYS(self, value: int) -> None:
        """Set the metrics retention period in days."""
        self.set("RETENTION_DAYS", value)
    
    def validate_config(self) -> bool:
        """
        Validate the monitoring configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if not super().validate_config():
            return False
            
        try:
            # Validate intervals
            if not isinstance(self.HEALTH_CHECK_INTERVAL, int) or self.HEALTH_CHECK_INTERVAL <= 0:
                logger.warning("HEALTH_CHECK_INTERVAL must be a positive integer")
                return False
                
            if not isinstance(self.METRICS_COLLECTION_INTERVAL, int) or self.METRICS_COLLECTION_INTERVAL <= 0:
                logger.warning("METRICS_COLLECTION_INTERVAL must be a positive integer")
                return False
            
            # Validate notification channel
            if self.NOTIFICATION_CHANNEL_ID is not None and not isinstance(self.NOTIFICATION_CHANNEL_ID, int):
                logger.warning("NOTIFICATION_CHANNEL_ID must be an integer")
                return False
            
            # Validate alert thresholds
            for key, value in self.ALERT_THRESHOLDS.items():
                if not isinstance(value, (int, float)) or value < 0:
                    logger.warning(f"Alert threshold {key} must be a non-negative number")
                    return False
            
            # Validate metrics collection settings
            for key, value in self.METRICS_TO_COLLECT.items():
                if not isinstance(value, bool):
                    logger.warning(f"Metrics collection setting {key} must be a boolean")
                    return False
            
            # Validate retention period
            if not isinstance(self.RETENTION_DAYS, int) or self.RETENTION_DAYS <= 0:
                logger.warning("RETENTION_DAYS must be a positive integer")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating monitoring config: {e}")
            return False

# Create a global instance
monitoring_config = MonitoringConfig() 