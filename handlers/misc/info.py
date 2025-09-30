"""
Basic info commands: start, help, id, info
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from core.helpers import MessageHelper, PermissionChecker
from core.constants import BOT_NAME, BOT_VERSION
from handlers.loader import get_command_loader

logger = logging.getLogger(__name__)

COMMAND_INFO = {
    "commands": ["start", "help", "id", "info"],
    "description": "Basic bot information commands",
    "usage": "/start, /help [category], /id, /info [user]",
    "category": "misc",
    "admin_only": False,
    "group_only": False
}

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle basic info commands"""
    command = update.effective_message.text.split()[0][1:].lower()  # Remove /
    
    if command == "start":
        await handle_start(update, context)
    elif command == "help":
        await handle_help(update, context)
    elif command == "id":
        await handle_id(update, context)
    elif command == "info":
        await handle_info(update, context)

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.type == "private":
        # Private chat start message
        text = f"""
🤖 **Welcome to {BOT_NAME}!**

I'm an advanced Telegram bot designed to help manage your groups with powerful moderation, anti-spam, and community features.

**🎯 Key Features:**
• **Moderation** - Ban, mute, kick, warn users
• **Anti-Spam** - Flood protection, raid protection, captcha
• **Content Management** - Filters, notes, welcome messages
• **Federations** - Connect multiple chats
• **Leveling & Economy** - XP system and virtual currency
• **And much more!**

**📚 Getting Started:**
• Add me to your group as an admin
• Use `/help` to see all available commands
• Use `/settings` to configure features

**💬 Need Help?**
Use `/help [category]` to see specific commands or contact my developers.

Version: {BOT_VERSION}
"""
    else:
        # Group start message
        text = f"""
👋 Hello {user.mention_markdown_v2()}!

I'm **{BOT_NAME}**, your group management assistant. I'm here to help keep this chat organized and fun!

Use `/help` to see what I can do, or `/settings` to configure my features.
"""
    
    await MessageHelper.send_message(update, context, text)

async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    loader = get_command_loader()
    if not loader:
        await MessageHelper.send_message(
            update, context, "❌ Command loader not available"
        )
        return
    
    # Check if user is admin (affects visible commands)
    is_admin = await PermissionChecker.is_user_admin(update, context)
    
    # Get category from arguments
    category = None
    if context.args:
        category = context.args[0].lower()
    
    try:
        help_text = loader.generate_help_text(category, is_admin)
        await MessageHelper.send_message(update, context, help_text)
    except Exception as e:
        logger.error(f"Error generating help: {e}")
        await MessageHelper.send_message(
            update, context, "❌ Error generating help text"
        )

async def handle_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /id command"""
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    
    text = f"**🆔 ID Information**\n\n"
    
    # Chat information
    text += f"**Chat ID:** `{chat.id}`\n"
    if chat.type != "private":
        text += f"**Chat Title:** {chat.title}\n"
        text += f"**Chat Type:** {chat.type}\n"
    
    # User information (sender)
    text += f"\n**Your ID:** `{user.id}`\n"
    text += f"**Your Name:** {user.first_name}"
    if user.last_name:
        text += f" {user.last_name}"
    if user.username:
        text += f"\n**Username:** @{user.username}"
    
    # Replied user information
    if message.reply_to_message and message.reply_to_message.from_user:
        replied_user = message.reply_to_message.from_user
        text += f"\n\n**Replied User ID:** `{replied_user.id}`"
        text += f"\n**Replied User:** {replied_user.first_name}"
        if replied_user.last_name:
            text += f" {replied_user.last_name}"
        if replied_user.username:
            text += f"\n**Username:** @{replied_user.username}"
    
    # Message ID
    text += f"\n\n**Message ID:** `{message.message_id}`"
    
    await MessageHelper.send_message(update, context, text)

async def handle_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /info command"""
    from utils.user_resolver import UserResolver
    
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
