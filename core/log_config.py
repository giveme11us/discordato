"""
Logging System

This module implements a comprehensive logging system for the Discord bot.

The Logging System is responsible for:
1. Structured log output in JSON format
2. Log file rotation and management
3. Multiple log levels and handlers
4. Command and error tracking

Critical:
- Provides structured logging
- Implements log rotation
- Supports multiple log levels and handlers
- Ensures proper log file management

Classes:
    StructuredFormatter: JSON log formatter
    BotLogger: Main logging system
"""

import os
import json
import logging
import logging.handlers
from typing import Any, Dict, Optional
from datetime import datetime
from pathlib import Path

class StructuredFormatter(logging.Formatter):
    """
    Formatter that outputs logs in a structured JSON format.
    
    This formatter:
    - Converts log records to JSON
    - Adds timestamp and context
    - Handles exception information
    - Supports custom fields
    
    Attributes:
        default_time_format (str): Time format string
        default_msec_format (str): Millisecond format string
        
    Critical:
        - Must handle all log record attributes
        - Should escape special characters
        - Must format exceptions properly
        - Should maintain consistent JSON structure
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as JSON.
        
        This method:
        1. Extracts standard log fields
        2. Adds timestamp and context
        3. Handles exceptions
        4. Formats as JSON string
        
        Args:
            record (logging.LogRecord): The log record to format
            
        Returns:
            str: JSON formatted log string
            
        Note:
            The output includes:
            - Standard log fields (time, level, message)
            - Exception information if present
            - Custom fields from extra/context
            - Source location (module, function, line)
        """
        data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }
            
        if hasattr(record, 'details'):
            data['details'] = record.details
            
        return json.dumps(data)

class BotLogger:
    """
    Main logging system for the Discord bot.
    
    This class manages:
    - Log file configuration and rotation
    - Multiple log levels and handlers
    - Structured and simple formatting
    - Command and error tracking
    
    Attributes:
        log_dir (Path): Directory for log files
        max_bytes (int): Maximum log file size
        backup_count (int): Number of backup files
        
    Critical:
        - Must handle concurrent writes safely
        - Should manage disk space efficiently
        - Must preserve error context
        - Should handle log rotation properly
    """
    
    def __init__(
        self,
        log_dir: str = 'logs',
        max_bytes: int = 10485760,  # 10MB
        backup_count: int = 5
    ):
        """
        Initialize the logging system.
        
        This method:
        1. Sets up log directory
        2. Configures root logger
        3. Creates log handlers
        4. Sets up log rotation
        
        Args:
            log_dir (str): Directory for log files
            max_bytes (int): Maximum size per log file (default: 10MB)
            backup_count (int): Number of backup files (default: 5)
            
        Note:
            Creates log directory if it doesn't exist
        """
        self.log_dir = Path(log_dir)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._configure_root_logger()
        self._setup_handlers()
        
    def _configure_root_logger(self) -> None:
        """
        Configure the root logger.
        
        This method:
        1. Sets base log level to DEBUG
        2. Removes existing handlers
        3. Prepares for new configuration
        
        Note:
            This is an internal method called during initialization
        """
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            
    def _setup_handlers(self) -> None:
        """
        Set up log handlers.
        
        This method:
        1. Creates structured and simple formatters
        2. Sets up file handlers for different levels
        3. Configures log rotation
        4. Adds console output handler
        
        Note:
            Creates separate handlers for:
            - Debug logs (all levels)
            - Info logs (info and above)
            - Error logs (error and critical)
            - Console output (info and above)
        """
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
        
        root_logger = logging.getLogger()
        root_logger.addHandler(debug_handler)
        root_logger.addHandler(error_handler)
        root_logger.addHandler(info_handler)
        root_logger.addHandler(console_handler)
        
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a configured logger instance.
        
        This method:
        1. Gets or creates logger
        2. Inherits root configuration
        3. Returns configured instance
        
        Args:
            name (str): Name for the logger
            
        Returns:
            logging.Logger: Configured logger instance
            
        Note:
            Creates a new logger if one doesn't exist
            Inherits handlers from root logger
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
        
        This method:
        1. Records command metadata
        2. Tracks execution status
        3. Includes context details
        
        Args:
            logger (logging.Logger): Logger instance
            command_name (str): Name of the command
            user (str): User who executed command
            guild (str): Guild where command was executed
            channel (str): Channel where command was executed
            status (str): Command execution status
            details (dict, optional): Additional command details
            
        Note:
            Status should be one of:
            - 'started'
            - 'completed'
            - 'failed'
            - 'denied'
        """
        log_data = {
            'command': command_name,
            'user': user,
            'guild': guild,
            'channel': channel,
            'status': status
        }
        
        if details:
            log_data.update(details)
            
        logger.info('Command execution', extra={'details': log_data})
        
    def log_error(
        self,
        logger: logging.Logger,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an error with context.
        
        This method:
        1. Records error information
        2. Includes stack trace
        3. Adds context details
        
        Args:
            logger (logging.Logger): Logger instance
            error (Exception): The error to log
            context (dict, optional): Additional error context
            
        Note:
            Context should include relevant information
            to help diagnose the error
        """
        error_data = {
            'error_type': type(error).__name__,
            'error_message': str(error)
        }
        
        if context:
            error_data.update(context)
            
        logger.error(
            'Error occurred',
            exc_info=error,
            extra={'details': error_data}
        )

# Create global logger instance
bot_logger = BotLogger()

def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name (str): Name for the logger
        
    Returns:
        logging.Logger: Configured logger instance
        
    Note:
        This is the main entry point for getting loggers
        in other modules.
    """
    return bot_logger.get_logger(name) 