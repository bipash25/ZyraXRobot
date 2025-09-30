"""
Dynamic command loader for ZyraX Bot
"""
import os
import sys
import importlib
import inspect
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler

logger = logging.getLogger(__name__)

class CommandLoader:
    """Dynamic command loader that scans and registers handlers"""
    
    def __init__(self, application: Application):
        self.application = application
        self.commands: Dict[str, Dict[str, Any]] = {}
        self.categories: Dict[str, List[str]] = {}
        self.loaded_modules: List[str] = []
    
    async def load_all_handlers(self, handlers_dir: str = "handlers") -> bool:
        """
        Load all command handlers from handlers directory
        
        Args:
            handlers_dir: Directory containing handler modules
            
        Returns:
            True if loading successful, False otherwise
        """
        try:
            handlers_path = Path(handlers_dir)
            
            if not handlers_path.exists():
                logger.error(f"Handlers directory {handlers_dir} not found")
                return False
            
            # Load handlers from each subdirectory
            for category_dir in handlers_path.iterdir():
                if category_dir.is_dir() and not category_dir.name.startswith('__'):
                    await self._load_category(category_dir)
            
            logger.info(f"Loaded {len(self.commands)} commands from {len(self.loaded_modules)} modules")
            return True
        
        except Exception as e:
            logger.error(f"Error loading handlers: {e}", exc_info=True)
            return False
    
    async def _load_category(self, category_path: Path) -> None:
        """Load all handlers from a category directory"""
        category_name = category_path.name
        self.categories[category_name] = []
        
        for handler_file in category_path.glob("*.py"):
            if handler_file.name.startswith('__'):
                continue
            
            try:
                await self._load_handler_file(handler_file, category_name)
            except Exception as e:
                logger.error(f"Error loading {handler_file}: {e}")
    
    async def _load_handler_file(self, handler_file: Path, category: str) -> None:
        """Load a single handler file"""
        # Build module path
        relative_path = handler_file.relative_to(Path.cwd())
        module_path = str(relative_path.with_suffix('')).replace(os.sep, '.')
        
        try:
            # Import the module
            if module_path in sys.modules:
                module = importlib.reload(sys.modules[module_path])
            else:
                module = importlib.import_module(module_path)
            
            # Check if module has COMMAND_INFO
            if not hasattr(module, 'COMMAND_INFO'):
                logger.warning(f"Module {module_path} has no COMMAND_INFO")
                return
            
            command_info = module.COMMAND_INFO
            
            # Validate command info
            if not self._validate_command_info(command_info, module_path):
                return
            
            # Register handlers based on command info
            await self._register_handlers(module, command_info, category)
            
            self.loaded_modules.append(module_path)
            logger.debug(f"Loaded module {module_path}")
        
        except Exception as e:
            logger.error(f"Error importing {module_path}: {e}")
    
    def _validate_command_info(self, command_info: Dict[str, Any], module_path: str) -> bool:
        """Validate command info structure"""
        required_fields = ['commands', 'description', 'category']
        
        for field in required_fields:
            if field not in command_info:
                logger.error(f"Module {module_path} missing required field: {field}")
                return False
        
        if not isinstance(command_info['commands'], list):
            logger.error(f"Module {module_path} commands must be a list")
            return False
        
        if not command_info['commands']:
            logger.error(f"Module {module_path} has empty commands list")
            return False
        
        return True
    
    async def _register_handlers(self, module, command_info: Dict[str, Any], category: str) -> None:
        """Register handlers from module"""
        commands = command_info['commands']
        
        # Look for handler functions in order of preference
        handler_func = None
        for func_name in ['handle', 'handler', 'main']:
            if hasattr(module, func_name):
                handler_func = getattr(module, func_name)
                break
        
        if not handler_func:
            logger.error(f"No handler function found in {module.__name__}")
            return
        
        # Register command handlers
        for command in commands:
            handler = CommandHandler(command, handler_func)
            self.application.add_handler(handler)
            
            # Store command info
            self.commands[command] = {
                **command_info,
                'handler_func': handler_func,
                'module': module.__name__,
                'category': category
            }
            
            self.categories[category].append(command)
        
        # Register message handler if specified
        if hasattr(module, 'MESSAGE_HANDLER') and hasattr(module, 'message_handler'):
            message_info = module.MESSAGE_HANDLER
            filters = message_info.get('filters')
            
            if filters:
                handler = MessageHandler(filters, module.message_handler)
                self.application.add_handler(handler)
                logger.debug(f"Registered message handler for {module.__name__}")
        
        # Register callback query handler if specified
        if hasattr(module, 'CALLBACK_HANDLER') and hasattr(module, 'callback_handler'):
            callback_info = module.CALLBACK_HANDLER
            pattern = callback_info.get('pattern')
            
            handler = CallbackQueryHandler(module.callback_handler, pattern=pattern)
            self.application.add_handler(handler)
            logger.debug(f"Registered callback handler for {module.__name__}")
    
    def get_command_info(self, command: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific command"""
        return self.commands.get(command)
    
    def get_commands_by_category(self, category: str) -> List[str]:
        """Get all commands in a category"""
        return self.categories.get(category, [])
    
    def get_all_categories(self) -> List[str]:
        """Get all available categories"""
        return list(self.categories.keys())
    
    def get_all_commands(self) -> List[str]:
        """Get all available commands"""
        return list(self.commands.keys())
    
    def is_command_enabled(self, command: str, chat_id: int) -> bool:
        """Check if command is enabled in chat"""
        # This would check database for disabled commands
        # For now, return True (implement later with database integration)
        return True
    
    def generate_help_text(self, category: str = None, user_is_admin: bool = False) -> str:
        """Generate help text for commands"""
        if category:
            return self._generate_category_help(category, user_is_admin)
        else:
            return self._generate_general_help(user_is_admin)
    
    def _generate_category_help(self, category: str, user_is_admin: bool) -> str:
        """Generate help text for specific category"""
        if category not in self.categories:
            return f"❌ Unknown category: {category}"
        
        commands = self.categories[category]
        if not commands:
            return f"❌ No commands found in category: {category}"
        
        from core.constants import HELP_CATEGORIES, EMOJIS
        
        category_title = HELP_CATEGORIES.get(category, category.title())
        help_text = f"**{category_title}**\n\n"
        
        for command in commands:
            command_info = self.commands[command]
            
            # Check if user has permission to see this command
            if command_info.get('admin_only', False) and not user_is_admin:
                continue
            
            description = command_info.get('description', 'No description')
            usage = command_info.get('usage', f'/{command}')
            
            help_text += f"• **{usage}**\n"
            help_text += f"  {description}\n\n"
        
        return help_text.strip()
    
    def _generate_general_help(self, user_is_admin: bool) -> str:
        """Generate general help text with categories"""
        from core.constants import HELP_CATEGORIES, BOT_NAME
        
        help_text = f"**🤖 {BOT_NAME} - Available Commands**\n\n"
        help_text += "Choose a category to see available commands:\n\n"
        
        for category, commands in self.categories.items():
            if not commands:
                continue
            
            # Count visible commands
            visible_count = 0
            for command in commands:
                command_info = self.commands[command]
                if not command_info.get('admin_only', False) or user_is_admin:
                    visible_count += 1
            
            if visible_count == 0:
                continue
            
            category_title = HELP_CATEGORIES.get(category, category.title())
            help_text += f"• **{category_title}** ({visible_count} commands)\n"
            help_text += f"  Use `/help {category}` to see commands\n\n"
        
        help_text += "\n💡 **Tip:** Use `/help <category>` to see specific commands"
        return help_text.strip()

# Global loader instance
command_loader: Optional[CommandLoader] = None

def get_command_loader() -> Optional[CommandLoader]:
    """Get the global command loader instance"""
    return command_loader

def init_command_loader(application: Application) -> CommandLoader:
    """Initialize the global command loader"""
    global command_loader
    command_loader = CommandLoader(application)
    return command_loader
