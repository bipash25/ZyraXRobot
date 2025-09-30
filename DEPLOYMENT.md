# ZyraX Bot Deployment Guide

This guide will help you deploy ZyraX Bot in different environments.

## 🚀 Quick Start

### Option 1: Use the Startup Script

**Windows:**
```bash
start.bat
```

**Linux/macOS:**
```bash
python start.py
```

### Option 2: Manual Setup

1. **Install Python 3.11+**
   - Download from [python.org](https://python.org)
   - Ensure pip is installed

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Start the Bot**
   ```bash
   python bot.py
   ```

## 🔧 Configuration

### Required Environment Variables

Create a `.env` file in the project root:

```env
# Bot Configuration
BOT_TOKEN=1234567890:ABCDEFGHijklmnopqrstuvwxyz123456789
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/zyraX_bot

# Optional Configuration
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
DEBUG=False
DEV_CHAT_ID=123456789
```

### Getting Bot Token

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Create a new bot with `/newbot`
3. Follow instructions to get your bot token
4. Add the token to your `.env` file

### Getting API ID and Hash (Optional)

1. Go to [my.telegram.org](https://my.telegram.org)
2. Login with your phone number
3. Go to "API Development Tools"
4. Create a new application
5. Copy API ID and API Hash to your `.env` file

## 📦 Database Setup

### MongoDB

#### Local MongoDB
1. Install MongoDB Community Edition
2. Start MongoDB service
3. Use default connection: `mongodb://localhost:27017/zyraX_bot`

#### MongoDB Atlas (Cloud)
1. Create account at [mongodb.com](https://mongodb.com)
2. Create a new cluster
3. Get connection string
4. Add to `.env` as `MONGODB_URI`

#### Docker MongoDB
```bash
docker run -d --name mongodb -p 27017:27017 mongo:latest
```

### Redis (Optional)

#### Local Redis
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Windows
# Download from https://redis.io/download
```

#### Docker Redis
```bash
docker run -d --name redis -p 6379:6379 redis:alpine
```

## 🖥️ Production Deployment

### Option 1: VPS/Server Deployment

#### System Requirements
- Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- Python 3.11+
- 1GB RAM minimum
- 10GB storage minimum

#### Installation Steps

1. **Update System**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Python 3.11**
   ```bash
   sudo apt install software-properties-common -y
   sudo add-apt-repository ppa:deadsnakes/ppa -y
   sudo apt update
   sudo apt install python3.11 python3.11-venv python3.11-dev -y
   ```

3. **Install MongoDB**
   ```bash
   wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
   echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
   sudo apt update
   sudo apt install -y mongodb-org
   sudo systemctl start mongod
   sudo systemctl enable mongod
   ```

4. **Setup Bot**
   ```bash
   git clone https://github.com/yourusername/ZyraX-Bot.git
   cd ZyraX-Bot
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp env.example .env
   # Edit .env with your configuration
   nano .env
   ```

5. **Create Systemd Service**
   ```bash
   sudo nano /etc/systemd/system/zyrabot.service
   ```

   Add this content:
   ```ini
   [Unit]
   Description=ZyraX Telegram Bot
   After=network.target mongod.service
   Wants=mongod.service

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/ZyraX-Bot
   Environment=PATH=/home/ubuntu/ZyraX-Bot/venv/bin
   ExecStart=/home/ubuntu/ZyraX-Bot/venv/bin/python bot.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

6. **Start Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start zyrabot
   sudo systemctl enable zyrabot
   sudo systemctl status zyrabot
   ```

### Option 2: Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  bot:
    build: .
    restart: unless-stopped
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - MONGODB_URI=mongodb://mongodb:27017/zyraX_bot
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - mongodb
      - redis
    volumes:
      - ./logs:/app/logs

  mongodb:
    image: mongo:6
    restart: unless-stopped
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"

  redis:
    image: redis:alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

volumes:
  mongodb_data:
  redis_data:
```

#### Deploy with Docker
```bash
# Create .env file with your configuration
cp env.example .env
nano .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f bot
```

### Option 3: Heroku Deployment

#### Prepare for Heroku

1. **Create files:**

   `Procfile`:
   ```
   web: python bot.py
   ```

   `runtime.txt`:
   ```
   python-3.11.7
   ```

2. **Setup Heroku**
   ```bash
   # Install Heroku CLI
   # Create Heroku app
   heroku create your-bot-name
   
   # Add MongoDB addon
   heroku addons:create mongolab:sandbox
   
   # Set environment variables
   heroku config:set BOT_TOKEN=your_bot_token
   heroku config:set API_ID=your_api_id
   heroku config:set API_HASH=your_api_hash
   
   # Deploy
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

## 🔍 Monitoring and Maintenance

### Logs

#### Check Logs (Systemd)
```bash
sudo journalctl -u zyrabot -f
```

#### Check Logs (Docker)
```bash
docker-compose logs -f bot
```

### Database Maintenance

#### Backup MongoDB
```bash
mongodump --db zyraX_bot --out backup/
```

#### Restore MongoDB
```bash
mongorestore --db zyraX_bot backup/zyraX_bot/
```

### Bot Updates

#### Manual Update
```bash
cd ZyraX-Bot
git pull origin main
pip install -r requirements.txt
sudo systemctl restart zyrabot
```

#### Automated Updates (Cron)
```bash
# Add to crontab: crontab -e
0 2 * * * cd /home/ubuntu/ZyraX-Bot && git pull && pip install -r requirements.txt && sudo systemctl restart zyrabot
```

## 🛠️ Troubleshooting

### Common Issues

#### "Bot Token Invalid"
- Check your bot token in `.env`
- Ensure no extra spaces or characters
- Verify token with [@BotFather](https://t.me/BotFather)

#### "Database Connection Failed"
- Check MongoDB is running: `sudo systemctl status mongod`
- Verify connection string in `.env`
- Check network/firewall settings

#### "Permission Denied"
- Ensure bot is admin in target groups
- Check file permissions: `chmod +x start.py`
- Verify user permissions for service

#### "Module Not Found"
- Reinstall requirements: `pip install -r requirements.txt`
- Check Python version: `python --version`
- Verify virtual environment is activated

### Performance Issues

#### High Memory Usage
- Monitor with: `htop` or `systemctl status zyrabot`
- Consider adding swap file
- Upgrade server resources

#### Slow Response
- Check database performance
- Monitor network latency
- Consider Redis caching

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ZyraX-Bot/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/ZyraX-Bot/wiki)
- **Telegram**: [@ZyraXSupport](https://t.me/ZyraXSupport)

---

**Happy Deploying! 🚀**
