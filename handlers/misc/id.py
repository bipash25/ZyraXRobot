"""
ID command - Get user and chat IDs
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from core.helpers import MessageHelper

logger = logging.getLogger(__name__)

COMMAND_INFO = {
    "commands": ["id"],
    "description": "Get user and chat IDs",
    "usage": "/id",
    "category": "misc",
    "admin_only": False,
    "group_only": False
}

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
