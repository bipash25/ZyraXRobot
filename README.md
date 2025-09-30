# ZyraX Telegram Bot (@ZyraXRobot)

A comprehensive, feature-rich Telegram bot for group management, moderation, and community engagement.

## 🚀 Features

### 🛡️ Moderation & Security
- **Advanced Moderation** - Ban, mute, kick, warn users with customizable actions
- **Anti-Flood Protection** - Configurable flood detection and automatic actions
- **Anti-Raid System** - Protect against mass join attacks
- **Captcha Verification** - Multiple captcha types (button, math, text, image)
- **Content Filtering** - Block unwanted words, links, and media
- **Approval System** - Whitelist trusted users to bypass restrictions

### 📝 Content Management
- **Smart Filters** - Auto-respond to keywords with text, media, or buttons
- **Notes System** - Save and retrieve information with hashtag triggers
- **Welcome/Goodbye Messages** - Customizable greetings with variables
- **Rules Management** - Set and display chat rules
- **Pin Management** - Advanced pin controls with anti-channel pin

### 🔒 Chat Security
- **Locks System** - Lock specific content types (stickers, urls, forwarding, etc.)
- **Federation System** - Connect multiple chats with shared ban lists
- **Blocklists** - Advanced word filtering with wildcards
- **Admin Cache** - Efficient permission checking with caching

### 🎮 Community Features
- **Leveling System** - XP and level progression for active members
- **Economy System** - Virtual currency with daily rewards
- **Giveaways** - Host and manage community giveaways
- **Fun Commands** - Entertainment and interactive features
- **Statistics** - Track chat activity and user engagement

### ⚙️ Management Tools
- **Command Disabling** - Enable/disable specific commands per chat
- **Connection System** - Manage multiple chats from one location
- **Import/Export** - Backup and restore chat settings
- **Logging** - Comprehensive action logging to channels
- **Multi-Language** - Support for multiple languages

## 🛠️ Technology Stack

- **Language**: Python 3.11+
- **Framework**: python-telegram-bot (PTB) v20+ & Pyrogram (MTProto)
- **Database**: MongoDB with Motor (async)
- **Scheduler**: APScheduler for timed actions
- **Cache**: Redis (optional)
- **Image Processing**: Pillow for captcha generation

## 📦 Installation

### Prerequisites
- Python 3.11 or higher
- MongoDB (local or cloud)
- Redis (optional, for caching)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ZyraX-Bot.git
   cd ZyraX-Bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your bot token and database details
   ```

4. **Set up environment variables**
   ```env
   BOT_TOKEN=your_bot_token_here
   API_ID=your_api_id_here
   API_HASH=your_api_hash_here
   MONGODB_URI=mongodb://localhost:27017/zyraX_bot
   ```

5. **Run the bot**
   ```bash
   python bot.py
   ```

## 🔧 Configuration

### Required Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Telegram Bot Token from @BotFather | Yes |
| `MONGODB_URI` | MongoDB connection string | Yes |
| `API_ID` | Telegram API ID (for MTProto features) | Optional |
| `API_HASH` | Telegram API Hash (for MTProto features) | Optional |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection URL | None |
| `LOG_LEVEL` | Logging level | INFO |
| `DEBUG` | Enable debug mode | False |
| `DEV_CHAT_ID` | Chat ID for error reporting | None |

## 📚 Usage

### Basic Commands

#### Admin Commands
- `/promote <user>` - Promote user to admin
- `/demote <user>` - Demote admin to user
- `/ban <user> [reason]` - Ban user from chat
- `/unban <user>` - Unban user
- `/mute <user> [time]` - Mute user
- `/kick <user>` - Kick user

#### Moderation
- `/warn <user> [reason]` - Warn user
- `/purge [count]` - Delete messages
- `/lock <type>` - Lock chat features
- `/unlock <type>` - Unlock chat features

#### Content Management
- `/filter <trigger> <response>` - Add auto-response
- `/note <name> <content>` - Save note
- `/rules` - Show chat rules
- `/welcome <message>` - Set welcome message

#### Information
- `/help [category]` - Show commands
- `/id` - Get chat/user IDs
- `/info [user]` - Get user information

### Advanced Features

#### Flood Protection
```
/setflood 5          # Set flood limit to 5 messages
/floodmode ban       # Ban on flood detection
/clearflood on       # Clear user messages on flood
```

#### Captcha System
```
/captcha on          # Enable captcha for new members
/captchamode button  # Set captcha type (button/math/text)
/captchakick 300     # Auto-kick after 5 minutes
```

#### Federation Management
```
/newfed MyFed        # Create federation
/joinfed <fed_id>    # Join federation
/fban <user>         # Federation ban
```

## 🏗️ Architecture

### Project Structure
```
ZyraX-Bot/
├── bot.py                    # Main entry point
├── config.py                 # Configuration management
├── requirements.txt          # Dependencies
├── core/                     # Core components
│   ├── database.py           # Database operations
│   ├── constants.py          # Constants and enums
│   ├── helpers.py            # Utility functions
│   ├── decorators.py         # Permission decorators
│   └── bot_instance.py       # Bot initialization
├── handlers/                 # Command handlers
│   ├── loader.py             # Dynamic command loader
│   ├── admin/                # Admin commands
│   ├── moderation/           # Moderation commands
│   ├── misc/                 # Miscellaneous commands
│   └── ...                   # Other categories
├── utils/                    # Utility modules
│   ├── message_parser.py     # Message parsing
│   ├── user_resolver.py      # User resolution
│   ├── time_parser.py        # Time parsing
│   └── captcha_gen.py        # Captcha generation
├── models/                   # Database models
├── middleware/               # Middleware components
└── locales/                  # Translation files
```

### Dynamic Command Loading

Commands are automatically loaded from handler modules that export `COMMAND_INFO`:

```python
COMMAND_INFO = {
    "commands": ["ban", "unban"],
    "description": "Ban and unban users",
    "usage": "/ban <user> [reason]",
    "category": "moderation",
    "permissions": ["can_restrict_members"],
    "admin_only": True,
    "group_only": True
}

async def handle(update, context):
    # Command implementation
    pass
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Report bugs and request features on GitHub Issues
- **Telegram**: Join our support group [@ZyraXSupport](https://t.me/ZyraXSupport)
- **Documentation**: Check the [Wiki](https://github.com/yourusername/ZyraX-Bot/wiki) for detailed guides

## 🙏 Acknowledgments

- [python-telegram-bot](https://python-telegram-bot.org/) - Telegram Bot API wrapper
- [Pyrogram](https://pyrogram.org/) - MTProto API framework
- [MongoDB](https://www.mongodb.com/) - Database
- [APScheduler](https://apscheduler.readthedocs.io/) - Task scheduling

---

**Made with ❤️ for the Telegram community**
