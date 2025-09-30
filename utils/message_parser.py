"""
Message parsing utilities for ZyraX Bot
"""
import re
from typing import Dict, Any, List, Tuple, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class MessageParser:
    """Parse messages with markdown, buttons, and variable substitution"""
    
    @staticmethod
    def parse_buttons(text: str) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
        """
        Parse button syntax from text and return cleaned text + keyboard
        
        Button syntax: [Button Text](buttonurl:URL)
        Multiple buttons on same row: [Button1](buttonurl:URL1) [Button2](buttonurl:URL2)
        New row: Use newline
        
        Args:
            text: Text containing button syntax
            
        Returns:
            Tuple of (cleaned_text, keyboard_markup)
        """
        if not text:
            return text, None
        
        # Find all button patterns
        button_pattern = r'\[([^\]]+)\]\(buttonurl:([^)]+)\)'
        
        lines = text.split('\n')
        cleaned_lines = []
        keyboard_rows = []
        
        for line in lines:
            buttons_in_line = re.findall(button_pattern, line)
            
            if buttons_in_line:
                # This line contains buttons
                row = []
                for button_text, button_url in buttons_in_line:
                    row.append(InlineKeyboardButton(button_text.strip(), url=button_url.strip()))
                
                if row:
                    keyboard_rows.append(row)
                
                # Remove button syntax from text
                cleaned_line = re.sub(button_pattern, '', line).strip()
                if cleaned_line:
                    cleaned_lines.append(cleaned_line)
            else:
                # Regular text line
                cleaned_lines.append(line)
        
        cleaned_text = '\n'.join(cleaned_lines).strip()
        keyboard = InlineKeyboardMarkup(keyboard_rows) if keyboard_rows else None
        
        return cleaned_text, keyboard
    
    @staticmethod
    def substitute_variables(text: str, **variables) -> str:
        """
        Substitute variables in text using {variable} syntax
        
        Common variables:
        - {mention}: User mention
        - {first}: First name
        - {last}: Last name
        - {username}: Username
        - {chat}: Chat title
        - {count}: Count (for warnings, etc.)
        - {limit}: Limit value
        - {reason}: Reason text
        - {level}: Level (for leveling)
        - {xp}: XP amount
        
        Args:
            text: Text with variable placeholders
            **variables: Variable values to substitute
            
        Returns:
            Text with variables substituted
        """
        if not text:
            return text
        
        # Default values for common variables
        defaults = {
            'mention': 'User',
            'first': 'User',
            'last': '',
            'username': 'user',
            'chat': 'this chat',
            'count': '0',
            'limit': '0',
            'reason': 'No reason provided',
            'level': '0',
            'xp': '0'
        }
        
        # Merge with provided variables
        variables = {**defaults, **variables}
        
        # Substitute variables
        try:
            return text.format(**variables)
        except KeyError as e:
            # If a variable is missing, leave it as is
            return text
    
    @staticmethod
    def escape_markdown(text: str) -> str:
        """Escape markdown special characters"""
        if not text:
            return text
        
        # Characters that need escaping in Telegram markdown
        escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    @staticmethod
    def parse_markdown_buttons(text: str) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
        """
        Parse both markdown and buttons from text
        
        Args:
            text: Text with markdown and button syntax
            
        Returns:
            Tuple of (parsed_text, keyboard_markup)
        """
        # First parse buttons
        text, keyboard = MessageParser.parse_buttons(text)
        
        # Markdown is handled by Telegram's parse_mode
        return text, keyboard
    
    @staticmethod
    def validate_button_syntax(text: str) -> List[str]:
        """
        Validate button syntax and return list of errors
        
        Args:
            text: Text to validate
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        if not text:
            return errors
        
        button_pattern = r'\[([^\]]+)\]\(buttonurl:([^)]+)\)'
        buttons = re.findall(button_pattern, text)
        
        for i, (button_text, button_url) in enumerate(buttons, 1):
            # Validate button text
            if not button_text.strip():
                errors.append(f"Button {i}: Empty button text")
            elif len(button_text) > 64:
                errors.append(f"Button {i}: Button text too long (max 64 characters)")
            
            # Validate URL
            if not button_url.strip():
                errors.append(f"Button {i}: Empty URL")
            elif not button_url.startswith(('http://', 'https://', 'tg://')):
                errors.append(f"Button {i}: Invalid URL format")
        
        return errors
    
    @staticmethod
    def extract_file_info(message) -> Optional[Dict[str, Any]]:
        """
        Extract file information from message
        
        Args:
            message: Telegram message object
            
        Returns:
            Dict with file info or None
        """
        if not message:
            return None
        
        file_info = {}
        
        # Check for different file types
        if message.photo:
            file_info = {
                'type': 'photo',
                'file_id': message.photo[-1].file_id,  # Get largest photo
                'file_size': message.photo[-1].file_size
            }
        elif message.video:
            file_info = {
                'type': 'video',
                'file_id': message.video.file_id,
                'file_size': message.video.file_size,
                'duration': message.video.duration
            }
        elif message.animation:
            file_info = {
                'type': 'animation',
                'file_id': message.animation.file_id,
                'file_size': message.animation.file_size
            }
        elif message.document:
            file_info = {
                'type': 'document',
                'file_id': message.document.file_id,
                'file_size': message.document.file_size,
                'file_name': message.document.file_name
            }
        elif message.sticker:
            file_info = {
                'type': 'sticker',
                'file_id': message.sticker.file_id,
                'file_size': message.sticker.file_size
            }
        elif message.audio:
            file_info = {
                'type': 'audio',
                'file_id': message.audio.file_id,
                'file_size': message.audio.file_size,
                'duration': message.audio.duration
            }
        elif message.voice:
            file_info = {
                'type': 'voice',
                'file_id': message.voice.file_id,
                'file_size': message.voice.file_size,
                'duration': message.voice.duration
            }
        elif message.video_note:
            file_info = {
                'type': 'video_note',
                'file_id': message.video_note.file_id,
                'file_size': message.video_note.file_size,
                'duration': message.video_note.duration
            }
        
        return file_info if file_info else None
    
    @staticmethod
    def format_user_variables(user_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Format user data into template variables
        
        Args:
            user_data: User information dict
            
        Returns:
            Dict of template variables
        """
        variables = {}
        
        # Basic user info
        variables['first'] = user_data.get('first_name', 'User')
        variables['last'] = user_data.get('last_name', '')
        variables['username'] = user_data.get('username', 'user')
        
        # Create mention
        if user_data.get('username'):
            variables['mention'] = f"@{user_data['username']}"
        elif user_data.get('id'):
            variables['mention'] = f"[{variables['first']}](tg://user?id={user_data['id']})"
        else:
            variables['mention'] = variables['first']
        
        # Full name
        if variables['last']:
            variables['fullname'] = f"{variables['first']} {variables['last']}"
        else:
            variables['fullname'] = variables['first']
        
        return variables
    
    @staticmethod
    def split_message(text: str, max_length: int = 4096) -> List[str]:
        """
        Split long message into chunks
        
        Args:
            text: Text to split
            max_length: Maximum length per chunk
            
        Returns:
            List of text chunks
        """
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by lines first
        lines = text.split('\n')
        
        for line in lines:
            # If adding this line would exceed limit
            if len(current_chunk) + len(line) + 1 > max_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                
                # If single line is too long, split it
                if len(line) > max_length:
                    words = line.split(' ')
                    for word in words:
                        if len(current_chunk) + len(word) + 1 > max_length:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                                current_chunk = ""
                        current_chunk += word + " "
                else:
                    current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
