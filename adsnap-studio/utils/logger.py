import logging
import os
from datetime import datetime
import json

class AdSnapLogger:
    """Custom logger for AdSnap Studio with structured logging."""
    
    def __init__(self, name: str = "adsnap_studio"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(f"logs/{name}_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_api_call(self, service: str, endpoint: str, duration: float, status_code: int, error: str = None):
        """Log API call details."""
        log_data = {
            "service": service,
            "endpoint": endpoint,
            "duration_ms": round(duration * 1000, 2),
            "status_code": status_code,
            "timestamp": datetime.now().isoformat(),
            "error": error
        }
        
        if error:
            self.logger.error(f"API call failed: {json.dumps(log_data)}")
        else:
            self.logger.info(f"API call successful: {json.dumps(log_data)}")
    
    def log_performance(self, operation: str, duration: float, memory_usage: float = None):
        """Log performance metrics."""
        log_data = {
            "operation": operation,
            "duration_ms": round(duration * 1000, 2),
            "memory_mb": round(memory_usage, 2) if memory_usage else None,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"Performance: {json.dumps(log_data)}")
    
    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def warning(self, message: str):
        self.logger.warning(message)