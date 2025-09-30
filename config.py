"""
Configuration management for ZyraX Telegram Bot
"""
import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Main configuration class"""
    
    # Bot Configuration
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    API_ID: int = int(os.getenv("API_ID", "0"))
    API_HASH: str = os.getenv("API_HASH", "")
    
    # Database Configuration
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/zyraX_bot")
    
    # Redis Configuration
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "bot.log")
    
    # Development Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    DEV_CHAT_ID: Optional[int] = int(os.getenv("DEV_CHAT_ID", "0")) or None
    
    # Federation Settings
    FEDERATION_LOGS: bool = os.getenv("FEDERATION_LOGS", "True").lower() == "true"
    FEDERATION_REASON_REQUIRED: bool = os.getenv("FEDERATION_REASON_REQUIRED", "True").lower() == "true"
    
    # Rate Limiting
    COMMAND_COOLDOWN: int = int(os.getenv("COMMAND_COOLDOWN", "3"))
    FLOOD_THRESHOLD: int = int(os.getenv("FLOOD_THRESHOLD", "10"))
    
    # File Upload Limits
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "50")) * 1024 * 1024  # 50MB default
    
    # Captcha Settings
    CAPTCHA_TIMEOUT: int = int(os.getenv("CAPTCHA_TIMEOUT", "300"))  # 5 minutes
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration values"""
        if not cls.BOT_TOKEN:
            logging.error("BOT_TOKEN is required")
            return False
        
        if not cls.API_ID or not cls.API_HASH:
            logging.warning("API_ID and API_HASH not set - MTProto features disabled")
        
        return True

# Create singleton instance
config = Config()

# Setup logging
def setup_logging():
    """Setup logging configuration"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper()),
        format=log_format,
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("pyrogram").setLevel(logging.WARNING)

setup_logging()
