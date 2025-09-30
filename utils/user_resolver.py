"""
User resolution utilities for ZyraX Bot
"""
import re
from typing import Optional, Union, Dict, Any
from telegram import Update, User, Message
from telegram.ext import ContextTypes

class UserResolver:
    """Resolve users from various input formats"""
    
    @staticmethod
    async def resolve_user(
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE, 
        text: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve user from reply, mention, username, or user ID
        
        Args:
            update: Telegram update object
            context: Bot context
            text: Text to parse for user (if not provided, uses command args)
            
        Returns:
            Dict with user info or None if not found
        """
        message = update.effective_message
        
        # Check if replying to a message
        if message.reply_to_message and message.reply_to_message.from_user:
            user = message.reply_to_message.from_user
            return UserResolver._user_to_dict(user)
        
        # Get text to parse
        if text is None:
            # Get text from command arguments
            if context.args:
                text = " ".join(context.args)
            else:
                return None
        
        if not text:
            return None
        
        # Try to resolve from various formats
        user_info = None
        
        # Try user ID (numeric)
        user_info = await UserResolver._resolve_by_id(context, text)
        if user_info:
            return user_info
        
        # Try username (@username or username)
        user_info = await UserResolver._resolve_by_username(context, text)
        if user_info:
            return user_info
        
        # Try mention format [Name](tg://user?id=123456)
        user_info = UserResolver._resolve_by_mention(text)
        if user_info:
            return user_info
        
        return None
    
    @staticmethod
    async def _resolve_by_id(context: ContextTypes.DEFAULT_TYPE, text: str) -> Optional[Dict[str, Any]]:
        """Resolve user by numeric ID"""
        try:
            user_id = int(text.strip())
            
            # Try to get user info from Telegram
            try:
                chat_member = await context.bot.get_chat_member(user_id, user_id)
                return UserResolver._user_to_dict(chat_member.user)
            except:
                # If we can't get from Telegram, return basic info
                return {
                    "id": user_id,
                    "first_name": f"User {user_id}",
                    "username": None,
                    "last_name": None,
                    "is_bot": False
                }
        except ValueError:
            return None
    
    @staticmethod
    async def _resolve_by_username(context: ContextTypes.DEFAULT_TYPE, text: str) -> Optional[Dict[str, Any]]:
        """Resolve user by username"""
        # Extract username
        username = text.strip()
        if username.startswith('@'):
            username = username[1:]
        
        # Username validation
        if not re.match(r'^[a-zA-Z0-9_]{5,32}$', username):
            return None
        
        # Try to get user info from chat members (this is limited in Bot API)
        # For now, return basic info - in a real implementation you'd have a cache
        return {
            "id": None,  # Unknown
            "first_name": f"@{username}",
            "username": username,
            "last_name": None,
            "is_bot": False
        }
    
    @staticmethod
    def _resolve_by_mention(text: str) -> Optional[Dict[str, Any]]:
        """Resolve user from markdown mention format"""
        # Pattern: [Name](tg://user?id=123456)
        pattern = r'\[([^\]]+)\]\(tg://user\?id=(\d+)\)'
        match = re.search(pattern, text)
        
        if match:
            name, user_id = match.groups()
            return {
                "id": int(user_id),
                "first_name": name,
                "username": None,
                "last_name": None,
                "is_bot": False
            }
        
        return None
    
    @staticmethod
    def _user_to_dict(user: User) -> Dict[str, Any]:
        """Convert Telegram User object to dict"""
        return {
            "id": user.id,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "username": user.username,
            "is_bot": user.is_bot
        }
    
    @staticmethod
    def format_user_mention(user_info: Dict[str, Any]) -> str:
        """Format user info as mention"""
        if user_info.get("username"):
            return f"@{user_info['username']}"
        elif user_info.get("id"):
            name = user_info.get("first_name", f"User {user_info['id']}")
            return f"[{name}](tg://user?id={user_info['id']})"
        else:
            return user_info.get("first_name", "Unknown User")
    
    @staticmethod
    def get_display_name(user_info: Dict[str, Any]) -> str:
        """Get display name for user"""
        if user_info.get("first_name") and user_info.get("last_name"):
            return f"{user_info['first_name']} {user_info['last_name']}"
        elif user_info.get("first_name"):
            return user_info["first_name"]
        elif user_info.get("username"):
            return f"@{user_info['username']}"
        else:
            return f"User {user_info.get('id', 'Unknown')}"
    
    @staticmethod
    def extract_reason(text: str, after_user: bool = True) -> str:
        """Extract reason from command text"""
        if not text:
            return "No reason provided"
        
        # If after_user is True, skip the first word (user identifier)
        if after_user:
            parts = text.split(None, 1)
            if len(parts) > 1:
                return parts[1]
            else:
                return "No reason provided"
        
        return text

# Convenience function for backward compatibility
async def resolve_user(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str = None) -> Optional[Dict[str, Any]]:
    """Resolve user from reply, mention, username, or user ID"""
    return await UserResolver.resolve_user(update, context, text)
