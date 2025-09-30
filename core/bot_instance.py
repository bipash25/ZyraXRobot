"""
Bot instance initialization and setup for ZyraX Bot
"""
import logging
from typing import Optional
from telegram.ext import Application, PicklePersistence
from telegram import BotCommand

from config import config
from core.database import init_database, close_database
from handlers.loader import init_command_loader

logger = logging.getLogger(__name__)

class ZyraXBot:
    """Main bot class for ZyraX"""
    
    def __init__(self):
        self.application: Optional[Application] = None
        self.command_loader = None
        self._running = False
    
    async def initialize(self) -> bool:
        """Initialize the bot application"""
        try:
            # Validate configuration
            if not config.validate():
                logger.error("Invalid configuration")
                return False
            
            # Setup persistence
            persistence = PicklePersistence(filepath="bot_data.pickle")
            
            # Create application
            self.application = (
                Application.builder()
                .token(config.BOT_TOKEN)
                .persistence(persistence)
                .build()
            )
            
            # Initialize database
            if not await init_database():
                logger.error("Failed to initialize database")
                return False
            
            # Initialize command loader
            self.command_loader = init_command_loader(self.application)
            
            # Load all handlers
            if not await self.command_loader.load_all_handlers():
                logger.error("Failed to load command handlers")
                return False
            
            # Setup bot commands menu
            await self._setup_bot_commands()
            
            # Setup error handler
            self.application.add_error_handler(self._error_handler)
            
            # Add shutdown handler
            self.application.add_handler(
                self.application.builder().build().shutdown_handler
            )
            
            logger.info("Bot initialized successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error initializing bot: {e}", exc_info=True)
            return False
    
    async def start(self) -> None:
        """Start the bot"""
        if not self.application:
            if not await self.initialize():
                raise RuntimeError("Failed to initialize bot")
        
        try:
            logger.info("Starting ZyraX Bot...")
            self._running = True
            
            # Start the bot
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(
                drop_pending_updates=True,
                allowed_updates=None
            )
            
            logger.info("Bot started successfully!")
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}", exc_info=True)
            await self.stop()
            raise
    
    async def stop(self) -> None:
        """Stop the bot"""
        if not self._running:
            return
        
        try:
            logger.info("Stopping ZyraX Bot...")
            self._running = False
            
            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
            
            # Close database connection
            await close_database()
            
            logger.info("Bot stopped successfully")
        
        except Exception as e:
            logger.error(f"Error stopping bot: {e}", exc_info=True)
    
    async def _setup_bot_commands(self) -> None:
        """Setup bot commands menu"""
        try:
            commands = [
                BotCommand("start", "Start the bot"),
                BotCommand("help", "Show help information"),
                BotCommand("settings", "Chat settings"),
                BotCommand("ban", "Ban a user"),
                BotCommand("unban", "Unban a user"),
                BotCommand("mute", "Mute a user"),
                BotCommand("unmute", "Unmute a user"),
                BotCommand("kick", "Kick a user"),
                BotCommand("warn", "Warn a user"),
                BotCommand("promote", "Promote a user to admin"),
                BotCommand("demote", "Demote an admin"),
                BotCommand("purge", "Delete messages"),
                BotCommand("pin", "Pin a message"),
                BotCommand("unpin", "Unpin a message"),
                BotCommand("lock", "Lock chat features"),
                BotCommand("unlock", "Unlock chat features"),
                BotCommand("filter", "Add a filter"),
                BotCommand("note", "Save a note"),
                BotCommand("rules", "Show chat rules"),
                BotCommand("id", "Get user/chat ID"),
                BotCommand("info", "Get user information")
            ]
            
            await self.application.bot.set_my_commands(commands)
            logger.info("Bot commands menu updated")
        
        except Exception as e:
            logger.error(f"Error setting bot commands: {e}")
    
    async def _error_handler(self, update, context) -> None:
        """Global error handler"""
        try:
            logger.error(
                f"Exception while handling update {update}: {context.error}",
                exc_info=context.error
            )
            
            # Send error to developer chat if configured
            if config.DEV_CHAT_ID and update:
                try:
                    error_msg = f"🚨 **Bot Error**\n\n"
                    
                    if update.effective_user:
                        error_msg += f"**User:** {update.effective_user.id} "
                        error_msg += f"(@{update.effective_user.username})\n"
                    
                    if update.effective_chat:
                        error_msg += f"**Chat:** {update.effective_chat.id} "
                        error_msg += f"({update.effective_chat.title})\n"
                    
                    if update.effective_message:
                        error_msg += f"**Message:** {update.effective_message.text[:100]}...\n"
                    
                    error_msg += f"\n**Error:** `{str(context.error)}`"
                    
                    await context.bot.send_message(
                        chat_id=config.DEV_CHAT_ID,
                        text=error_msg,
                        parse_mode="Markdown"
                    )
                
                except Exception as e:
                    logger.error(f"Error sending error report: {e}")
        
        except Exception as e:
            logger.error(f"Error in error handler: {e}")
    
    @property
    def is_running(self) -> bool:
        """Check if bot is running"""
        return self._running
    
    async def get_bot_info(self) -> dict:
        """Get bot information"""
        if not self.application:
            return {}
        
        try:
            bot = await self.application.bot.get_me()
            return {
                'id': bot.id,
                'username': bot.username,
                'first_name': bot.first_name,
                'can_join_groups': bot.can_join_groups,
                'can_read_all_group_messages': bot.can_read_all_group_messages,
                'supports_inline_queries': bot.supports_inline_queries
            }
        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            return {}

# Global bot instance
bot_instance: Optional[ZyraXBot] = None

def get_bot() -> Optional[ZyraXBot]:
    """Get the global bot instance"""
    return bot_instance

def create_bot() -> ZyraXBot:
    """Create and return the global bot instance"""
    global bot_instance
    if bot_instance is None:
        bot_instance = ZyraXBot()
    return bot_instance
