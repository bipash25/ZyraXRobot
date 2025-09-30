"""
Database connection and management for ZyraX Bot
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio

import motor.motor_asyncio
from pymongo import IndexModel, ASCENDING, DESCENDING
from config import config

logger = logging.getLogger(__name__)

class Database:
    """MongoDB database manager using Motor (async PyMongo)"""
    
    def __init__(self):
        self.client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.db: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None
        self._connected = False
    
    async def connect(self) -> bool:
        """Connect to MongoDB"""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGODB_URI)
            # Extract database name from URI or use default
            # Handle both local and Atlas URIs
            if '/' in config.MONGODB_URI:
                db_part = config.MONGODB_URI.split('/')[-1]
                # Remove query parameters for Atlas URIs
                db_name = db_part.split('?')[0] if '?' in db_part else db_part
                # Use default if empty
                db_name = db_name if db_name else 'zyraX_bot'
            else:
                db_name = 'zyraX_bot'
            self.db = self.client[db_name]
            
            # Test connection
            await self.client.admin.command('ping')
            self._connected = True
            
            # Setup indexes
            await self._setup_indexes()
            
            logger.info("Successfully connected to MongoDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("Disconnected from MongoDB")
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self._connected
    
    async def _setup_indexes(self):
        """Setup database indexes for performance"""
        try:
            # Chats collection indexes
            await self.db.chats.create_indexes([
                IndexModel([("_id", ASCENDING)]),  # chat_id
                IndexModel([("fed_id", ASCENDING)]),
                IndexModel([("title", "text")])  # Text search on chat titles
            ])
            
            # Users collection indexes
            await self.db.users.create_indexes([
                IndexModel([("_id", ASCENDING)]),  # user_id
                IndexModel([("username", ASCENDING)]),
                IndexModel([("chat_data", ASCENDING)])
            ])
            
            # Federations collection indexes
            await self.db.federations.create_indexes([
                IndexModel([("_id", ASCENDING)]),  # fed_id
                IndexModel([("owner_id", ASCENDING)]),
                IndexModel([("name", "text")])
            ])
            
            # Filters collection indexes
            await self.db.filters.create_indexes([
                IndexModel([("chat_id", ASCENDING), ("trigger", ASCENDING)]),
                IndexModel([("chat_id", ASCENDING)]),
                IndexModel([("created_at", DESCENDING)])
            ])
            
            # Notes collection indexes
            await self.db.notes.create_indexes([
                IndexModel([("chat_id", ASCENDING), ("name", ASCENDING)]),
                IndexModel([("chat_id", ASCENDING)]),
                IndexModel([("created_at", DESCENDING)])
            ])
            
            # Blocklists collection indexes
            await self.db.blocklists.create_indexes([
                IndexModel([("chat_id", ASCENDING), ("trigger", ASCENDING)]),
                IndexModel([("chat_id", ASCENDING)]),
                IndexModel([("created_at", DESCENDING)])
            ])
            
            # Captcha pending collection indexes
            await self.db.captcha_pending.create_indexes([
                IndexModel([("chat_id", ASCENDING), ("user_id", ASCENDING)]),
                IndexModel([("expires_at", ASCENDING)])  # For cleanup
            ])
            
            # Scheduled actions collection indexes
            await self.db.scheduled_actions.create_indexes([
                IndexModel([("execute_at", ASCENDING)]),
                IndexModel([("chat_id", ASCENDING)]),
                IndexModel([("user_id", ASCENDING)])
            ])
            
            # Action logs collection indexes
            await self.db.action_logs.create_indexes([
                IndexModel([("chat_id", ASCENDING), ("timestamp", DESCENDING)]),
                IndexModel([("action_type", ASCENDING)]),
                IndexModel([("performed_by", ASCENDING)]),
                IndexModel([("target_user", ASCENDING)])
            ])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")

# Collection wrappers with common operations
class ChatCollection:
    """Chat data operations"""
    
    def __init__(self, db):
        self.collection = db.chats
    
    async def get_chat(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Get chat by ID"""
        return await self.collection.find_one({"_id": str(chat_id)})
    
    async def create_chat(self, chat_id: int, chat_type: str, title: str) -> Dict[str, Any]:
        """Create new chat with default settings"""
        now = datetime.utcnow()
        chat_data = {
            "_id": str(chat_id),
            "chat_type": chat_type,
            "title": title,
            
            # Admin settings
            "anon_admin": False,
            "admin_error": True,
            "admin_cache": [],
            "admin_cache_updated": None,
            
            # Antiflood
            "flood_limit": 10,
            "flood_mode": "mute",
            "flood_timer": {"count": 10, "duration": 30},
            "clear_flood": True,
            
            # Antiraid
            "antiraid_enabled": False,
            "antiraid_duration": 21600,
            "antiraid_action_time": 3600,
            "auto_antiraid": 0,
            
            # Locks - all disabled by default
            "locks": {
                "sticker": False, "animation": False, "media": False,
                "url": False, "button": False, "forward": False,
                "document": False, "photo": False, "video": False,
                "audio": False, "voice": False, "contact": False,
                "location": False, "rtl": False, "email": False,
                "phone": False, "bot": False, "inline": False,
                "game": False, "poll": False, "dice": False
            },
            "lock_warns": True,
            "allowlist": [],
            
            # Captcha
            "captcha_enabled": False,
            "captcha_mode": "button",
            "captcha_rules": False,
            "captcha_mute_time": 0,
            "captcha_kick": False,
            "captcha_kick_time": 0,
            
            # Greetings
            "welcome_enabled": True,
            "welcome_text": "Welcome {mention}!",
            "goodbye_enabled": False,
            "goodbye_text": "Goodbye {first}!",
            "clean_welcome": False,
            
            # Warnings
            "warn_mode": "ban",
            "warn_limit": 3,
            "warn_time": 0,
            
            # Federations
            "fed_id": None,
            "quiet_fed": False,
            
            # Logs
            "log_channel_id": None,
            "log_categories": [],
            
            # Language
            "language": "en",
            
            # Clean service
            "clean_service": {
                "all": False, "join": False, "leave": False,
                "boost": False, "location": False, "voice_chat": False
            },
            
            # Reports
            "reports_enabled": True,
            
            # Rules
            "rules": None,
            "private_rules": False,
            "rules_button": "Rules",
            
            # Disabled commands
            "disabled_commands": [],
            "disable_delete": False,
            "disable_admin": False,
            
            # Notes
            "private_notes": False,
            
            # Pins
            "anti_channel_pin": False,
            "clean_linked": False,
            
            # Topics (for forum groups)
            "action_topic_id": None,
            
            # Connections
            "connected_chat": None,
            
            # Leveling
            "leveling_enabled": False,
            "level_up_message": "Congrats {mention}, you reached level {level}!",
            
            "created_at": now,
            "updated_at": now
        }
        
        await self.collection.insert_one(chat_data)
        return chat_data
    
    async def update_chat(self, chat_id: int, update_data: Dict[str, Any]) -> bool:
        """Update chat settings"""
        update_data["updated_at"] = datetime.utcnow()
        result = await self.collection.update_one(
            {"_id": str(chat_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def get_or_create_chat(self, chat_id: int, chat_type: str = "supergroup", title: str = "Unknown") -> Dict[str, Any]:
        """Get existing chat or create new one"""
        chat = await self.get_chat(chat_id)
        if not chat:
            chat = await self.create_chat(chat_id, chat_type, title)
        return chat

class UserCollection:
    """User data operations"""
    
    def __init__(self, db):
        self.collection = db.users
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return await self.collection.find_one({"_id": str(user_id)})
    
    async def create_user(self, user_id: int, username: str = None, first_name: str = "", last_name: str = "") -> Dict[str, Any]:
        """Create new user"""
        now = datetime.utcnow()
        user_data = {
            "_id": str(user_id),
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "chat_data": {},
            "language": "en",
            "created_at": now,
            "updated_at": now
        }
        
        await self.collection.insert_one(user_data)
        return user_data
    
    async def update_user(self, user_id: int, update_data: Dict[str, Any]) -> bool:
        """Update user data"""
        update_data["updated_at"] = datetime.utcnow()
        result = await self.collection.update_one(
            {"_id": str(user_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def get_or_create_user(self, user_id: int, username: str = None, first_name: str = "", last_name: str = "") -> Dict[str, Any]:
        """Get existing user or create new one"""
        user = await self.get_user(user_id)
        if not user:
            user = await self.create_user(user_id, username, first_name, last_name)
        return user
    
    async def get_user_chat_data(self, user_id: int, chat_id: int) -> Dict[str, Any]:
        """Get user's data for specific chat"""
        user = await self.get_or_create_user(user_id)
        chat_id_str = str(chat_id)
        
        if chat_id_str not in user.get("chat_data", {}):
            # Initialize chat data for user
            default_chat_data = {
                "approved": False,
                "warnings": 0,
                "warn_reasons": [],
                "last_warn": None,
                "message_count": 0,
                "flood_start": None,
                "xp": 0,
                "level": 0,
                "last_xp": None,
                "balance": 0,
                "bank": 0
            }
            
            await self.collection.update_one(
                {"_id": str(user_id)},
                {"$set": {f"chat_data.{chat_id_str}": default_chat_data}}
            )
            
            return default_chat_data
        
        return user["chat_data"][chat_id_str]
    
    async def update_user_chat_data(self, user_id: int, chat_id: int, update_data: Dict[str, Any]) -> bool:
        """Update user's chat-specific data"""
        chat_id_str = str(chat_id)
        
        # Ensure user exists first
        await self.get_or_create_user(user_id)
        
        # Update specific chat data
        update_dict = {}
        for key, value in update_data.items():
            update_dict[f"chat_data.{chat_id_str}.{key}"] = value
        
        update_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": str(user_id)},
            {"$set": update_dict}
        )
        return result.modified_count > 0

# Global database instance
database = Database()

# Collection instances
chats: Optional[ChatCollection] = None
users: Optional[UserCollection] = None

async def init_database():
    """Initialize database connection and collection wrappers"""
    global chats, users
    
    if await database.connect():
        chats = ChatCollection(database.db)
        users = UserCollection(database.db)
        return True
    return False

async def close_database():
    """Close database connection"""
    await database.disconnect()

# Utility functions for common operations
async def get_chat_settings(chat_id: int) -> Dict[str, Any]:
    """Get chat settings, creating defaults if needed"""
    if not chats:
        raise RuntimeError("Database not initialized")
    return await chats.get_or_create_chat(chat_id)

async def update_chat_setting(chat_id: int, setting: str, value: Any) -> bool:
    """Update a single chat setting"""
    if not chats:
        raise RuntimeError("Database not initialized")
    return await chats.update_chat(chat_id, {setting: value})

async def get_user_data(user_id: int, chat_id: int = None) -> Dict[str, Any]:
    """Get user data, optionally with chat-specific data"""
    if not users:
        raise RuntimeError("Database not initialized")
    
    if chat_id:
        return await users.get_user_chat_data(user_id, chat_id)
    else:
        return await users.get_or_create_user(user_id)

async def update_user_data(user_id: int, chat_id: int, **kwargs) -> bool:
    """Update user's chat-specific data"""
    if not users:
        raise RuntimeError("Database not initialized")
    return await users.update_user_chat_data(user_id, chat_id, kwargs)
