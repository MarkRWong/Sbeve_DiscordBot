# **Discord Bot for AWS EC2 Instance Management**

## **📌 Overview**  
This Discord bot allows you to manage an AWS EC2 instance by starting, stopping, and checking the status of the instance using simple bot commands. It is useful for automating server management tasks, especially for Minecraft or other server hosting.

## **⚙️ Required Imports & Installations**  
Before running the bot, make sure you have the following Python packages installed:

```bash
pip install discord.py python-dotenv boto3 paramiko
```

| Package          | Purpose |
|-----------------|---------|
| `discord.py`    | Discord bot library for interacting with Discord API |
| `python-dotenv` | Loads environment variables from a `.env` file for security |
| `boto3`         | AWS SDK for Python to interact with AWS services |
| `paramiko`      | SSH client for executing commands on the EC2 instance |

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
   
3. **Create AWS Secret Key**  
   3.1. *Create a policy under:*  
      IAM > Policies > Create Policy > JSON  
      Replace the `{}` with the following:
      Note you can replace the `{}` with `*` <-- select all
      ```json
      {
         "Version": "2012-10-17",
         "Statement": [
            {
               "Sid": "VisualEditor0",
               "Effect": "Allow",
               "Action": [
                  "ec2:StartInstances",
                  "ec2:StopInstances"
               ],
               "Resource": "arn:aws:ec2:Region:account ID:instance/instance ID"
            },
            {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "ec2:DescribeInstances",
            "Resource": "*"
            }
         ]
      }
      ```
   
   3.2. *Create a user:*  
      IAM > Users > Create user  

      Step 1: Create a name  
      Step 2: Add user to a group  
      Check "Use a permissions boundary to control the maximum permissions"  
      Search for the newly created policy from 3.1.  
      Create the user.  
   
   3.3. *Create access key:*  
      Click on your newly created user, under Access Key 1, click on "Create access key", and select "Application running on an AWS compute service". Copy your access key and secret key.

4. **Create a `.env` File**  
   In the root directory, create a `.env` file and add your **Discord bot token** and AWS credentials:  
   ```
   DISCORD_TOKEN=your-discord-bot-token

   AWS_INSTANCE_ID=your-aws-instance-id
   AWS_ACCESS_KEY_ID=your-aws-access-key-id
   AWS_REGION=your-aws-region
   AWS_USERNAME=aws-user
   AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
   PRIVATE_KEY_PATH=file-path-to-.pem

   SERVER_RAM=-Xmx{RAM}G -Xms{RAM}G # Has to be in this format replace {RAM} with number of ram you want
   MINECRAFT_SERVER_FILE_PATH=minecraft-server
   ```

5. **Run the Bot**  
   ```bash
   python main.py
   ```

## **🛠 Bot Commands**  
| Command | Description |
|---------|------------|
| `!start` | Starts the AWS EC2 instance and launches the Minecraft server. |
| `!istart` | Starts only the AWS EC2 instance. |
| `!stop` | Saves, stops the Minecraft server, and shuts down the AWS EC2 instance. |
| `!istop` | Stops only the AWS EC2 instance. |
| `!status` | Checks the current status of the AWS EC2 instance. |
| `!ip` | Retrieves the public IP of the EC2 instance. |
| `!mc "command"` | Sends a command to the running Minecraft server. |
| `!cmd "command"` | Executes an SSH command on the EC2 instance. |

Now your bot is ready to manage your AWS EC2 instance and Minecraft server! 🚀
