"""
Chat logging middleware
"""
import logging
from datetime import datetime
from typing import Dict, Any

try:
    from telegram import Update
    from telegram.ext import ContextTypes
except ImportError:
    pass

logger = logging.getLogger(__name__)

class ChatLogger:
    """Middleware for logging chat activities"""
    
    def __init__(self):
        self.enabled = True
    
    async def log_action(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        action_type: str,
        **metadata
    ):
        """Log an action to database and/or log channel"""
        if not self.enabled:
            return
        
        try:
            from core.database import database
            
            if not database.is_connected:
                return
            
            log_data = {
                "chat_id": str(update.effective_chat.id),
                "action_type": action_type,
                "performed_by": str(update.effective_user.id),
                "timestamp": datetime.utcnow(),
                "metadata": metadata
            }
            
            # Add additional context if available
            if hasattr(context, 'action_log_data'):
                log_data.update(context.action_log_data)
            
            # Insert into database
            await database.db.action_logs.insert_one(log_data)
            
            # Send to log channel if configured
            await self._send_to_log_channel(update, context, log_data)
        
        except Exception as e:
            logger.error(f"Error logging action: {e}")
    
    async def _send_to_log_channel(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        log_data: Dict[str, Any]
    ):
        """Send log message to configured log channel"""
        try:
            from core.database import get_chat_settings
            
            chat_settings = await get_chat_settings(update.effective_chat.id)
            log_channel_id = chat_settings.get('log_channel_id')
            
            if not log_channel_id:
                return
            
            # Format log message
            action_type = log_data['action_type']
            performed_by = log_data['performed_by']
            
            log_msg = f"**🔍 Action Log**\n\n"
            log_msg += f"**Action:** {action_type.title()}\n"
            log_msg += f"**Performed by:** {performed_by}\n"
            log_msg += f"**Chat:** {update.effective_chat.title or 'Unknown'}\n"
            log_msg += f"**Time:** {log_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            
            # Add metadata
            metadata = log_data.get('metadata', {})
            if metadata:
                log_msg += "\n**Details:**\n"
                for key, value in metadata.items():
                    log_msg += f"• {key}: {value}\n"
            
            await context.bot.send_message(
                chat_id=log_channel_id,
                text=log_msg,
                parse_mode="Markdown"
            )
        
        except Exception as e:
            logger.debug(f"Could not send to log channel: {e}")

# Global logger instance
chat_logger = ChatLogger()
