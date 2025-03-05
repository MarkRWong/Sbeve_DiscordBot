import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import boto3
import paramiko
import asyncio
import time

load_dotenv()

# Configuration (consider using environment variables or a .env file)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

AWS_INSTANCE_ID = os.getenv("AWS_INSTANCE_ID")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-west-1")

EC2_USERNAME = "ec2-user" # testing hard code remove later
PRIVATE_KEY_PATH = "./minecraft-server.pem" # testing hard code remove later

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

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

def sshCommand(client, command):
    try:
        stdin, stdout, stderr = client.exec_command(command)
        client.close()
        print(stdout.readlines())
    except Exception as e:
        print(e)

async def stoptMinecraftServer(ctx, client):
    save = "screen -S minecraft -X stuff 'save-all\n'"
    sshCommand(client, save)
    time.sleep(2)

    stop = "screen -S minecraft -X stuff 'stop\n'"
    sshCommand(client, stop)
    client.close()

def get_instance_state(instance_id):
    """Get the current state of an EC2 instance."""
    try:
        response = ec2.describe_instances(InstanceIds = [instance_id])
        state = response["Reservations"][0]["Instances"][0]["State"]["Name"]
        return state
    except Exception as e:
        return None
    
def get_instance_publicIP(instance_id):
    """Get the current state of an EC2 instance."""
    try:
        response = ec2.describe_instances(InstanceIds = [instance_id])
        public_ip = response["Reservations"][0]["Instances"][0]["PublicIpAddress"]
        return public_ip
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
        while state != "running":
            await asyncio.sleep(5)
            state = get_instance_state(AWS_INSTANCE_ID)
    else:
        await ctx.send(f"⚠️ Instance is in '{state}' state. Unable to start.")
        return
    
    publicIP = get_instance_publicIP(AWS_INSTANCE_ID)
    await ctx.send(f"IP: {publicIP}")

    # SSH connection
    await ctx.send("Connecting SSH...")
    client.connect(publicIP, username=EC2_USERNAME, key_filename=PRIVATE_KEY_PATH)
    await ctx.send("Connected SSH!")

    # Opening minecraft server
    await ctx.send("Opening Minecraft Server...")
    start = 'cd minecraft-server; java -Xmx1024M -Xms1024M -jar server.jar nogui'
    sshCommand(client, start)
    await ctx.send("Minecraft Server Running!")

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

        stoptMinecraftServer(client)

        while state != "stopped":
            await asyncio.sleep(5)
            state = get_instance_state(AWS_INSTANCE_ID)

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

# Event: gets the IP address of the ec2 instance
@bot.command()
async def ip(ctx):
    state = get_instance_state(AWS_INSTANCE_ID)
    if state == "running":
        publicIP = get_instance_publicIP(AWS_INSTANCE_ID)
        await ctx.send(f"IP: {publicIP}")
    elif state == "stopped":
        await ctx.send("No IP Instance stopped.")
    else:
        await ctx.send(f"⚠️ Instance is in '{state}' state.")

@bot.command()
async def ssh(ctx, arg):
    stdin, stdout, stderr = client.exec_command(arg)
    print(stdout)
    line = stdout.readlines()
    print(line)
    await ctx.send(line)

@bot.command()
async def sshstatus(ctx):
    try:
        if client.get_transport() is not None:
            if client.get_transport().is_active():
                print("Connection is still alive.")
                await ctx.send("Connection is still alive.")
            else:
                print("Connection is not active.")
                await ctx.send("Connection is not active.")
    except Exception as e:
        print("Error")

@bot.command()
async def sshclose(ctx):
    client.close()

# Run the bot with your token
bot.run(DISCORD_TOKEN)