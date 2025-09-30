"""
Promote and demote admin commands
"""
import logging
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus

from core.decorators import admin_required, group_only, bot_admin_required, handle_errors
from core.helpers import MessageHelper
from utils.user_resolver import UserResolver

logger = logging.getLogger(__name__)

COMMAND_INFO = {
    "commands": ["promote", "demote"],
    "description": "Promote or demote users to/from admin",
    "usage": "/promote <user> [title] or /demote <user>",
    "category": "admin",
    "permissions": ["can_promote_members"],
    "admin_only": True,
    "group_only": True
}

@handle_errors
@group_only
@bot_admin_required
@admin_required(["can_promote_members"])
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle promote/demote commands"""
    command = update.effective_message.text.split()[0][1:].lower()  # Remove /
    
    if command == "promote":
        await handle_promote(update, context)
    elif command == "demote":
        await handle_demote(update, context)

async def handle_promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /promote command"""
    # Resolve target user
    target_user = await UserResolver.resolve_user(update, context)
    
    if not target_user:
        await MessageHelper.send_message(
            update, context, "❌ Please specify a user to promote (reply, mention, username, or ID)"
        )
        return
    
    user_id = target_user['id']
    if not user_id:
        await MessageHelper.send_message(
            update, context, "❌ Could not determine user ID"
        )
        return
    
    # Check if user is already admin
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            await MessageHelper.send_message(
                update, context, "❌ User is already an administrator"
            )
            return
    except Exception as e:
        logger.error(f"Error checking member status: {e}")
        await MessageHelper.send_message(
            update, context, "❌ Error checking user status"
        )
        return
    
    # Get custom title if provided
    custom_title = None
    if len(context.args) > 1:
        # Extract title from args (skip first arg which is user identifier)
        title_parts = context.args[1:]
        custom_title = " ".join(title_parts)[:16]  # Max 16 characters
    
    try:
        # Promote user with default admin permissions
        await context.bot.promote_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_promote_members=False,
            is_anonymous=False,
            can_manage_chat=False,
            can_manage_video_chats=False
        )
        
        # Set custom title if provided
        if custom_title:
            try:
                await context.bot.set_chat_administrator_custom_title(
                    chat_id=update.effective_chat.id,
                    user_id=user_id,
                    custom_title=custom_title
                )
            except Exception as e:
                logger.warning(f"Could not set custom title: {e}")
        
        # Format success message
        user_mention = UserResolver.format_user_mention(target_user)
        success_msg = f"✅ **Promoted** {user_mention} to administrator"
        
        if custom_title:
            success_msg += f" with title: **{custom_title}**"
        
        await MessageHelper.send_message(update, context, success_msg)
        
        # Log action
        context.action_log_data = {
            'target_user': str(user_id),
            'reason': f"Promoted to admin{f' with title: {custom_title}' if custom_title else ''}",
            'metadata': {'custom_title': custom_title}
        }
    
    except Exception as e:
        logger.error(f"Error promoting user: {e}")
        await MessageHelper.send_message(
            update, context, "❌ Failed to promote user. Make sure I have the required permissions."
        )

async def handle_demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /demote command"""
    # Resolve target user
    target_user = await UserResolver.resolve_user(update, context)
    
    if not target_user:
        await MessageHelper.send_message(
            update, context, "❌ Please specify a user to demote (reply, mention, username, or ID)"
        )
        return
    
    user_id = target_user['id']
    if not user_id:
        await MessageHelper.send_message(
            update, context, "❌ Could not determine user ID"
        )
        return
    
    # Check if user is admin
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        
        if member.status == ChatMemberStatus.OWNER:
            await MessageHelper.send_message(
                update, context, "❌ Cannot demote the chat creator"
            )
            return
        
        if member.status != ChatMemberStatus.ADMINISTRATOR:
            await MessageHelper.send_message(
                update, context, "❌ User is not an administrator"
            )
            return
    
    except Exception as e:
        logger.error(f"Error checking member status: {e}")
        await MessageHelper.send_message(
            update, context, "❌ Error checking user status"
        )
        return
    
    try:
        # Demote user by removing all admin permissions
        await context.bot.promote_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            is_anonymous=False,
            can_manage_chat=False,
            can_manage_video_chats=False
        )
        
        # Format success message
        user_mention = UserResolver.format_user_mention(target_user)
        success_msg = f"✅ **Demoted** {user_mention} from administrator"
        
        await MessageHelper.send_message(update, context, success_msg)
        
        # Log action
        context.action_log_data = {
            'target_user': str(user_id),
            'reason': 'Demoted from admin',
            'metadata': {}
        }
    
    except Exception as e:
        logger.error(f"Error demoting user: {e}")
        await MessageHelper.send_message(
            update, context, "❌ Failed to demote user. Make sure I have the required permissions."
        )
