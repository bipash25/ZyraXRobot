"""
Help command with inline keyboard navigation
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from core.helpers import MessageHelper, PermissionChecker
from core.constants import BOT_NAME, HELP_CATEGORIES
from handlers.loader import get_command_loader

logger = logging.getLogger(__name__)

COMMAND_INFO = {
    "commands": ["help"],
    "description": "Show available commands and help",
    "usage": "/help [category]",
    "category": "misc",
    "admin_only": False,
    "group_only": False
}

# Callback handler for help navigation
CALLBACK_HANDLER = {
    "pattern": "^help:"
}

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    loader = get_command_loader()
    if not loader:
        await MessageHelper.send_message(
            update, context, "❌ Command loader not available"
        )
        return
    
    # Check if user is admin
    is_admin = await PermissionChecker.is_user_admin(update, context)
    
    # Get category from arguments
    if context.args:
        category = context.args[0].lower()
        await send_category_help(update, context, category, is_admin)
    else:
        await send_main_help(update, context, is_admin)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries for help navigation"""
    query = update.callback_query
    await query.answer()
    
    loader = get_command_loader()
    if not loader:
        return
    
    # Check if user is admin
    is_admin = await PermissionChecker.is_user_admin(update, context)
    
    # Parse callback data
    data = query.data.split(":")
    if len(data) < 2:
        return
    
    action = data[1]
    
    if action == "main":
        await edit_main_help(update, context, is_admin)
    elif action == "category":
        if len(data) >= 3:
            category = data[2]
            await edit_category_help(update, context, category, is_admin)

async def send_main_help(update: Update, context: ContextTypes.DEFAULT_TYPE, is_admin: bool):
    """Send main help message with category buttons"""
    loader = get_command_loader()
    
    text = f"**🤖 {BOT_NAME} - Available Commands**\n\n"
    text += "Choose a category below to see available commands:\n"
    
    # Create inline keyboard with category buttons
    keyboard = []
    row = []
    
    for i, (category, commands) in enumerate(loader.categories.items()):
        if not commands:
            continue
        
        # Count visible commands
        visible_count = sum(
            1 for cmd in commands
            if not loader.commands[cmd].get('admin_only', False) or is_admin
        )
        
        if visible_count == 0:
            continue
        
        category_title = HELP_CATEGORIES.get(category, category.title())
        emoji = category_title.split()[0] if category_title.split() else "📁"
        
        button = InlineKeyboardButton(
            f"{emoji} {category.title()}", 
            callback_data=f"help:category:{category}"
        )
        row.append(button)
        
        # 2 buttons per row
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    # Add remaining buttons
    if row:
        keyboard.append(row)
    
    # Add close button
    keyboard.append([InlineKeyboardButton("❌ Close", callback_data="help:close")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await MessageHelper.send_message(
        update, context, text, reply_markup=reply_markup
    )

async def edit_main_help(update: Update, context: ContextTypes.DEFAULT_TYPE, is_admin: bool):
    """Edit message to show main help"""
    loader = get_command_loader()
    query = update.callback_query
    
    text = f"**🤖 {BOT_NAME} - Available Commands**\n\n"
    text += "Choose a category below to see available commands:\n"
    
    # Create inline keyboard
    keyboard = []
    row = []
    
    for category, commands in loader.categories.items():
        if not commands:
            continue
        
        visible_count = sum(
            1 for cmd in commands
            if not loader.commands[cmd].get('admin_only', False) or is_admin
        )
        
        if visible_count == 0:
            continue
        
        category_title = HELP_CATEGORIES.get(category, category.title())
        emoji = category_title.split()[0] if category_title.split() else "📁"
        
        button = InlineKeyboardButton(
            f"{emoji} {category.title()}", 
            callback_data=f"help:category:{category}"
        )
        row.append(button)
        
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("❌ Close", callback_data="help:close")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def send_category_help(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str, is_admin: bool):
    """Send help for specific category"""
    loader = get_command_loader()
    
    if category not in loader.categories:
        await MessageHelper.send_message(
            update, context, f"❌ Unknown category: {category}"
        )
        return
    
    commands = loader.categories[category]
    if not commands:
        await MessageHelper.send_message(
            update, context, f"❌ No commands found in category: {category}"
        )
        return
    
    category_title = HELP_CATEGORIES.get(category, category.title())
    text = f"**{category_title}**\n\n"
    
    for command in commands:
        command_info = loader.commands[command]
        
        if command_info.get('admin_only', False) and not is_admin:
            continue
        
        description = command_info.get('description', 'No description')
        usage = command_info.get('usage', f'/{command}')
        
        text += f"• **{usage}**\n"
        text += f"  {description}\n\n"
    
    # Add back button
    keyboard = [[InlineKeyboardButton("⬅️ Back to Categories", callback_data="help:main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await MessageHelper.send_message(
        update, context, text.strip(), reply_markup=reply_markup
    )

async def edit_category_help(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str, is_admin: bool):
    """Edit message to show category help"""
    loader = get_command_loader()
    query = update.callback_query
    
    if category not in loader.categories:
        await query.answer("❌ Unknown category")
        return
    
    commands = loader.categories[category]
    if not commands:
        await query.answer("❌ No commands in this category")
        return
    
    category_title = HELP_CATEGORIES.get(category, category.title())
    text = f"**{category_title}**\n\n"
    
    for command in commands:
        command_info = loader.commands[command]
        
        if command_info.get('admin_only', False) and not is_admin:
            continue
        
        description = command_info.get('description', 'No description')
        usage = command_info.get('usage', f'/{command}')
        
        text += f"• **{usage}**\n"
        text += f"  {description}\n\n"
    
    keyboard = [[InlineKeyboardButton("⬅️ Back to Categories", callback_data="help:main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(text.strip(), reply_markup=reply_markup, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error editing help message: {e}")
