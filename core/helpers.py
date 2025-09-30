"""
Helper functions for ZyraX Bot
"""
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from telegram import Update, User, Chat, ChatMember
from telegram.ext import ContextTypes
from telegram.constants import ChatType, ChatMemberStatus

from core.database import get_chat_settings, get_user_data
from utils.user_resolver import UserResolver
from utils.time_parser import TimeParser

logger = logging.getLogger(__name__)

class PermissionChecker:
    """Check user permissions in chat"""
    
    @staticmethod
    async def is_user_admin(
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE, 
        user_id: int = None,
        chat_id: int = None
    ) -> bool:
        """Check if user is admin in chat"""
        try:
            if user_id is None:
                user_id = update.effective_user.id
            if chat_id is None:
                chat_id = update.effective_chat.id
            
            # Bot owner is always admin
            if user_id == context.bot_data.get('owner_id'):
                return True
            
            # Get chat member
            member = await context.bot.get_chat_member(chat_id, user_id)
            return member.status in [ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR]
        
        except Exception as e:
            logger.error(f"Error checking admin status: {e}")
            return False
    
    @staticmethod
    async def is_bot_admin(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        chat_id: int = None
    ) -> bool:
        """Check if bot is admin in chat"""
        try:
            if chat_id is None:
                chat_id = update.effective_chat.id
            
            member = await context.bot.get_chat_member(chat_id, context.bot.id)
            return member.status == ChatMemberStatus.ADMINISTRATOR
        
        except Exception as e:
            logger.error(f"Error checking bot admin status: {e}")
            return False
    
    @staticmethod
    async def has_permission(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        permission: str,
        user_id: int = None,
        chat_id: int = None
    ) -> bool:
        """Check if user has specific permission"""
        try:
            if user_id is None:
                user_id = update.effective_user.id
            if chat_id is None:
                chat_id = update.effective_chat.id
            
            # Check if user is admin first
            if not await PermissionChecker.is_user_admin(update, context, user_id, chat_id):
                return False
            
            # Get chat member with permissions
            member = await context.bot.get_chat_member(chat_id, user_id)
            
            # Creator has all permissions
            if member.status == ChatMemberStatus.CREATOR:
                return True
            
            # Check specific permission
            if hasattr(member, permission):
                return getattr(member, permission)
            
            return False
        
        except Exception as e:
            logger.error(f"Error checking permission {permission}: {e}")
            return False

class MessageHelper:
    """Helper functions for message handling"""
    
    @staticmethod
    async def send_message(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        text: str,
        parse_mode: str = "Markdown",
        reply_markup=None,
        reply_to_message: bool = False
    ):
        """Send message with error handling"""
        try:
            kwargs = {
                'text': text,
                'parse_mode': parse_mode
            }
            
            if reply_markup:
                kwargs['reply_markup'] = reply_markup
            
            if reply_to_message and update.effective_message:
                kwargs['reply_to_message_id'] = update.effective_message.message_id
            
            return await context.bot.send_message(
                chat_id=update.effective_chat.id,
                **kwargs
            )
        
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            # Try without markdown if parsing failed
            try:
                return await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text
                )
            except Exception as e2:
                logger.error(f"Error sending plain message: {e2}")
                return None
    
    @staticmethod
    async def edit_message(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        message_id: int,
        text: str,
        parse_mode: str = "Markdown",
        reply_markup=None
    ):
        """Edit message with error handling"""
        try:
            return await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=message_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error editing message: {e}")
            return None
    
    @staticmethod
    async def delete_message(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        message_id: int = None
    ):
        """Delete message with error handling"""
        try:
            if message_id is None:
                message_id = update.effective_message.message_id
            
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=message_id
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            return False

class ChatHelper:
    """Helper functions for chat operations"""
    
    @staticmethod
    async def get_chat_admins(
        chat_id: int,
        context: ContextTypes.DEFAULT_TYPE,
        use_cache: bool = True
    ) -> List[ChatMember]:
        """Get chat administrators with caching"""
        try:
            # Check cache first if enabled
            cache_key = f"admins_{chat_id}"
            if use_cache and cache_key in context.bot_data:
                cached_data = context.bot_data[cache_key]
                # Check if cache is still valid (10 minutes)
                if datetime.now() - cached_data['timestamp'] < timedelta(minutes=10):
                    return cached_data['admins']
            
            # Fetch from Telegram
            admins = await context.bot.get_chat_administrators(chat_id)
            
            # Update cache
            if use_cache:
                context.bot_data[cache_key] = {
                    'admins': admins,
                    'timestamp': datetime.now()
                }
            
            return admins
        
        except Exception as e:
            logger.error(f"Error getting chat admins: {e}")
            return []
    
    @staticmethod
    async def restrict_user(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user_id: int,
        until_date: datetime = None,
        can_send_messages: bool = False,
        can_send_media: bool = False,
        can_send_other: bool = False,
        can_add_web_page_previews: bool = False
    ) -> bool:
        """Restrict user in chat"""
        try:
            from telegram import ChatPermissions
            
            permissions = ChatPermissions(
                can_send_messages=can_send_messages,
                can_send_media_messages=can_send_media,
                can_send_other_messages=can_send_other,
                can_add_web_page_previews=can_add_web_page_previews
            )
            
            await context.bot.restrict_chat_member(
                chat_id=update.effective_chat.id,
                user_id=user_id,
                permissions=permissions,
                until_date=until_date
            )
            return True
        
        except Exception as e:
            logger.error(f"Error restricting user: {e}")
            return False
    
    @staticmethod
    async def ban_user(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user_id: int,
        until_date: datetime = None,
        revoke_messages: bool = False
    ) -> bool:
        """Ban user from chat"""
        try:
            await context.bot.ban_chat_member(
                chat_id=update.effective_chat.id,
                user_id=user_id,
                until_date=until_date,
                revoke_messages=revoke_messages
            )
            return True
        
        except Exception as e:
            logger.error(f"Error banning user: {e}")
            return False
    
    @staticmethod
    async def unban_user(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user_id: int,
        only_if_banned: bool = True
    ) -> bool:
        """Unban user from chat"""
        try:
            await context.bot.unban_chat_member(
                chat_id=update.effective_chat.id,
                user_id=user_id,
                only_if_banned=only_if_banned
            )
            return True
        
        except Exception as e:
            logger.error(f"Error unbanning user: {e}")
            return False

class ValidationHelper:
    """Helper functions for validation"""
    
    @staticmethod
    def validate_chat_type(update: Update, allowed_types: List[str]) -> bool:
        """Validate if command can be used in current chat type"""
        if not update.effective_chat:
            return False
        
        chat_type = update.effective_chat.type
        return chat_type in allowed_types
    
    @staticmethod
    def validate_user_input(text: str, max_length: int = None, min_length: int = None) -> Tuple[bool, str]:
        """Validate user input"""
        if not text:
            return False, "Input cannot be empty"
        
        if min_length and len(text) < min_length:
            return False, f"Input must be at least {min_length} characters"
        
        if max_length and len(text) > max_length:
            return False, f"Input cannot exceed {max_length} characters"
        
        return True, ""
    
    @staticmethod
    def is_url(text: str) -> bool:
        """Check if text is a valid URL"""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(text) is not None

class FormatHelper:
    """Helper functions for formatting"""
    
    @staticmethod
    def format_user_mention(user: Union[User, Dict[str, Any]]) -> str:
        """Format user mention"""
        if isinstance(user, User):
            if user.username:
                return f"@{user.username}"
            return f"[{user.first_name}](tg://user?id={user.id})"
        elif isinstance(user, dict):
            return UserResolver.format_user_mention(user)
        return "Unknown User"
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format duration in human readable format"""
        return TimeParser.format_duration(seconds)
    
    @staticmethod
    def format_chat_title(chat: Chat) -> str:
        """Format chat title"""
        if chat.type == ChatType.PRIVATE:
            return f"Private chat with {chat.first_name or 'Unknown'}"
        return chat.title or "Unknown Chat"
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Truncate text with ellipsis"""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
    
    @staticmethod
    def format_list(items: List[str], max_items: int = 10) -> str:
        """Format list of items"""
        if not items:
            return "None"
        
        if len(items) <= max_items:
            return ", ".join(items)
        
        shown = items[:max_items]
        remaining = len(items) - max_items
        return ", ".join(shown) + f" and {remaining} more"

class CacheHelper:
    """Helper functions for caching"""
    
    @staticmethod
    def get_from_cache(
        context: ContextTypes.DEFAULT_TYPE,
        key: str,
        max_age_seconds: int = 600
    ) -> Optional[Any]:
        """Get data from cache if not expired"""
        if key not in context.bot_data:
            return None
        
        cached_data = context.bot_data[key]
        if 'timestamp' not in cached_data:
            return None
        
        age = datetime.now() - cached_data['timestamp']
        if age.total_seconds() > max_age_seconds:
            del context.bot_data[key]
            return None
        
        return cached_data.get('data')
    
    @staticmethod
    def set_cache(
        context: ContextTypes.DEFAULT_TYPE,
        key: str,
        data: Any
    ):
        """Set data in cache with timestamp"""
        context.bot_data[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    @staticmethod
    def clear_cache(context: ContextTypes.DEFAULT_TYPE, pattern: str = None):
        """Clear cache entries matching pattern"""
        if pattern is None:
            context.bot_data.clear()
            return
        
        keys_to_remove = [k for k in context.bot_data.keys() if pattern in k]
        for key in keys_to_remove:
            del context.bot_data[key]
