"""
Logging configuration module
Provides consistent logging setup across all modules
"""
import logging
import sys
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """Setup logger with consistent formatting
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file specified)
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger with default configuration
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Create a default logger for the application
def setup_app_logger(config: Optional[dict] = None) -> logging.Logger:
    """Setup application-wide logger with configuration
    
    Args:
        config: Optional configuration dictionary with logging settings
    
    Returns:
        Configured application logger
    """
    if config is None:
        config = {}
    
    # Get logging configuration
    log_level_str = config.get('level', 'INFO')
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    log_file = config.get('file')
    max_bytes = config.get('max_bytes', 10485760)
    backup_count = config.get('backup_count', 5)
    
    return setup_logger(
        'eclipse_sites',
        level=log_level,
        log_file=log_file,
        max_bytes=max_bytes,
        backup_count=backup_count
    )


# Convenience function to log with emojis for better readability
class EmojiLogger:
    """Logger wrapper with emoji support for better console output"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def success(self, message: str) -> None:
        """Log success message with ✓ emoji"""
        self.logger.info(f"✓ {message}")
    
    def error(self, message: str) -> None:
        """Log error message with ✗ emoji"""
        self.logger.error(f"✗ {message}")
    
    def warning(self, message: str) -> None:
        """Log warning message with ⚠️ emoji"""
        self.logger.warning(f"⚠️  {message}")
    
    def info(self, message: str) -> None:
        """Log info message"""
        self.logger.info(message)
    
    def debug(self, message: str) -> None:
        """Log debug message"""
        self.logger.debug(message)
    
    def step(self, step_num: int, message: str) -> None:
        """Log step message with formatting"""
        self.logger.info(f"\nSTEP {step_num}: {message}")
        self.logger.info("=" * 60)
    
    def separator(self) -> None:
        """Log separator line"""
        self.logger.info("=" * 60)
    
    def progress(self, current: int, total: int, item: str) -> None:
        """Log progress message"""
        self.logger.info(f"[{current}/{total}] {item}")

# Made with Bob