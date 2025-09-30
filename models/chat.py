"""
Chat model for database operations
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from core.constants import LockType, FloodMode, PunishmentMode, CaptchaType

@dataclass
class ChatSettings:
    """Chat settings data class"""
    # Basic info
    chat_id: str
    chat_type: str = "supergroup"
    title: str = "Unknown"
    
    # Admin settings
    anon_admin: bool = False
    admin_error: bool = True
    admin_cache: List[str] = field(default_factory=list)
    admin_cache_updated: Optional[datetime] = None
    
    # Antiflood settings
    flood_limit: int = 10
    flood_mode: str = FloodMode.MUTE.value
    flood_timer: Dict[str, int] = field(default_factory=lambda: {"count": 10, "duration": 30})
    clear_flood: bool = True
    
    # Antiraid settings
    antiraid_enabled: bool = False
    antiraid_duration: int = 21600  # 6 hours
    antiraid_action_time: int = 3600  # 1 hour
    auto_antiraid: int = 0
    
    # Lock settings
    locks: Dict[str, bool] = field(default_factory=lambda: {
        lock_type.value: False for lock_type in LockType
    })
    lock_warns: bool = True
    allowlist: List[str] = field(default_factory=list)
    
    # Captcha settings
    captcha_enabled: bool = False
    captcha_mode: str = CaptchaType.BUTTON.value
    captcha_rules: bool = False
    captcha_mute_time: int = 0
    captcha_kick: bool = False
    captcha_kick_time: int = 0
    
    # Greeting settings
    welcome_enabled: bool = True
    welcome_text: str = "Welcome {mention}!"
    goodbye_enabled: bool = False
    goodbye_text: str = "Goodbye {first}!"
    clean_welcome: bool = False
    
    # Warning settings
    warn_mode: str = PunishmentMode.BAN.value
    warn_limit: int = 3
    warn_time: int = 0
    
    # Federation settings
    fed_id: Optional[str] = None
    quiet_fed: bool = False
    
    # Log settings
    log_channel_id: Optional[int] = None
    log_categories: List[str] = field(default_factory=list)
    
    # Language
    language: str = "en"
    
    # Clean service settings
    clean_service: Dict[str, bool] = field(default_factory=lambda: {
        "all": False, "join": False, "leave": False,
        "boost": False, "location": False, "voice_chat": False
    })
    
    # Reports
    reports_enabled: bool = True
    
    # Rules
    rules: Optional[str] = None
    private_rules: bool = False
    rules_button: str = "Rules"
    
    # Disabled commands
    disabled_commands: List[str] = field(default_factory=list)
    disable_delete: bool = False
    disable_admin: bool = False
    
    # Notes
    private_notes: bool = False
    
    # Pins
    anti_channel_pin: bool = False
    clean_linked: bool = False
    
    # Topics (for forum groups)
    action_topic_id: Optional[int] = None
    
    # Connections
    connected_chat: Optional[int] = None
    
    # Leveling
    leveling_enabled: bool = False
    level_up_message: str = "Congrats {mention}, you reached level {level}!"
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        data = asdict(self)
        # Convert chat_id to _id for MongoDB
        data["_id"] = data.pop("chat_id")
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSettings':
        """Create instance from database document"""
        # Convert _id back to chat_id
        if "_id" in data:
            data["chat_id"] = data.pop("_id")
        
        # Handle datetime fields
        for field_name in ["created_at", "updated_at", "admin_cache_updated"]:
            if field_name in data and data[field_name] is not None:
                if isinstance(data[field_name], str):
                    data[field_name] = datetime.fromisoformat(data[field_name])
        
        # Filter out unknown fields
        valid_fields = set(cls.__dataclass_fields__.keys())
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()

class Chat:
    """Chat operations wrapper"""
    
    @staticmethod
    def create_default_settings(chat_id: int, chat_type: str = "supergroup", title: str = "Unknown") -> ChatSettings:
        """Create default chat settings"""
        return ChatSettings(
            chat_id=str(chat_id),
            chat_type=chat_type,
            title=title
        )
    
    @staticmethod
    def validate_lock_type(lock_type: str) -> bool:
        """Validate if lock type is valid"""
        return lock_type in [lt.value for lt in LockType]
    
    @staticmethod
    def validate_flood_mode(mode: str) -> bool:
        """Validate if flood mode is valid"""
        return mode in [fm.value for fm in FloodMode]
    
    @staticmethod
    def validate_warn_mode(mode: str) -> bool:
        """Validate if warn mode is valid"""
        return mode in [pm.value for pm in PunishmentMode]
    
    @staticmethod
    def validate_captcha_mode(mode: str) -> bool:
        """Validate if captcha mode is valid"""
        return mode in [ct.value for ct in CaptchaType]
