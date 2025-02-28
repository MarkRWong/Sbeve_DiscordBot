# **Discord Bot for AWS EC2 Instance Management**

## **📌 Overview**  
This Discord bot allows you to manage an AWS EC2 instance by starting, stopping, and checking the status of the instance using simple bot commands. It is useful for automating server management tasks, especially for Minecraft or other server hosting.

## **⚙️ Required Imports & Installations**  
Before running the bot, make sure you have the following Python packages installed:

```bash
pip install discord.py python-dotenv boto3

```

| Package          | Purpose |
|-----------------|---------|
| `discord.py`    | Discord bot library for interacting with Discord API |
| `python-dotenv` | Loads environment variables from a `.env` file for security |
| `boto3`         | AWS SDK for Python to interact with AWS services |

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

3. **Create AWS Secret Key**<br />
   3.1. *Create a policy under:*
      IAM > Policies > Create Policy > JSON<br />
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

      Step 1: Create a name<br />
      Step 2: Add user to a group<br />
      Check "Use a permissions boundary to control the maximum permissions"<br />
      Search for the newly created policy from 3.1.<br />
      Create the user.<br />
      
   3.3. *Create access key:*
      Click on your newly created user, under Access Key 1, click on "Create access key", and select "Application running on an AWS compute service". Copy your access key and secret key.

4. **Create a `.env` File**  
   In the root directory, create a `.env` file and add your **Discord bot token**:  
   ```
   DISCORD_TOKEN=your-discord-bot-token
   
   AWS_INSTANCE_ID=your-aws-instance-id
   AWS_ACCESS_KEY_ID=your-aws-access-key-id
   AWS_REGION=your-aws-region
   AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
   ```

5. **Run the Bot**  
   ```bash
   python main.py
   ```

## **🛠 Bot Commands**  
| Command | Description |
|---------|------------|
| `!start` | Starts the AWS EC2 instance if it is not already running. |
| `!stop` | Stops the AWS EC2 instance if it is running. |
| `!status` | Checks the current status of the AWS EC2 instance. |
