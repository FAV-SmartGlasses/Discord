import threading
from flask import Flask, request, jsonify
import discord
from discord.ext import commands
import asyncio
import requests
import json
import os
import dotenv

dotenv.load_dotenv(os.path.abspath(".env"))

# Initialize message store
message_log = []
webhook_store = {}
if os.path.exists(os.path.abspath("webhooks.json")):
    with open("webhooks.json") as f:
        webhook_store = json.load(f)
        print(webhook_store)

# Flask setup
app = Flask(__name__)

# Discord bot setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Endpoint to send webhook message
@app.route('/messages/send', methods=['POST'])
def send_webhook():
    data = request.json
    message = data.get('message')
    username = data.get('name')
    avatar_url = data.get('pfp')
    webhook_url = data.get('webhook')

    if not all([message, username, webhook_url]):
        return 'Missing fields', 400

    payload = {
        "content": message,
        "username": username,
        "avatar_url": avatar_url
    }

    response = requests.post(webhook_url, json=payload)
    if response.status_code in [200, 204]:
        return 'Message sent!', 200
    else:
        return 'Failed to send', 500

# Endpoint to get all collected messages
@app.route('/messages/get', methods=['GET'])
def get_messages():
    return jsonify(message_log)

# Endpoint to send private DM
@app.route('/messages/send_private', methods=['POST'])
def send_private():
    data = request.json
    message = data.get('message')
    username = data.get('name')
    tag = data.get('tag')

    if not all([message, username, tag]):
        return 'Missing fields', 400

    # Find user by tag and send DM in the bot loop
    async def send_dm():
        for guild in bot.guilds:
            member = discord.utils.find(lambda m: m.name == tag, guild.members)
            if member:
                try:
                    await member.send(f"**[{username}]:** {message}")
                    return
                except:
                    continue

    asyncio.run_coroutine_threadsafe(send_dm(), bot.loop)
    return 'Attempted to send DM', 200

@app.route('/webhooks', methods=['GET'])
def get_webhooks():
    if os.path.exists('webhooks.json'):
        with open('webhooks.json', 'r') as f:
            return jsonify(json.load(f))
    else:
        return jsonify({})

@app.route('/tag', methods=['POST'])
def get_user_tags():
    data = request.json
    username = data.get('username')
    if not username:
        return 'Missing username', 400

    matches = []
    for guild in bot.guilds:
        for member in guild.members:
            if member.name == username or member.display_name == username:
                matches.append({
                    'username': member.name,
                    'id': member.id,
                    'guild': guild.name
                })
    return jsonify(matches)

# Capture messages from all servers the bot is in
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    message_log.append({
        'author': f"{message.author.name}#{message.author.discriminator}",
        'content': message.content,
        'channel': str(message.channel),
        'timestamp': str(message.created_at)
    })

    await bot.process_commands(message)

@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        try:
            webhook = await channel.create_webhook(name='AutoWebhook')
            webhook_store[channel.name] = webhook.url
        except Exception as e:
            print(f"Failed to create webhook in {channel.name}: {e}")
    # Save to JSON file
    with open('webhooks.json', 'w') as f:
        json.dump(webhook_store, f)

# Run Flask in separate thread
def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Start everything
if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    bot.run(os.getenv("BOT_TOKEN"))
