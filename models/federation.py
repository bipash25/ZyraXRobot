"""
Federation model for database operations
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict

@dataclass
class FederationBan:
    """Federation ban entry"""
    user_id: str
    reason: str
    banned_by: str
    banned_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FederationBan':
        if "banned_at" in data and isinstance(data["banned_at"], str):
            data["banned_at"] = datetime.fromisoformat(data["banned_at"])
        return cls(**data)

@dataclass
class FederationData:
    """Federation data model"""
    fed_id: str
    name: str
    owner_id: str
    admins: List[str] = field(default_factory=list)
    
    # Settings
    fed_notif: bool = True
    fed_reason_required: bool = True
    
    # Subscriptions
    subscribed_feds: List[str] = field(default_factory=list)
    
    # Bans
    banned_users: List[FederationBan] = field(default_factory=list)
    
    # Log
    log_channel_id: Optional[int] = None
    log_language: str = "en"
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        data = asdict(self)
        data["_id"] = data.pop("fed_id")
        
        # Convert banned_users to dicts
        data["banned_users"] = [ban.to_dict() for ban in self.banned_users]
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FederationData':
        """Create instance from database document"""
        if "_id" in data:
            data["fed_id"] = data.pop("_id")
        
        # Handle datetime fields
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        
        # Convert banned_users back to objects
        if "banned_users" in data:
            data["banned_users"] = [FederationBan.from_dict(ban) for ban in data["banned_users"]]
        
        # Filter unknown fields
        valid_fields = set(cls.__dataclass_fields__.keys())
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)

class Federation:
    """Federation operations wrapper"""
    
    @staticmethod
    def generate_fed_id() -> str:
        """Generate unique federation ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    @staticmethod
    def create_federation(name: str, owner_id: int) -> FederationData:
        """Create new federation"""
        return FederationData(
            fed_id=Federation.generate_fed_id(),
            name=name,
            owner_id=str(owner_id)
        )
