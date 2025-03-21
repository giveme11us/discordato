"""
Unit tests for logging system.
"""
import pytest
import logging
import json
from pathlib import Path
from unittest.mock import Mock, patch, call
from core.log_config import LogManager, LogHandler, LogLevel, LogError

@pytest.mark.unit
class TestLoggingSystem:
    """Test suite for logging system functionality."""
    
    @pytest.fixture
    def log_manager(self, tmp_path):
        """Fixture to provide a log manager instance with temporary directory."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        return LogManager(log_dir=str(log_dir))
        
    @pytest.fixture
    def mock_handler(self):
        """Fixture to provide a mock log handler."""
        handler = Mock(spec=LogHandler)
        handler.format = Mock(return_value="formatted_log")
        return handler
        
    def test_log_initialization(self, tmp_path):
        """Test logging system initialization."""
        # Setup
        log_dir = tmp_path / "logs"
        
        # Test
        log_manager = LogManager(log_dir=str(log_dir))
        
        # Verify
        assert log_dir.exists()
        assert log_manager.log_dir == str(log_dir)
        assert isinstance(log_manager.logger, logging.Logger)
        
    def test_log_levels(self, log_manager, mock_handler):
        """Test different logging levels."""
        # Setup
        log_manager.add_handler(mock_handler)
        test_message = "Test log message"
        
        # Test each log level
        log_manager.debug(test_message)
        log_manager.info(test_message)
        log_manager.warning(test_message)
        log_manager.error(test_message)
        log_manager.critical(test_message)
        
        # Verify
        assert mock_handler.handle.call_count == 5
        calls = mock_handler.handle.call_args_list
        assert calls[0][0][0].levelno == logging.DEBUG
        assert calls[1][0][0].levelno == logging.INFO
        assert calls[2][0][0].levelno == logging.WARNING
        assert calls[3][0][0].levelno == logging.ERROR
        assert calls[4][0][0].levelno == logging.CRITICAL
        
    def test_file_handler(self, log_manager, tmp_path):
        """Test file-based logging handler."""
        # Setup
        log_file = tmp_path / "logs" / "test.log"
        log_manager.add_file_handler(str(log_file))
        test_message = "Test log message"
        
        # Test
        log_manager.info(test_message)
        
        # Verify
        assert log_file.exists()
        log_content = log_file.read_text()
        assert test_message in log_content
        
    def test_json_formatting(self, log_manager, tmp_path):
        """Test JSON log formatting."""
        # Setup
        log_file = tmp_path / "logs" / "json.log"
        log_manager.add_json_handler(str(log_file))
        test_message = "Test log message"
        
        # Test
        log_manager.info(test_message)
        
        # Verify
        assert log_file.exists()
        log_content = log_file.read_text()
        log_entry = json.loads(log_content.strip())
        assert log_entry["message"] == test_message
        assert "timestamp" in log_entry
        assert "level" in log_entry
        
    def test_log_rotation(self, log_manager, tmp_path):
        """Test log file rotation."""
        # Setup
        log_file = tmp_path / "logs" / "rotating.log"
        max_bytes = 1000
        backup_count = 3
        
        log_manager.add_rotating_handler(
            str(log_file),
            max_bytes=max_bytes,
            backup_count=backup_count
        )
        
        # Test - write enough logs to trigger rotation
        large_message = "X" * (max_bytes // 2)
        for _ in range(10):
            log_manager.info(large_message)
            
        # Verify
        assert log_file.exists()
        backup_files = list(tmp_path.glob("logs/rotating.log.*"))
        assert len(backup_files) <= backup_count
        
    def test_log_filtering(self, log_manager, mock_handler):
        """Test log message filtering."""
        # Setup
        log_manager.add_handler(mock_handler, level=LogLevel.WARNING)
        
        # Test
        log_manager.debug("Debug message")
        log_manager.info("Info message")
        log_manager.warning("Warning message")
        log_manager.error("Error message")
        
        # Verify - only WARNING and above should be logged
        assert mock_handler.handle.call_count == 2
        calls = mock_handler.handle.call_args_list
        assert all(call[0][0].levelno >= logging.WARNING for call in calls)
        
    def test_context_logging(self, log_manager, mock_handler):
        """Test logging with context information."""
        # Setup
        log_manager.add_handler(mock_handler)
        
        # Test
        with log_manager.context(user_id="123", action="test"):
            log_manager.info("Action performed")
            
        # Verify
        log_record = mock_handler.handle.call_args[0][0]
        assert log_record.user_id == "123"
        assert log_record.action == "test"
        
    def test_error_logging(self, log_manager, mock_handler):
        """Test error logging with exception information."""
        # Setup
        log_manager.add_handler(mock_handler)
        
        # Test
        try:
            raise ValueError("Test error")
        except ValueError as e:
            log_manager.exception("An error occurred", exc_info=e)
            
        # Verify
        log_record = mock_handler.handle.call_args[0][0]
        assert log_record.levelno == logging.ERROR
        assert "Test error" in str(log_record.exc_info)
        
    def test_custom_formatter(self, log_manager, tmp_path):
        """Test custom log formatter."""
        # Setup
        log_file = tmp_path / "logs" / "custom.log"
        
        def custom_format(record):
            return f"CUSTOM: {record.levelname} - {record.message}"
            
        log_manager.add_file_handler(str(log_file), formatter=custom_format)
        
        # Test
        test_message = "Test message"
        log_manager.info(test_message)
        
        # Verify
        log_content = log_file.read_text()
        assert log_content.startswith("CUSTOM: INFO")
        assert test_message in log_content
        
    def test_multiple_handlers(self, log_manager, tmp_path):
        """Test logging to multiple handlers."""
        # Setup
        file1 = tmp_path / "logs" / "file1.log"
        file2 = tmp_path / "logs" / "file2.log"
        
        log_manager.add_file_handler(str(file1))
        log_manager.add_file_handler(str(file2))
        
        # Test
        test_message = "Test multiple handlers"
        log_manager.info(test_message)
        
        # Verify
        assert test_message in file1.read_text()
        assert test_message in file2.read_text()
        
    def test_log_cleanup(self, log_manager, tmp_path):
        """Test log file cleanup functionality."""
        # Setup
        log_dir = tmp_path / "logs"
        old_log = log_dir / "old.log"
        new_log = log_dir / "new.log"
        
        # Create test log files with different timestamps
        old_log.touch()
        new_log.touch()
        
        # Mock file age
        with patch('os.path.getmtime') as mock_getmtime:
            def mtime_side_effect(path):
                if Path(path).name == "old.log":
                    return 0  # Very old
                return 9999999999  # Very new
                
            mock_getmtime.side_effect = mtime_side_effect
            
            # Test
            log_manager.cleanup_old_logs(max_age_days=1)
            
            # Verify
            assert not old_log.exists()
            assert new_log.exists()
            
    def test_log_validation(self, log_manager):
        """Test log input validation."""
        # Test invalid log level
        with pytest.raises(LogError, match="Invalid log level"):
            log_manager.log(9999, "Invalid level message")
            
        # Test invalid message type
        with pytest.raises(LogError, match="Log message must be a string"):
            log_manager.info(123)
            
        # Test invalid handler
        with pytest.raises(LogError, match="Invalid log handler"):
            log_manager.add_handler(None) 