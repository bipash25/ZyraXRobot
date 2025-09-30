"""
User info command - Get detailed user information
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from core.helpers import MessageHelper
from utils.user_resolver import UserResolver

logger = logging.getLogger(__name__)

COMMAND_INFO = {
    "commands": ["info"],
    "description": "Get detailed user information",
    "usage": "/info [user]",
    "category": "misc",
    "admin_only": False,
    "group_only": False
}

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /info command"""
    # Try to resolve target user
    target_user = await UserResolver.resolve_user(update, context)
    
    if not target_user:
        # Show info about sender
        target_user = {
            'id': update.effective_user.id,
            'first_name': update.effective_user.first_name,
            'last_name': update.effective_user.last_name,
            'username': update.effective_user.username,
            'is_bot': update.effective_user.is_bot
        }
    
    try:
        text = f"**👤 User Information**\n\n"
        text += f"**ID:** `{target_user['id']}`\n"
        text += f"**Name:** {target_user['first_name']}"
        if target_user.get('last_name'):
            text += f" {target_user['last_name']}"
        text += "\n"
        
        if target_user.get('username'):
            text += f"**Username:** @{target_user['username']}\n"
        
        text += f"**Is Bot:** {'Yes' if target_user.get('is_bot') else 'No'}\n"
        
        # Get additional info if in group
        if update.effective_chat.type != "private":
            try:
                member = await context.bot.get_chat_member(
                    update.effective_chat.id, target_user['id']
                )
                text += f"**Status:** {member.status.title()}\n"
                
                if member.status == "administrator":
                    perms = []
                    if member.can_delete_messages:
                        perms.append("Delete Messages")
                    if member.can_restrict_members:
                        perms.append("Restrict Members")
                    if member.can_promote_members:
                        perms.append("Promote Members")
                    if member.can_change_info:
                        perms.append("Change Info")
                    if member.can_invite_users:
                        perms.append("Invite Users")
                    if member.can_pin_messages:
                        perms.append("Pin Messages")
                    
                    if perms:
                        text += f"**Permissions:** {', '.join(perms)}\n"
            
            except Exception as e:
                logger.debug(f"Could not get member info: {e}")
        
        # Try to get user data from database
        try:
            from core.database import get_user_data
            user_data = await get_user_data(target_user['id'])
            
            if user_data:
                text += f"\n**🗃️ Database Info:**\n"
                text += f"**Language:** {user_data.get('language', 'en')}\n"
                
                # Show chat-specific data if in group
                if update.effective_chat.type != "private":
                    chat_data = user_data.get('chat_data', {}).get(
                        str(update.effective_chat.id), {}
                    )
                    if chat_data:
                        if chat_data.get('approved'):
                            text += "**Status:** Approved ✅\n"
                        if chat_data.get('warnings', 0) > 0:
                            text += f"**Warnings:** {chat_data['warnings']}\n"
                        if chat_data.get('level', 0) > 0:
                            text += f"**Level:** {chat_data['level']} "
                            text += f"(XP: {chat_data.get('xp', 0)})\n"
        
        except Exception as e:
            logger.debug(f"Could not get user database info: {e}")
        
        await MessageHelper.send_message(update, context, text)
    
    except Exception as e:
        logger.error(f"Error in info command: {e}")
        await MessageHelper.send_message(
            update, context, "❌ Error retrieving user information"
        )
