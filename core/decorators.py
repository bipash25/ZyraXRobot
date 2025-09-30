"""
Decorators for command permission checking and validation
"""
import functools
import logging
from typing import List, Optional, Callable, Any
from datetime import datetime

try:
    from telegram import Update
    from telegram.ext import ContextTypes
    from telegram.constants import ChatType
except ImportError:
    # Handle case where telegram is not installed yet
    pass

from core.helpers import PermissionChecker, ValidationHelper, MessageHelper
from core.constants import ERROR_MESSAGES
from core.database import get_chat_settings

logger = logging.getLogger(__name__)

def admin_required(permissions: List[str] = None):
    """
    Decorator to require admin permissions
    
    Args:
        permissions: List of specific permissions required (optional)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
            # Check if user is admin
            if not await PermissionChecker.is_user_admin(update, context):
                await MessageHelper.send_message(
                    update, context, ERROR_MESSAGES["admin_only"]
                )
                return
            
            # Check specific permissions if provided
            if permissions:
                for permission in permissions:
                    if not await PermissionChecker.has_permission(update, context, permission):
                        await MessageHelper.send_message(
                            update, context, ERROR_MESSAGES["insufficient_permissions"]
                        )
                        return
            
            return await func(update, context)
        
        return wrapper
    return decorator

def bot_admin_required(func: Callable) -> Callable:
    """Decorator to require bot to be admin"""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
        if not await PermissionChecker.is_bot_admin(update, context):
            await MessageHelper.send_message(
                update, context, ERROR_MESSAGES["bot_not_admin"]
            )
            return
        
        return await func(update, context)
    
    return wrapper

def group_only(func: Callable) -> Callable:
    """Decorator to restrict command to groups only"""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
        allowed_types = [ChatType.GROUP, ChatType.SUPERGROUP]
        if not ValidationHelper.validate_chat_type(update, allowed_types):
            await MessageHelper.send_message(
                update, context, ERROR_MESSAGES["group_only"]
            )
            return
        
        return await func(update, context)
    
    return wrapper

def private_only(func: Callable) -> Callable:
    """Decorator to restrict command to private chats only"""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
        allowed_types = [ChatType.PRIVATE]
        if not ValidationHelper.validate_chat_type(update, allowed_types):
            await MessageHelper.send_message(
                update, context, ERROR_MESSAGES["private_only"]
            )
            return
        
        return await func(update, context)
    
    return wrapper

def owner_only(func: Callable) -> Callable:
    """Decorator to restrict command to bot owner only"""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
        owner_id = context.bot_data.get('owner_id')
        if not owner_id or update.effective_user.id != owner_id:
            await MessageHelper.send_message(
                update, context, ERROR_MESSAGES["no_permission"]
            )
            return
        
        return await func(update, context)
    
    return wrapper

def rate_limit(max_calls: int = 5, window_seconds: int = 60):
    """
    Decorator for rate limiting commands
    
    Args:
        max_calls: Maximum calls allowed in time window
        window_seconds: Time window in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
            user_id = update.effective_user.id
            current_time = context.application.bot_data.get('current_time', 0)
            
            # Initialize rate limit data if not exists
            if 'rate_limits' not in context.bot_data:
                context.bot_data['rate_limits'] = {}
            
            rate_limits = context.bot_data['rate_limits']
            
            # Get user's call history
            func_name = func.__name__
            key = f"{user_id}_{func_name}"
            
            if key not in rate_limits:
                rate_limits[key] = []
            
            call_times = rate_limits[key]
            
            # Remove old calls outside window
            cutoff_time = current_time - window_seconds
            call_times[:] = [t for t in call_times if t > cutoff_time]
            
            # Check if limit exceeded
            if len(call_times) >= max_calls:
                await MessageHelper.send_message(
                    update, context, ERROR_MESSAGES["rate_limited"]
                )
                return
            
            # Add current call
            call_times.append(current_time)
            
            return await func(update, context)
        
        return wrapper
    return decorator

def require_args(min_args: int = 1, usage: str = None):
    """
    Decorator to require minimum number of arguments
    
    Args:
        min_args: Minimum number of arguments required
        usage: Usage string to show if args missing
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
            if len(context.args) < min_args:
                message = f"❌ Not enough arguments."
                if usage:
                    message += f"\n**Usage:** {usage}"
                
                await MessageHelper.send_message(update, context, message)
                return
            
            return await func(update, context)
        
        return wrapper
    return decorator

def feature_enabled(feature_name: str):
    """
    Decorator to check if a feature is enabled in the chat
    
    Args:
        feature_name: Name of the feature to check
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
            chat_id = update.effective_chat.id
            
            try:
                chat_settings = await get_chat_settings(chat_id)
                
                # Check if feature is disabled
                if feature_name in chat_settings.get('disabled_commands', []):
                    await MessageHelper.send_message(
                        update, context, ERROR_MESSAGES["feature_disabled"]
                    )
                    return
                
                # Feature-specific checks
                if feature_name == 'captcha' and not chat_settings.get('captcha_enabled', False):
                    await MessageHelper.send_message(
                        update, context, "❌ Captcha is not enabled in this chat."
                    )
                    return
                
                if feature_name == 'leveling' and not chat_settings.get('leveling_enabled', False):
                    await MessageHelper.send_message(
                        update, context, "❌ Leveling is not enabled in this chat."
                    )
                    return
                
                if feature_name == 'reports' and not chat_settings.get('reports_enabled', True):
                    await MessageHelper.send_message(
                        update, context, "❌ Reports are disabled in this chat."
                    )
                    return
                
            except Exception as e:
                logger.error(f"Error checking feature {feature_name}: {e}")
                # Continue execution if database error
            
            return await func(update, context)
        
        return wrapper
    return decorator

def log_action(action_type: str):
    """
    Decorator to log admin actions
    
    Args:
        action_type: Type of action being performed
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
            # Execute the function first
            result = await func(update, context)
            
            # Log the action
            try:
                from core.database import database
                
                if database.is_connected:
                    log_data = {
                        "chat_id": str(update.effective_chat.id),
                        "action_type": action_type,
                        "performed_by": str(update.effective_user.id),
                        "target_user": None,  # To be filled by the function
                        "reason": None,       # To be filled by the function
                        "metadata": {},       # Additional data
                        "timestamp": datetime.utcnow()
                    }
                    
                    # Try to extract target user and reason from context
                    if hasattr(context, 'action_log_data'):
                        log_data.update(context.action_log_data)
                        delattr(context, 'action_log_data')
                    
                    await database.db.action_logs.insert_one(log_data)
                
            except Exception as e:
                logger.error(f"Error logging action {action_type}: {e}")
            
            return result
        
        return wrapper
    return decorator

def handle_errors(func: Callable) -> Callable:
    """Decorator to handle and log errors gracefully"""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
        try:
            return await func(update, context)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            
            # Send user-friendly error message
            await MessageHelper.send_message(
                update, context, ERROR_MESSAGES["database_error"]
            )
            
            # Report error to developer if configured
            dev_chat_id = context.bot_data.get('dev_chat_id')
            if dev_chat_id:
                try:
                    error_msg = f"🚨 **Error in {func.__name__}**\n\n"
                    error_msg += f"**User:** {update.effective_user.id}\n"
                    error_msg += f"**Chat:** {update.effective_chat.id}\n"
                    error_msg += f"**Error:** `{str(e)}`"
                    
                    await context.bot.send_message(
                        chat_id=dev_chat_id,
                        text=error_msg,
                        parse_mode="Markdown"
                    )
                except:
                    pass  # Don't fail if error reporting fails
    
    return wrapper

def approved_or_admin(func: Callable) -> Callable:
    """Decorator to allow approved users or admins"""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Check if user is admin
        if await PermissionChecker.is_user_admin(update, context):
            return await func(update, context)
        
        # Check if user is approved
        try:
            from core.database import get_user_data
            user_data = await get_user_data(user_id, chat_id)
            
            if user_data.get('approved', False):
                return await func(update, context)
        
        except Exception as e:
            logger.error(f"Error checking approval status: {e}")
        
        await MessageHelper.send_message(
            update, context, ERROR_MESSAGES["no_permission"]
        )
    
    return wrapper
