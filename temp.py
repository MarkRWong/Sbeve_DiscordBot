import os
import asyncio
import discord
from discord.ext import commands
import boto3
from mcrcon import MCRcon  # pip install mcrcon

# Configuration (consider using environment variables or a .env file)
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
INSTANCE_ID = os.environ.get("INSTANCE_ID", "i-xxxxxxxxxxxx")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "your-discord-bot-token")
RCON_PASSWORD = os.environ.get("RCON_PASSWORD", "your_rcon_password")
RCON_PORT = int(os.environ.get("RCON_PORT", "25575"))
MINECRAFT_WORLD_DIR = os.environ.get("MINECRAFT_WORLD_DIR", "/home/ubuntu/minecraft/world")
S3_BUCKET = os.environ.get("S3_BUCKET", "your-backup-bucket")
S3_BACKUP_PREFIX = os.environ.get("S3_BACKUP_PREFIX", "backup")

# Initialize AWS clients
ec2 = boto3.client("ec2", region_name=AWS_REGION)
ssm = boto3.client("ssm", region_name=AWS_REGION)

# Set up the Discord bot with a command prefix.
bot = commands.Bot(command_prefix="!")

@bot.command()
async def start(ctx):
    """Starts the EC2 instance hosting the Minecraft server."""
    # Check if the instance is already running.
    response = ec2.describe_instances(InstanceIds=[INSTANCE_ID])
    instance = response["Reservations"][0]["Instances"][0]
    state = instance["State"]["Name"]

    if state == "running":
        await ctx.send("The server is already running.")
        return

    await ctx.send("Starting the server...")
    try:
        ec2.start_instances(InstanceIds=[INSTANCE_ID])
    except Exception as e:
        await ctx.send(f"Error starting the instance: {e}")
        return

    # Wait until the instance reaches the running state.
    while True:
        response = ec2.describe_instances(InstanceIds=[INSTANCE_ID])
        instance = response["Reservations"][0]["Instances"][0]
        state = instance["State"]["Name"]
        if state == "running":
            break
        await asyncio.sleep(5)

    await ctx.send("Server started! It may take a minute for Minecraft to be fully ready.")

@bot.command()
async def stop(ctx):
    """Saves the server state, backs up world data, and stops the EC2 instance."""
    # Check if the instance is running.
    response = ec2.describe_instances(InstanceIds=[INSTANCE_ID])
    instance = response["Reservations"][0]["Instances"][0]
    state = instance["State"]["Name"]

    if state != "running":
        await ctx.send("The server is not running.")
        return

    public_ip = instance.get("PublicIpAddress")
    if not public_ip:
        await ctx.send("Could not retrieve the server's public IP.")
        return

    await ctx.send("Issuing in-game save command...")

    # Connect to the Minecraft server via RCON to send the "save-all" command.
    try:
        with MCRcon(public_ip, RCON_PASSWORD, port=RCON_PORT) as mcr:
            mcr.command("save-all")
    except Exception as e:
        await ctx.send(f"Error sending save command via RCON: {e}")
        return

    # Allow time for the server to flush world data to disk.
    await asyncio.sleep(5)

    await ctx.send("Backing up world data...")
    # Define shell commands to compress the Minecraft world folder and upload to S3.
    backup_commands = [
        # Compress the world folder into a tar.gz archive with a timestamp.
        f"tar -czf /tmp/world_backup.tar.gz {MINECRAFT_WORLD_DIR}",
        # Upload the backup to S3.
        f"aws s3 cp /tmp/world_backup.tar.gz s3://{S3_BUCKET}/{S3_BACKUP_PREFIX}/world_backup_$(date +%Y%m%d%H%M%S).tar.gz"
    ]

    try:
        ssm_response = ssm.send_command(
            InstanceIds=[INSTANCE_ID],
            DocumentName="AWS-RunShellScript",
            Parameters={"commands": backup_commands},
        )
        command_id = ssm_response["Command"]["CommandId"]

        # Optionally wait for the backup command to finish.
        while True:
            invocation = ssm.get_command_invocation(
                CommandId=command_id,
                InstanceId=INSTANCE_ID,
            )
            if invocation["Status"] in ["Success", "Failed", "Cancelled", "TimedOut"]:
                break
            await asyncio.sleep(5)
    except Exception as e:
        await ctx.send(f"Error during backup: {e}")
        return

    await ctx.send("Backup complete. Shutting down the server...")
    try:
        ec2.stop_instances(InstanceIds=[INSTANCE_ID])
    except Exception as e:
        await ctx.send(f"Error stopping the instance: {e}")
        return

    await ctx.send("Server is shutting down.")

bot.run(DISCORD_TOKEN)
