"""
Constants and enums for ZyraX Bot
"""
from enum import Enum

# Bot Information
BOT_NAME = "ZyraX"
BOT_USERNAME = "ZyraXRobot"
BOT_VERSION = "1.0.0"

# Time Constants (in seconds)
MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY
MONTH = 30 * DAY

# Limits
MAX_MESSAGE_LENGTH = 4096
MAX_CAPTION_LENGTH = 1024
MAX_BUTTON_TEXT_LENGTH = 64
MAX_WARNS_PER_USER = 10
MAX_ADMIN_CACHE_AGE = 600  # 10 minutes

# File size limits (in bytes)
MAX_PHOTO_SIZE = 10 * 1024 * 1024  # 10MB
MAX_DOCUMENT_SIZE = 50 * 1024 * 1024  # 50MB

# Action Types
class ActionType(Enum):
    BAN = "ban"
    UNBAN = "unban"
    MUTE = "mute"
    UNMUTE = "unmute"
    KICK = "kick"
    WARN = "warn"
    UNWARN = "unwarn"
    PROMOTE = "promote"
    DEMOTE = "demote"
    PIN = "pin"
    UNPIN = "unpin"
    DELETE = "delete"
    PURGE = "purge"

# Lock Types
class LockType(Enum):
    STICKER = "sticker"
    ANIMATION = "animation"
    MEDIA = "media"
    URL = "url"
    BUTTON = "button"
    FORWARD = "forward"
    DOCUMENT = "document"
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    VOICE = "voice"
    CONTACT = "contact"
    LOCATION = "location"
    RTL = "rtl"
    EMAIL = "email"
    PHONE = "phone"
    BOT = "bot"
    INLINE = "inline"
    GAME = "game"
    POLL = "poll"
    DICE = "dice"

# Ban/Mute Modes
class PunishmentMode(Enum):
    BAN = "ban"
    MUTE = "mute"
    KICK = "kick"
    WARN = "warn"
    NOTHING = "nothing"

# Captcha Types
class CaptchaType(Enum):
    BUTTON = "button"
    MATH = "math"
    TEXT = "text"

# Flood Modes
class FloodMode(Enum):
    BAN = "ban"
    MUTE = "mute"
    KICK = "kick"
    WARN = "warn"

# Log Categories
class LogCategory(Enum):
    ADMIN = "admin"
    BAN = "ban"
    MUTE = "mute"
    WARN = "warn"
    KICK = "kick"
    PROMOTE = "promote"
    DEMOTE = "demote"
    PURGE = "purge"
    PIN = "pin"
    FILTER = "filter"
    BLOCKLIST = "blocklist"
    CAPTCHA = "captcha"
    FLOOD = "flood"
    LOCK = "lock"
    REPORT = "report"
    FEDERATION = "federation"

# Service Message Types
class ServiceType(Enum):
    JOIN = "join"
    LEAVE = "leave"
    BOOST = "boost"
    LOCATION = "location"
    VOICE_CHAT = "voice_chat"
    ALL = "all"

# Chat Types
class ChatType(Enum):
    PRIVATE = "private"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"

# User Status
class UserStatus(Enum):
    CREATOR = "creator"
    ADMINISTRATOR = "administrator"
    MEMBER = "member"
    RESTRICTED = "restricted"
    LEFT = "left"
    KICKED = "kicked"

# Button Types
class ButtonType(Enum):
    URL = "url"
    CALLBACK = "callback"

# File Types
class FileType(Enum):
    PHOTO = "photo"
    VIDEO = "video"
    ANIMATION = "animation"
    DOCUMENT = "document"
    STICKER = "sticker"
    AUDIO = "audio"
    VOICE = "voice"
    VIDEO_NOTE = "video_note"
    CONTACT = "contact"
    LOCATION = "location"
    VENUE = "venue"
    POLL = "poll"
    DICE = "dice"
    GAME = "game"

# Permission flags
ADMIN_PERMISSIONS = [
    "can_change_info",
    "can_delete_messages",
    "can_invite_users",
    "can_restrict_members",
    "can_pin_messages",
    "can_promote_members",
    "can_manage_chat",
    "can_manage_video_chats",
    "can_manage_topics",
    "is_anonymous"
]

# Time parsing regex patterns
TIME_PATTERNS = {
    's': 1,
    'm': MINUTE,
    'h': HOUR,
    'd': DAY,
    'w': WEEK,
    'M': MONTH
}

# Default messages
DEFAULT_MESSAGES = {
    "welcome": "Welcome {mention}! 👋",
    "goodbye": "Goodbye {first}! 👋",
    "rules": "No rules have been set for this chat.",
    "ban_message": "Banned user {mention} from {chat}",
    "unban_message": "Unbanned user {mention} from {chat}",
    "mute_message": "Muted user {mention} in {chat}",
    "unmute_message": "Unmuted user {mention} in {chat}",
    "kick_message": "Kicked user {mention} from {chat}",
    "warn_message": "⚠️ Warning {count}/{limit} for {mention}\nReason: {reason}",
    "flood_message": "Flooding detected! Taking action against {mention}",
    "captcha_message": "Welcome {mention}! Please solve the captcha below to verify you're human:",
    "level_up": "🎉 Congratulations {mention}! You reached level {level}!"
}

# Emoji constants
EMOJIS = {
    "warning": "⚠️",
    "ban": "🔨",
    "mute": "🔇",
    "kick": "👢",
    "success": "✅",
    "error": "❌",
    "info": "ℹ️",
    "pin": "📌",
    "lock": "🔒",
    "unlock": "🔓",
    "fire": "🔥",
    "star": "⭐",
    "heart": "❤️",
    "party": "🎉",
    "robot": "🤖",
    "shield": "🛡️",
    "crown": "👑",
    "gem": "💎",
    "money": "💰",
    "chart": "📊"
}

# Error messages
ERROR_MESSAGES = {
    "no_permission": "❌ You don't have permission to use this command.",
    "admin_only": "❌ This command is for admins only.",
    "group_only": "❌ This command can only be used in groups.",
    "private_only": "❌ This command can only be used in private chat.",
    "user_not_found": "❌ User not found.",
    "invalid_time": "❌ Invalid time format. Use: 1m, 2h, 3d, etc.",
    "database_error": "❌ Database error occurred. Please try again later.",
    "rate_limited": "❌ You're sending commands too fast. Please slow down.",
    "feature_disabled": "❌ This feature is disabled in this chat.",
    "federation_not_found": "❌ Federation not found.",
    "already_banned": "❌ User is already banned.",
    "not_banned": "❌ User is not banned.",
    "cannot_ban_admin": "❌ Cannot ban an administrator.",
    "cannot_restrict_admin": "❌ Cannot restrict an administrator.",
    "bot_not_admin": "❌ I need to be an admin to perform this action.",
    "insufficient_permissions": "❌ I don't have sufficient permissions.",
}

# Success messages
SUCCESS_MESSAGES = {
    "settings_updated": "✅ Settings updated successfully!",
    "user_banned": "✅ User banned successfully.",
    "user_unbanned": "✅ User unbanned successfully.",
    "user_muted": "✅ User muted successfully.",
    "user_unmuted": "✅ User unmuted successfully.",
    "user_kicked": "✅ User kicked successfully.",
    "user_warned": "✅ User warned successfully.",
    "warning_removed": "✅ Warning removed successfully.",
    "filter_added": "✅ Filter added successfully.",
    "filter_removed": "✅ Filter removed successfully.",
    "note_saved": "✅ Note saved successfully.",
    "note_deleted": "✅ Note deleted successfully.",
    "federation_created": "✅ Federation created successfully.",
    "federation_deleted": "✅ Federation deleted successfully.",
}

# Help categories
HELP_CATEGORIES = {
    "admin": "👑 Admin Commands",
    "moderation": "🔨 Moderation",
    "antiflood": "💧 Anti-Flood",
    "antiraid": "🛡️ Anti-Raid", 
    "approval": "✅ Approval System",
    "blocklists": "🚫 Blocklists",
    "captcha": "🔐 Captcha System",
    "filters": "📝 Filters",
    "notes": "📋 Notes",
    "greetings": "👋 Greetings",
    "locks": "🔒 Locks",
    "federations": "🤝 Federations",
    "pins": "📌 Pin Management",
    "reports": "📢 Reports",
    "rules": "📖 Rules",
    "clean": "🧹 Clean Service",
    "logs": "📊 Logging",
    "connections": "🔗 Connections",
    "disabling": "❌ Command Disabling",
    "language": "🌐 Language",
    "import_export": "📥 Import/Export",
    "misc": "🔧 Miscellaneous",
    "fun": "🎮 Fun Commands",
    "leveling": "📈 Leveling",
    "economy": "💰 Economy",
    "giveaways": "🎁 Giveaways",
    "tickets": "🎫 Tickets",
    "suggestions": "💡 Suggestions",
    "stats": "📊 Statistics"
}
