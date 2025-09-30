"""
Filter model for database operations
"""
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from bson import ObjectId

@dataclass
class FilterData:
    """Filter data model"""
    chat_id: str
    trigger: str
    response: str
    file_id: Optional[str] = None
    file_type: Optional[str] = None
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    _id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        data = asdict(self)
        if self._id is None:
            data.pop("_id")
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FilterData':
        """Create instance from database document"""
        # Handle ObjectId
        if "_id" in data and isinstance(data["_id"], ObjectId):
            data["_id"] = str(data["_id"])
        
        # Handle datetime
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        
        return cls(**data)

class Filter:
    """Filter operations wrapper"""
    pass
