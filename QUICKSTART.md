# ZyraX Bot - Quick Start Guide

## ✅ Import Error Fixed!

The import error has been resolved. The issue was in `utils/__init__.py` - it was importing `parse_time_string` from the wrong module.

## 🚀 Running the Bot

### 1. Prerequisites
Make sure you have:
- ✅ Python 3.11+ installed
- ✅ MongoDB running (local or cloud)
- ✅ Bot token from @BotFather

### 2. Setup (Already Done)
```bash
# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure .env File
Create a `.env` file in the project root with:

```env
# Required - Get from @BotFather
BOT_TOKEN=1234567890:ABCDEFGHijklmnopqrstuvwxyz123456789

# Required - MongoDB connection
MONGODB_URI=mongodb://localhost:27017/zyraX_bot

# Optional - For MTProto features (advanced)
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890

# Optional - Redis for caching
REDIS_URL=redis://localhost:6379/0

# Optional - Logging
LOG_LEVEL=INFO
DEBUG=False

# Optional - Error reporting
DEV_CHAT_ID=your_telegram_user_id
```

### 4. Start MongoDB
If using local MongoDB:
```bash
# Linux (systemd)
sudo systemctl start mongod

# macOS
brew services start mongodb-community

# Docker
docker run -d --name mongodb -p 27017:27017 mongo:latest
```

### 5. Run the Bot
```bash
python3.12 bot.py
```

Or use the startup script:
```bash
python3.12 start.py
```

## 📋 Checklist

Before running, ensure:
- [ ] Virtual environment is activated (you should see `(venv)` in your terminal)
- [ ] Dependencies are installed (`pip list` should show python-telegram-bot, etc.)
- [ ] `.env` file exists with at least `BOT_TOKEN` and `MONGODB_URI`
- [ ] MongoDB is running and accessible
- [ ] Bot token is valid (test it with @BotFather's `/token` command)

## 🔍 Testing the Bot

Once the bot starts successfully, test it:

1. **Add bot to a group**
   - Make the bot an admin with appropriate permissions

2. **Test basic commands**
   ```
   /start - Should show welcome message
   /help - Should show command categories
   /id - Should show chat and user IDs
   ```

3. **Test admin commands** (as admin in group)
   ```
   /ban @username - Test banning
   /unban @username - Test unbanning
   /promote @username - Test promotion
   ```

4. **Test moderation**
   ```
   /ban <user> spam - Ban with reason
   /tban <user> 1h - Temporary ban for 1 hour
   ```

## ⚠️ Common Issues & Solutions

### Import Errors
**Fixed!** The utils import issue has been resolved.

### "Bot Token Invalid"
- Check your `.env` file
- Ensure no spaces around `=` in `.env`
- Verify token with @BotFather

### "Database Connection Failed"
```bash
# Check MongoDB status
sudo systemctl status mongod  # Linux
brew services list | grep mongo  # macOS

# Test connection
mongosh  # Should connect to localhost:27017
```

### "Permission Denied" Errors
```bash
# Make sure bot is admin in the group
# Check bot has these permissions:
# - Delete messages
# - Ban users
# - Pin messages
# - Manage chat
```

### "Module Not Found"
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📊 Expected Bot Output

When bot starts successfully, you should see:
```
==================================================
🤖 Starting ZyraX Telegram Bot
==================================================
Bot Token: ********************your_token
Database URI: mongodb://localhost:27017/zyraX_bot
Debug Mode: False
Log Level: INFO
Successfully connected to MongoDB
Database indexes created successfully
Loaded X commands from Y modules
Bot initialized successfully
Starting ZyraX Bot...
Bot started successfully!
```

## 🎮 Next Steps

After successful startup:

1. **Add more handlers** - The system is ready to accept new command handlers
2. **Configure features** - Use `/settings` command to configure per-chat
3. **Test thoroughly** - Try all implemented commands
4. **Extend functionality** - Add new modules following the pattern in `handlers/`

## 🛠️ Development Mode

To run in development mode with auto-reload:
```bash
# Edit config.py to set DEBUG=True
# Or in .env:
DEBUG=True

# Then run
python3.12 bot.py
```

## 📝 Adding New Commands

To add a new command, create a file in the appropriate handler category:

```python
# handlers/misc/mycommand.py

COMMAND_INFO = {
    "commands": ["mycommand"],
    "description": "My custom command",
    "usage": "/mycommand <args>",
    "category": "misc",
    "admin_only": False,
    "group_only": False
}

async def handle(update, context):
    await update.message.reply_text("Hello from my command!")
```

The command will be automatically loaded and registered!

## 🆘 Getting Help

- **Logs**: Check `bot.log` file for detailed error messages
- **Database**: Use `mongosh` to inspect database state
- **Issues**: Report bugs on GitHub Issues
- **Documentation**: Check README.md and DEPLOYMENT.md

---

**You're all set! The bot should now run without errors. Happy coding! 🚀**
