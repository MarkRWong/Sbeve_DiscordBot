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

SERVER_RAM = "-Xmx3G -Xms3G" # testing hard Code Remove later
EC2_USERNAME = "ec2-user" # testing hard code remove later
PRIVATE_KEY_PATH = "./minecraft-server.pem" # testing hard code remove later

ec2 = boto3.client(
    "ec2",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

def sshCommand(client, command):
    try:
        stdin, stdout, stderr = client.exec_command(command)
        print(stdout.readlines())
    except Exception as e:
        print(e)

def get_instance_publicIP(instance_id):
    """Get the current state of an EC2 instance."""
    try:
        response = ec2.describe_instances(InstanceIds = [instance_id])
        public_ip = response["Reservations"][0]["Instances"][0]["PublicIpAddress"]
        return public_ip
    except Exception as e:
        return None

def start_server(client, publicIP):
    client.connect(publicIP, username=EC2_USERNAME, key_filename=PRIVATE_KEY_PATH)
    print("starting minecraft server")
    startCommand = f"cd minecraft-server; screen -dmS minecraft java {SERVER_RAM} -jar server.jar nogui"
    sshCommand(client, startCommand)
    print("minecraft server started")
    client.close()

def op(client, publicIP):
    client.connect(publicIP, username=EC2_USERNAME, key_filename=PRIVATE_KEY_PATH)
    print("op")
    startCommand = f"cd minecraft-server; screen -S minecraft -X stuff 'op leotheclasher\n'"
    sshCommand(client, startCommand)

def say(client, publicIP):
    client.connect(publicIP, username=EC2_USERNAME, key_filename=PRIVATE_KEY_PATH)
    print("say")
    startCommand = f"cd minecraft-server; screen -S minecraft -X stuff 'say hello world\n'"
    sshCommand(client, startCommand)

def stop_server(client, publicIP):
    client.connect(publicIP, username=EC2_USERNAME, key_filename=PRIVATE_KEY_PATH)
    print("saving minecraft server")
    save = "cd minecraft-server; screen -S minecraft -X stuff 'save-all\n'"
    sshCommand(client, save)
    print("minecraft server saved")

    time.sleep(2)
    
    print("stopping minecraft server")
    stop = "cd minecraft-server; screen -S minecraft -X stuff 'stop\n'"
    sshCommand(client, stop)
    print("minecraft server stopped")
    client.close()

def get_status(client):
    print("IDK yet")

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    publicIP = get_instance_publicIP(AWS_INSTANCE_ID)
    print(f"IP: {publicIP}")

    while True:
        command = input("Enter command (start/stop/status/exit): ").strip().lower()
        if command == "start":
            start_server(client, publicIP)
        if command == "echo":
            sshCommand(client, 'echo "This is a est"')
        elif command == "stop":
            stop_server(client, publicIP)
        elif command == "status":
            get_status(client)
        elif command == "op":
            op(client, publicIP)
        elif command == "say":
            say(client, publicIP)
        elif command == "exit":
            break
        else:
            print("Invalid command.")

main()