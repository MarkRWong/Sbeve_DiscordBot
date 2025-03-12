from discord.ext import commands
from dotenv import load_dotenv
import discord
import os
import boto3
import paramiko
import asyncio

load_dotenv()

# Configuration (consider using environment variables or a .env file)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# AWS variables
AWS_INSTANCE_ID = os.getenv("AWS_INSTANCE_ID")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
AWS_USERNAME = os.getenv("AWS_USERNAME", "ec2-user")
AWS_SSH_PRIVATE_KEY_PATH = os.getenv("AWS_SSH_PRIVATE_KEY_PATH", "./MINECRAFT_SERVER_FILE_PATH.pem")

# Server Variables
SERVER_RAM = os.getenv("SERVER_RAM", "-Xmx3G -Xms3G")
MINECRAFT_SERVER_FILE_PATH = os.getenv("MINECRAFT_SERVER_FILE_PATH", "MINECRAFT_SERVER_FILE_PATH")

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

# Helper function to execute terminal commands to the instance
def sshCommand(client, command):
    try:
        stdin, stdout, stderr = client.exec_command(command)
        return stdout.readlines()
    except Exception as e:
        print(e)

# Helper function to get the instance status
def get_instance_state(instance_id):
    """Get the current state of an EC2 instance."""
    try:
        response = ec2.describe_instances(InstanceIds = [instance_id])
        state = response["Reservations"][0]["Instances"][0]["State"]["Name"]
        return state
    except Exception as e:
        return None
    
# Helper function to get the public IP
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

# Event: starts the ec2 instance and minecraft server
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
    # Opening minecraft server
    client.connect(publicIP, username=AWS_USERNAME, key_filename=AWS_SSH_PRIVATE_KEY_PATH)
    try:
        await ctx.send("Opening Minecraft Server...")
        start = f"cd {MINECRAFT_SERVER_FILE_PATH}; screen -dmS minecraft java {SERVER_RAM} -jar server.jar nogui"
        sshCommand(client, start)
        await ctx.send("Minecraft Server Running!")
    except Exception as e:
        print(e)
    client.close()

# Event: starts the ec2 instance ONLY
@bot.command()
async def istart(ctx):
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
        await ctx.send("Started instance")
    else:
        await ctx.send(f"⚠️ Instance is in '{state}' state. Unable to start.")
        return
    
# Event: save and quits the minecraft server and stops the ec2 instance
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
        publicIP = get_instance_publicIP(AWS_INSTANCE_ID)
        try:
            client.connect(publicIP, username=AWS_USERNAME, key_filename=AWS_SSH_PRIVATE_KEY_PATH)

            check = "screen -list"
            cmd = sshCommand(client, check)
            if cmd != "['No Sockets found in /run/screen/S-ec2-user.\n', '\r\n']":
                save = "cd {MINECRAFT_SERVER_FILE_PATH}; screen -S minecraft -X stuff 'save-all\n'"
                sshCommand(client, save)
                stop = "cd {MINECRAFT_SERVER_FILE_PATH}; screen -S minecraft -X stuff 'stop\n'"
                sshCommand(client, stop)
                print("minecraft server stopped")
        except Exception as e:
            print(e)

        await ctx.send("⏳ Stopping instance...")
        ec2.stop_instances(InstanceIds=[AWS_INSTANCE_ID])

        while state != "stopped":
            await asyncio.sleep(5)
            state = get_instance_state(AWS_INSTANCE_ID)

        await ctx.send("Instance stopped successfully.")
        client.close()
    else:
        await ctx.send(f"⚠️ Instance is in '{state}' state. Unable to stop.")

# Event: save and quits the minecraft server and stops the ec2 instance
@bot.command()
async def istop(ctx):
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

        while state != "stopped":
            await asyncio.sleep(5)
            state = get_instance_state(AWS_INSTANCE_ID)

        await ctx.send("Instance stopped successfully.")
        client.close()
    else:
        await ctx.send(f"⚠️ Instance is in '{state}' state. Unable to stop.")

# Event: writes admin commands to the server
@bot.command()
async def mc(ctx, msg):
    """Start the EC2 instance if it is not already running."""
    if not AWS_INSTANCE_ID:
        await ctx.send("❌ No instance ID configured.")
        return

    state = get_instance_state(AWS_INSTANCE_ID)

    if state == "running":
        publicIP = get_instance_publicIP(AWS_INSTANCE_ID)
        client.connect(publicIP, username=AWS_USERNAME, key_filename=AWS_SSH_PRIVATE_KEY_PATH)
        await ctx.send(f"Running Command: /{msg}")
        command = f"cd {MINECRAFT_SERVER_FILE_PATH}; screen -S minecraft -X stuff '{msg}\n'"
        sshCommand(client, command)
        client.close()
    else:
        await ctx.send(f"⚠️ Instance is in '{state}' state.")
        return

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

# sends ssh Command to the server
@bot.command()
async def cmd(ctx, msg):
    state = get_instance_state(AWS_INSTANCE_ID)

    if state == "running":
        publicIP = get_instance_publicIP(AWS_INSTANCE_ID)
        client.connect(publicIP, username=AWS_USERNAME, key_filename=AWS_SSH_PRIVATE_KEY_PATH)
        cmd = sshCommand(client, msg)
        await ctx.send(cmd)
        client.close()

# Run the bot with your token
bot.run(DISCORD_TOKEN)