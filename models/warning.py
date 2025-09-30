"""
Warning model for database operations
"""
from typing import Dict, Any
from datetime import datetime
from dataclasses import dataclass, field, asdict
from bson import ObjectId

@dataclass
class WarningData:
    """Warning data model"""
    chat_id: str
    user_id: str
    reason: str
    warned_by: str
    warn_count: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    _id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        data = asdict(self)
        if self._id is None:
            data.pop("_id")
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WarningData':
        """Create instance from database document"""
        # Handle ObjectId
        if "_id" in data and isinstance(data["_id"], ObjectId):
            data["_id"] = str(data["_id"])
        
        # Handle datetime
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        
        return cls(**data)

class Warning:
    """Warning operations wrapper"""
    pass
