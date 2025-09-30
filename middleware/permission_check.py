"""
Permission checking middleware
"""
import logging
from typing import Optional, Callable, Any

try:
    from telegram import Update
    from telegram.ext import ContextTypes, BaseHandler
except ImportError:
    pass

logger = logging.getLogger(__name__)

class PermissionMiddleware:
    """Middleware for checking permissions before command execution"""
    
    def __init__(self):
        self.handler_permissions = {}
    
    def register_handler(self, handler_name: str, permissions: dict):
        """Register permission requirements for a handler"""
        self.handler_permissions[handler_name] = permissions
    
    async def check_permissions(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE,
        handler_name: str
    ) -> bool:
        """Check if user has required permissions"""
        if handler_name not in self.handler_permissions:
            return True  # No restrictions
        
        perms = self.handler_permissions[handler_name]
        
        # Check admin requirement
        if perms.get('admin_only', False):
            from core.helpers import PermissionChecker
            if not await PermissionChecker.is_user_admin(update, context):
                return False
        
        # Check group requirement
        if perms.get('group_only', False):
            if update.effective_chat.type == 'private':
                return False
        
        # Check private requirement
        if perms.get('private_only', False):
            if update.effective_chat.type != 'private':
                return False
        
        return True

# Global middleware instance
permission_middleware = PermissionMiddleware()
