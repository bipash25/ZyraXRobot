"""
User model for database operations
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict

@dataclass
class UserChatData:
    """User data for a specific chat"""
    approved: bool = False
    warnings: int = 0
    warn_reasons: List[str] = field(default_factory=list)
    last_warn: Optional[datetime] = None
    
    # Antiflood tracking
    message_count: int = 0
    flood_start: Optional[datetime] = None
    
    # Leveling
    xp: int = 0
    level: int = 0
    last_xp: Optional[datetime] = None
    
    # Economy
    balance: int = 0
    bank: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserChatData':
        """Create instance from database document"""
        # Handle datetime fields
        for field_name in ["last_warn", "flood_start", "last_xp"]:
            if field_name in data and data[field_name] is not None:
                if isinstance(data[field_name], str):
                    data[field_name] = datetime.fromisoformat(data[field_name])
        
        # Filter out unknown fields
        valid_fields = set(cls.__dataclass_fields__.keys())
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)

@dataclass
class UserData:
    """User data model"""
    user_id: str
    username: Optional[str] = None
    first_name: str = ""
    last_name: str = ""
    chat_data: Dict[str, UserChatData] = field(default_factory=dict)
    language: str = "en"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        data = asdict(self)
        # Convert user_id to _id for MongoDB
        data["_id"] = data.pop("user_id")
        
        # Convert chat_data to dict format
        chat_data_dict = {}
        for chat_id, chat_data in data["chat_data"].items():
            if isinstance(chat_data, UserChatData):
                chat_data_dict[chat_id] = chat_data.to_dict()
            else:
                chat_data_dict[chat_id] = chat_data
        data["chat_data"] = chat_data_dict
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserData':
        """Create instance from database document"""
        # Convert _id back to user_id
        if "_id" in data:
            data["user_id"] = data.pop("_id")
        
        # Handle datetime fields
        for field_name in ["created_at", "updated_at"]:
            if field_name in data and data[field_name] is not None:
                if isinstance(data[field_name], str):
                    data[field_name] = datetime.fromisoformat(data[field_name])
        
        # Convert chat_data back to UserChatData objects
        chat_data_dict = {}
        if "chat_data" in data:
            for chat_id, chat_data in data["chat_data"].items():
                if isinstance(chat_data, dict):
                    chat_data_dict[chat_id] = UserChatData.from_dict(chat_data)
                else:
                    chat_data_dict[chat_id] = chat_data
        data["chat_data"] = chat_data_dict
        
        # Filter out unknown fields
        valid_fields = set(cls.__dataclass_fields__.keys())
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()
    
    def get_chat_data(self, chat_id: int) -> UserChatData:
        """Get or create chat data for specific chat"""
        chat_id_str = str(chat_id)
        if chat_id_str not in self.chat_data:
            self.chat_data[chat_id_str] = UserChatData()
        return self.chat_data[chat_id_str]
    
    def add_warning(self, chat_id: int, reason: str = "No reason provided"):
        """Add a warning to user in specific chat"""
        chat_data = self.get_chat_data(chat_id)
        chat_data.warnings += 1
        chat_data.warn_reasons.append(reason)
        chat_data.last_warn = datetime.utcnow()
        self.update_timestamp()
    
    def remove_warning(self, chat_id: int) -> bool:
        """Remove last warning from user in specific chat"""
        chat_data = self.get_chat_data(chat_id)
        if chat_data.warnings > 0:
            chat_data.warnings -= 1
            if chat_data.warn_reasons:
                chat_data.warn_reasons.pop()
            self.update_timestamp()
            return True
        return False
    
    def reset_warnings(self, chat_id: int):
        """Reset all warnings for user in specific chat"""
        chat_data = self.get_chat_data(chat_id)
        chat_data.warnings = 0
        chat_data.warn_reasons = []
        chat_data.last_warn = None
        self.update_timestamp()
    
    def approve(self, chat_id: int):
        """Approve user in specific chat"""
        chat_data = self.get_chat_data(chat_id)
        chat_data.approved = True
        self.update_timestamp()
    
    def unapprove(self, chat_id: int):
        """Unapprove user in specific chat"""
        chat_data = self.get_chat_data(chat_id)
        chat_data.approved = False
        self.update_timestamp()
    
    def add_xp(self, chat_id: int, amount: int = 1) -> bool:
        """Add XP to user in specific chat, returns True if leveled up"""
        chat_data = self.get_chat_data(chat_id)
        
        # Check cooldown (prevent XP farming)
        now = datetime.utcnow()
        if chat_data.last_xp and (now - chat_data.last_xp).seconds < 60:
            return False
        
        chat_data.xp += amount
        chat_data.last_xp = now
        
        # Calculate level (XP required = level^2 * 100)
        old_level = chat_data.level
        new_level = int((chat_data.xp / 100) ** 0.5)
        
        if new_level > old_level:
            chat_data.level = new_level
            self.update_timestamp()
            return True
        
        self.update_timestamp()
        return False
    
    def update_balance(self, chat_id: int, amount: int):
        """Update user balance in specific chat"""
        chat_data = self.get_chat_data(chat_id)
        chat_data.balance += amount
        self.update_timestamp()
    
    def transfer_to_bank(self, chat_id: int, amount: int) -> bool:
        """Transfer money from balance to bank"""
        chat_data = self.get_chat_data(chat_id)
        if chat_data.balance >= amount:
            chat_data.balance -= amount
            chat_data.bank += amount
            self.update_timestamp()
            return True
        return False
    
    def withdraw_from_bank(self, chat_id: int, amount: int) -> bool:
        """Withdraw money from bank to balance"""
        chat_data = self.get_chat_data(chat_id)
        if chat_data.bank >= amount:
            chat_data.bank -= amount
            chat_data.balance += amount
            self.update_timestamp()
            return True
        return False

class User:
    """User operations wrapper"""
    
    @staticmethod
    def create_default_data(user_id: int, username: str = None, first_name: str = "", last_name: str = "") -> UserData:
        """Create default user data"""
        return UserData(
            user_id=str(user_id),
            username=username,
            first_name=first_name,
            last_name=last_name
        )
    
    @staticmethod
    def calculate_level_from_xp(xp: int) -> int:
        """Calculate level from XP amount"""
        return int((xp / 100) ** 0.5)
    
    @staticmethod
    def calculate_xp_for_level(level: int) -> int:
        """Calculate XP required for specific level"""
        return level * level * 100
    
    @staticmethod
    def format_user_mention(user_data: UserData) -> str:
        """Format user mention string"""
        if user_data.username:
            return f"@{user_data.username}"
        return f"[{user_data.first_name}](tg://user?id={user_data.user_id})"
    
    @staticmethod
    def get_display_name(user_data: UserData) -> str:
        """Get user display name"""
        if user_data.first_name and user_data.last_name:
            return f"{user_data.first_name} {user_data.last_name}"
        elif user_data.first_name:
            return user_data.first_name
        elif user_data.username:
            return user_data.username
        else:
            return f"User {user_data.user_id}"
