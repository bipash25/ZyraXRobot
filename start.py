#!/usr/bin/env python3
"""
Quick start script for ZyraX Bot
"""
import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    return True

def check_requirements():
    """Check if requirements are installed"""
    try:
        import telegram
        import pyrogram
        import motor
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Installing requirements...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Requirements installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install requirements")
            return False

def check_config():
    """Check if configuration exists"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please copy env.example to .env and configure your settings:")
        print("  cp env.example .env")
        print("  # Edit .env with your bot token and database details")
        return False
    
    # Check if BOT_TOKEN is set
    from config import config
    if not config.BOT_TOKEN:
        print("❌ BOT_TOKEN not configured!")
        print("Please add your bot token to the .env file")
        return False
    
    print("✅ Configuration found")
    return True

def main():
    """Main startup function"""
    print("🤖 ZyraX Bot Startup Script")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check requirements
    if not check_requirements():
        return False
    
    # Check configuration
    if not check_config():
        return False
    
    print("\n🚀 Starting ZyraX Bot...")
    print("=" * 40)
    
    # Start the bot
    try:
        import bot
        return True
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
        return True
    except Exception as e:
        print(f"\n❌ Error starting bot: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
