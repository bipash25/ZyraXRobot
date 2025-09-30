"""
Ban and unban commands
"""
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus

from core.decorators import admin_required, group_only, bot_admin_required, handle_errors
from core.helpers import MessageHelper, ChatHelper
from utils.user_resolver import UserResolver
from utils.time_parser import TimeParser

logger = logging.getLogger(__name__)

COMMAND_INFO = {
    "commands": ["ban", "unban", "tban", "sban", "dban"],
    "description": "Ban and unban users from the chat",
    "usage": "/ban <user> [reason], /tban <user> <time> [reason], /unban <user>",
    "category": "moderation",
    "permissions": ["can_restrict_members"],
    "admin_only": True,
    "group_only": True
}

@handle_errors
@group_only
@bot_admin_required
@admin_required(["can_restrict_members"])
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle ban/unban commands"""
    command = update.effective_message.text.split()[0][1:].lower()  # Remove /
    
    if command in ["ban", "sban", "dban"]:
        await handle_ban(update, context, command)
    elif command == "tban":
        await handle_tban(update, context)
    elif command == "unban":
        await handle_unban(update, context)

async def handle_ban(update: Update, context: ContextTypes.DEFAULT_TYPE, ban_type: str):
    """Handle ban, sban, dban commands"""
    # Resolve target user
    target_user = await UserResolver.resolve_user(update, context)
    
    if not target_user:
        await MessageHelper.send_message(
            update, context, "❌ Please specify a user to ban (reply, mention, username, or ID)"
        )
        return
    
    user_id = target_user['id']
    if not user_id:
        await MessageHelper.send_message(
            update, context, "❌ Could not determine user ID"
        )
        return
    
    # Check if target is admin
    if await _check_user_protection(update, context, user_id):
        return
    
    # Extract reason
    reason = UserResolver.extract_reason(" ".join(context.args) if context.args else "")
    
    try:
        # Determine ban options
        revoke_messages = ban_type == "dban"  # Delete messages for dban
        
        # Ban user
        success = await ChatHelper.ban_user(
            update, context, user_id, revoke_messages=revoke_messages
        )
        
        if success:
            user_mention = UserResolver.format_user_mention(target_user)
            
            if ban_type == "sban":
                # Silent ban - delete the command message
                await MessageHelper.delete_message(update, context)
            else:
                # Regular ban message
                ban_msg = f"🔨 **Banned** {user_mention}"
                if reason != "No reason provided":
                    ban_msg += f"\n**Reason:** {reason}"
                if ban_type == "dban":
                    ban_msg += "\n*Messages deleted*"
                
                await MessageHelper.send_message(update, context, ban_msg)
            
            # Log action
            context.action_log_data = {
                'target_user': str(user_id),
                'reason': reason,
                'metadata': {
                    'ban_type': ban_type,
                    'revoke_messages': revoke_messages
                }
            }
        else:
            await MessageHelper.send_message(
                update, context, "❌ Failed to ban user"
            )
    
    except Exception as e:
        logger.error(f"Error banning user: {e}")
        await MessageHelper.send_message(
            update, context, "❌ Error occurred while banning user"
        )

async def handle_tban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle temporary ban command"""
    if len(context.args) < 2:
        await MessageHelper.send_message(
            update, context, 
            "❌ Usage: `/tban <user> <time> [reason]`\nExample: `/tban @user 1h spam`"
        )
        return
    
    # Resolve target user
    target_user = await UserResolver.resolve_user(update, context)
    
    if not target_user:
        await MessageHelper.send_message(
            update, context, "❌ Please specify a user to ban"
        )
        return
    
    user_id = target_user['id']
    if not user_id:
        await MessageHelper.send_message(
            update, context, "❌ Could not determine user ID"
        )
        return
    
    # Check if target is admin
    if await _check_user_protection(update, context, user_id):
        return
    
    # Parse time duration
    time_arg = context.args[1] if len(context.args) > 1 else context.args[0]
    duration_seconds = TimeParser.parse_time_string(time_arg)
    
    if not duration_seconds:
        await MessageHelper.send_message(
            update, context, "❌ Invalid time format. Use: 1m, 2h, 3d, etc."
        )
        return
    
    # Validate duration (max 366 days for Telegram API)
    max_duration = 366 * 24 * 3600  # 366 days in seconds
    if duration_seconds > max_duration:
        await MessageHelper.send_message(
            update, context, "❌ Maximum ban duration is 366 days"
        )
        return
    
    # Calculate until_date
    until_date = datetime.now() + timedelta(seconds=duration_seconds)
    
    # Extract reason (skip user and time args)
    reason_parts = context.args[2:] if len(context.args) > 2 else []
    reason = " ".join(reason_parts) if reason_parts else "No reason provided"
    
    try:
        # Temporary ban user
        success = await ChatHelper.ban_user(update, context, user_id, until_date=until_date)
        
        if success:
            user_mention = UserResolver.format_user_mention(target_user)
            duration_text = TimeParser.format_duration(duration_seconds)
            
            ban_msg = f"⏰ **Temporarily banned** {user_mention} for {duration_text}"
            if reason != "No reason provided":
                ban_msg += f"\n**Reason:** {reason}"
            ban_msg += f"\n**Expires:** {until_date.strftime('%Y-%m-%d %H:%M UTC')}"
            
            await MessageHelper.send_message(update, context, ban_msg)
            
            # Log action
            context.action_log_data = {
                'target_user': str(user_id),
                'reason': reason,
                'metadata': {
                    'ban_type': 'tban',
                    'duration_seconds': duration_seconds,
                    'until_date': until_date.isoformat()
                }
            }
        else:
            await MessageHelper.send_message(
                update, context, "❌ Failed to ban user"
            )
    
    except Exception as e:
        logger.error(f"Error temporarily banning user: {e}")
        await MessageHelper.send_message(
            update, context, "❌ Error occurred while banning user"
        )

async def handle_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unban command"""
    # Resolve target user
    target_user = await UserResolver.resolve_user(update, context)
    
    if not target_user:
        await MessageHelper.send_message(
            update, context, "❌ Please specify a user to unban (reply, mention, username, or ID)"
        )
        return
    
    user_id = target_user['id']
    if not user_id:
        await MessageHelper.send_message(
            update, context, "❌ Could not determine user ID"
        )
        return
    
    try:
        # Unban user
        success = await ChatHelper.unban_user(update, context, user_id)
        
        if success:
            user_mention = UserResolver.format_user_mention(target_user)
            await MessageHelper.send_message(
                update, context, f"✅ **Unbanned** {user_mention}"
            )
            
            # Log action
            context.action_log_data = {
                'target_user': str(user_id),
                'reason': 'Unbanned',
                'metadata': {}
            }
        else:
            await MessageHelper.send_message(
                update, context, "❌ Failed to unban user (user may not be banned)"
            )
    
    except Exception as e:
        logger.error(f"Error unbanning user: {e}")
        await MessageHelper.send_message(
            update, context, "❌ Error occurred while unbanning user"
        )

async def _check_user_protection(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    """Check if user is protected from bans (admin, etc.)"""
    try:
        # Check if target is bot owner
        if user_id == context.bot_data.get('owner_id'):
            await MessageHelper.send_message(
                update, context, "❌ Cannot ban the bot owner"
            )
            return True
        
        # Check if target is the bot itself
        if user_id == context.bot.id:
            await MessageHelper.send_message(
                update, context, "❌ I cannot ban myself"
            )
            return True
        
        # Check if target is admin
        member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            await MessageHelper.send_message(
                update, context, "❌ Cannot ban an administrator"
            )
            return True
        
        return False
    
    except Exception as e:
        logger.debug(f"Error checking user protection: {e}")
        return False
