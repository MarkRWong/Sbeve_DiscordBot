import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Configuration (consider using environment variables or a .env file)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Set up the Discord bot with a command prefix.
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Event: Called when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')

# Event: starts the ec2 instance
@bot.command()
async def start(ctx):
    await ctx.send("start")

# Event: stops the ec2 instance
@bot.command()
async def stop(ctx):
    await ctx.send("stop")

# Event: checks the status of the ec2 instance
@bot.command()
async def status(ctx):
    await ctx.send("status")

# Run the bot with your token
bot.run(DISCORD_TOKEN)