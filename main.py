import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import boto3

load_dotenv()

# Configuration (consider using environment variables or a .env file)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

AWS_INSTANCE_ID = os.getenv("AWS_INSTANCE_ID")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-west-1")

ec2 = boto3.client(
    "ec2",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

# Set up the Discord bot with a command prefix.
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def get_instance_state(instance_id):
    """Get the current state of an EC2 instance."""
    try:
        response = ec2.describe_instances(InstanceIds = [instance_id])
        state = response["Reservations"][0]["Instances"][0]["State"]["Name"]
        return state
    except Exception as e:
        return None

# Event: Called when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')

# Event: starts the ec2 instance
@bot.command()
async def start(ctx):
    """Start the EC2 instance if it is not already running."""
    if not AWS_INSTANCE_ID:
        await ctx.send("❌ No instance ID configured.")
        return

    state = get_instance_state(AWS_INSTANCE_ID)

    if state == "running":
        await ctx.send("Instance is already running.")
    elif state == "stopped":
        await ctx.send("⏳ Starting instance...")
        ec2.start_instances(InstanceIds=[AWS_INSTANCE_ID])
        await ctx.send("Instance started successfully.")
    else:
        await ctx.send(f"⚠️ Instance is in '{state}' state. Unable to start.")

# Event: stops the ec2 instance
@bot.command()
async def stop(ctx):
    """Stop the EC2 instance if it is running."""
    if not AWS_INSTANCE_ID:
        await ctx.send("❌ No instance ID configured.")
        return

    state = get_instance_state(AWS_INSTANCE_ID)

    if state == "stopped":
        await ctx.send("Instance is already stopped.")
    elif state == "running":
        await ctx.send("⏳ Stopping instance...")
        ec2.stop_instances(InstanceIds=[AWS_INSTANCE_ID])
        await ctx.send("Instance stopped successfully.")
    else:
        await ctx.send(f"⚠️ Instance is in '{state}' state. Unable to stop.")

# Event: checks the status of the ec2 instance
@bot.command()
async def status(ctx):
    if not AWS_INSTANCE_ID:
        await ctx.send("No instance ID configured.")
        return
    
    state = get_instance_state(AWS_INSTANCE_ID)
    if state == "running":
        await ctx.send("Instance running.")
    elif state == "stopped":
        await ctx.send("Instance stopped.")
    else:
        await ctx.send(f"⚠️ Instance is in '{state}' state.")

# Run the bot with your token
bot.run(DISCORD_TOKEN)