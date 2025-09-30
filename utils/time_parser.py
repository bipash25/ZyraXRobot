"""
Time parsing utilities for ZyraX Bot
"""
import re
from typing import Optional, Tuple
from core.constants import TIME_PATTERNS

class TimeParser:
    """Parse time strings like '1m', '2h', '3d', etc."""
    
    @staticmethod
    def parse_time_string(time_str: str) -> Optional[int]:
        """
        Parse time string and return seconds
        
        Args:
            time_str: Time string like '1m', '2h', '3d', '1w', '1M'
            
        Returns:
            Number of seconds or None if invalid
        """
        if not time_str:
            return None
        
        # Remove spaces and convert to lowercase
        time_str = time_str.replace(" ", "").strip()
        
        # Regex pattern to match number + unit
        pattern = r'^(\d+)([smhdwM])$'
        match = re.match(pattern, time_str)
        
        if not match:
            return None
        
        amount, unit = match.groups()
        amount = int(amount)
        
        # Get multiplier for unit
        multiplier = TIME_PATTERNS.get(unit)
        if multiplier is None:
            return None
        
        return amount * multiplier
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """
        Format seconds into human readable duration
        
        Args:
            seconds: Number of seconds
            
        Returns:
            Human readable string like "2 days, 3 hours"
        """
        if seconds == 0:
            return "0 seconds"
        
        units = [
            ("week", 604800),  # 7 days
            ("day", 86400),    # 24 hours
            ("hour", 3600),    # 60 minutes
            ("minute", 60),    # 60 seconds
            ("second", 1)
        ]
        
        parts = []
        
        for unit_name, unit_seconds in units:
            if seconds >= unit_seconds:
                unit_count = seconds // unit_seconds
                seconds %= unit_seconds
                
                if unit_count == 1:
                    parts.append(f"{unit_count} {unit_name}")
                else:
                    parts.append(f"{unit_count} {unit_name}s")
        
        if len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            return f"{parts[0]} and {parts[1]}"
        else:
            return ", ".join(parts[:-1]) + f", and {parts[-1]}"
    
    @staticmethod
    def is_valid_duration(duration_str: str) -> bool:
        """Check if duration string is valid"""
        return TimeParser.parse_time_string(duration_str) is not None
    
    @staticmethod
    def parse_duration_with_validation(duration_str: str, min_seconds: int = 0, max_seconds: int = None) -> Tuple[Optional[int], Optional[str]]:
        """
        Parse duration with validation
        
        Args:
            duration_str: Duration string to parse
            min_seconds: Minimum allowed seconds
            max_seconds: Maximum allowed seconds (None for no limit)
            
        Returns:
            Tuple of (seconds, error_message)
        """
        seconds = TimeParser.parse_time_string(duration_str)
        
        if seconds is None:
            return None, "Invalid time format. Use format like: 1m, 2h, 3d, 1w"
        
        if seconds < min_seconds:
            min_formatted = TimeParser.format_duration(min_seconds)
            return None, f"Duration must be at least {min_formatted}"
        
        if max_seconds and seconds > max_seconds:
            max_formatted = TimeParser.format_duration(max_seconds)
            return None, f"Duration cannot exceed {max_formatted}"
        
        return seconds, None

# Convenience function for backward compatibility
def parse_time_string(time_str: str) -> Optional[int]:
    """Parse time string and return seconds"""
    return TimeParser.parse_time_string(time_str)
