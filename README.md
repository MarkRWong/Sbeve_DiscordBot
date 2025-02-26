# **Discord Bot for AWS EC2 Minecraft Server Management**

## **📌 Overview**  
This Discord bot allows you to start, stop, and check the status of a Minecraft server hosted on an AWS EC2 instance using simple bot commands.  

## **⚙️ Required Imports & Installations**  
Before running the bot, make sure you have the following Python packages installed:  

```bash
pip install discord.py python-dotenv
```

| Package          | Purpose |
|-----------------|---------|
| `discord.py`    | Discord bot library for interacting with Discord API |
| `python-dotenv` | Loads environment variables from a `.env` file for security |

## **📂 Setup Instructions**  

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/your-repo-name.git
   cd your-repo-name
   ```

2. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` File**  
   In the root directory, create a `.env` file and add your **Discord bot token**:  
   ```
   DISCORD_TOKEN=your-bot-token-here
   ```

4. **Run the Bot**  
   ```bash
   python main.py
   ```

## **🛠 Bot Commands**  
| Command | Description |
|---------|------------|
| `!start` | ... |
| `!stop` | ... |
| `!status` | ... |
