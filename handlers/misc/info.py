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
    "commands": ["start"],
    "description": "Start the bot and show welcome message",
    "usage": "/start",
    "category": "misc",
    "admin_only": False,
    "group_only": False
}

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle start command"""
    await handle_start(update, context)

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
