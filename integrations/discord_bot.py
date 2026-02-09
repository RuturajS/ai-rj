
import discord
import config
import logging
from remote_handler import handle_remote_command

# Suppress debug logs
logging.getLogger('discord').setLevel(logging.WARNING)

class AssistantBot(discord.Client):
    async def on_ready(self):
        print(f'[Discord] Logged in as {self.user} (ID: {self.user.id})')

    async def on_message(self, message):
        # Ignore self
        if message.author == self.user:
            return

        # Security Check: Only allow commands from configured channel
        allowed_channel = config.REMOTE_CONFIG["discord_channel_id"]
        if allowed_channel and message.channel.id != allowed_channel:
            return

        print(f"[Discord] Command from {message.author}: {message.content}")
        
        # Execute Command
        response = handle_remote_command(message.content)
        
        # Reply
        await message.channel.send(f"🤖 **RJ**: {response}")

def run_discord():
    token = config.REMOTE_CONFIG["discord_token"]
    if not token:
        print("[Discord] No token found. Skipping Discord bot.")
        return

    intents = discord.Intents.default()
    intents.message_content = True
    client = AssistantBot(intents=intents)
    try:
        client.run(token)
    except Exception as e:
        print(f"[Discord] Connection Failed: {e}")
