"""
Main entry point for ZyraX Telegram Bot
"""
import asyncio
import logging
import signal
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import config, setup_logging
from core.bot_instance import create_bot

# Setup logging first
setup_logging()
logger = logging.getLogger(__name__)

class BotRunner:
    """Bot runner with graceful shutdown handling"""
    
    def __init__(self):
        self.bot = None
        self.shutdown_event = asyncio.Event()
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        if sys.platform != "win32":
            # Unix signals
            for sig in (signal.SIGTERM, signal.SIGINT):
                signal.signal(sig, self._signal_handler)
        else:
            # Windows signal
            signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(self._shutdown())
    
    async def _shutdown(self):
        """Trigger shutdown"""
        self.shutdown_event.set()
    
    async def run(self):
        """Run the bot with graceful shutdown"""
        try:
            # Create bot instance
            self.bot = create_bot()
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Initialize and start bot
            if not await self.bot.initialize():
                logger.error("Failed to initialize bot")
                return False
            
            # Start bot in background
            bot_task = asyncio.create_task(self.bot.start())
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
            # Stop bot gracefully
            logger.info("Shutting down bot...")
            await self.bot.stop()
            
            # Wait for bot task to complete
            try:
                await asyncio.wait_for(bot_task, timeout=10.0)
            except asyncio.TimeoutError:
                logger.warning("Bot shutdown timed out")
                bot_task.cancel()
            
            logger.info("Bot shutdown complete")
            return True
        
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            return True
        except Exception as e:
            logger.error(f"Error running bot: {e}", exc_info=True)
            return False
        finally:
            if self.bot:
                await self.bot.stop()

async def main():
    """Main entry point"""
    logger.info("=" * 50)
    logger.info("🤖 Starting ZyraX Telegram Bot")
    logger.info("=" * 50)
    
    # Display configuration info
    logger.info(f"Bot Token: {'*' * 20}{config.BOT_TOKEN[-10:] if config.BOT_TOKEN else 'NOT SET'}")
    logger.info(f"Database URI: {config.MONGODB_URI}")
    logger.info(f"Debug Mode: {config.DEBUG}")
    logger.info(f"Log Level: {config.LOG_LEVEL}")
    
    # Validate required config
    if not config.BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not configured!")
        logger.error("Please set BOT_TOKEN in your .env file or environment variables")
        return False
    
    if not config.MONGODB_URI:
        logger.error("❌ MONGODB_URI not configured!")
        logger.error("Please set MONGODB_URI in your .env file or environment variables")
        return False
    
    # Run the bot
    runner = BotRunner()
    success = await runner.run()
    
    if success:
        logger.info("✅ Bot stopped successfully")
        return True
    else:
        logger.error("❌ Bot stopped with errors")
        return False

if __name__ == "__main__":
    try:
        # Run the bot
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
