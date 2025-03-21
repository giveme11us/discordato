"""
path: core/logging.py
purpose: Implements comprehensive logging system with structured logging and rotation
critical:
- Provides structured logging
- Implements log rotation
- Supports multiple log levels and handlers
"""

import os
import json
import logging
import logging.handlers
from typing import Any, Dict, Optional
from datetime import datetime
from pathlib import Path

class StructuredFormatter(logging.Formatter):
    """Formatter that outputs logs in a structured JSON format."""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as JSON.
        
        Args:
            record: The log record to format
            
        Returns:
            JSON formatted log string
        """
        # Get the original format data
        data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }
            
        # Add extra fields
        if hasattr(record, 'details'):
            data['details'] = record.details
            
        return json.dumps(data)

class BotLogger:
    """Centralized logging for the bot."""
    
    def __init__(
        self,
        log_dir: str = 'logs',
        max_bytes: int = 10485760,  # 10MB
        backup_count: int = 5
    ):
        """
        Initialize the logger.
        
        Args:
            log_dir: Directory to store log files
            max_bytes: Maximum size of each log file
            backup_count: Number of backup files to keep
        """
        self.log_dir = Path(log_dir)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        self._configure_root_logger()
        
        # Set up handlers
        self._setup_handlers()
        
    def _configure_root_logger(self) -> None:
        """Configure the root logger."""
        # Get root logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            
    def _setup_handlers(self) -> None:
        """Set up log handlers."""
        # Create formatters
        structured_formatter = StructuredFormatter()
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Debug log handler (all logs)
        debug_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'debug.log',
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(structured_formatter)
        
        # Error log handler (error and critical)
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'error.log',
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(structured_formatter)
        
        # Info log handler (info and above)
        info_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'info.log',
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(structured_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(debug_handler)
        root_logger.addHandler(error_handler)
        root_logger.addHandler(info_handler)
        root_logger.addHandler(console_handler)
        
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger with the given name.
        
        Args:
            name: Name for the logger
            
        Returns:
            Configured logger instance
        """
        return logging.getLogger(name)
        
    def log_command(
        self,
        logger: logging.Logger,
        command_name: str,
        user: str,
        guild: str,
        channel: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a command execution.
        
        Args:
            logger: Logger instance to use
            command_name: Name of the command
            user: User who executed the command
            guild: Guild where command was executed
            channel: Channel where command was executed
            status: Command execution status
            details: Additional command details
        """
        log_data = {
            'command': command_name,
            'user': user,
            'guild': guild,
            'channel': channel,
            'status': status
        }
        
        if details:
            log_data['details'] = details
            
        logger.info(
            f"Command executed: {command_name}",
            extra={'details': log_data}
        )
        
    def log_error(
        self,
        logger: logging.Logger,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an error with context.
        
        Args:
            logger: Logger instance to use
            error: The error that occurred
            context: Additional context about the error
        """
        log_data = {
            'error_type': error.__class__.__name__,
            'error_message': str(error)
        }
        
        if context:
            log_data['context'] = context
            
        logger.error(
            f"Error occurred: {str(error)}",
            exc_info=error,
            extra={'details': log_data}
        )

# Create global logger instance
bot_logger = BotLogger()

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.
    
    Args:
        name: Name for the logger
        
    Returns:
        Configured logger instance
    """
    return bot_logger.get_logger(name) 