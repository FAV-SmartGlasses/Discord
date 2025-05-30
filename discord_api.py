import asyncio
import json
import os
import threading

import discord
import dotenv
import requests
from discord import ThreadMember
from discord.ext import commands
from flask import Flask, request, jsonify

dotenv.load_dotenv(os.path.abspath(".env"))

LLM_URL = os.getenv("LLM_SERVER")

ai_messages : dict[str, list[dict[str, str]]] = {}
if os.path.exists(os.path.abspath("ai_messages.json")):
    with open("ai_messages.json") as f:
        ai_messages = json.load(f)

# Initialize message store
message_log : dict[str, dict[str, list]] = {}
if os.path.exists(os.path.abspath("messages.json")):
    with open("messages.json") as f:
        message_log = json.load(f)

webhook_store = {}
if os.path.exists(os.path.abspath("webhooks.json")):
    with open("webhooks.json") as f:
        webhook_store = json.load(f)

channels = {}
if os.path.exists(os.path.abspath("channels.json")):
    with open("channels.json") as f:
        channels = json.load(f)

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
    auth = request.args.get("auth")

    if auth != os.getenv("AUTH_KEY"):
        return "Invalid auth key", 401

    if not all([message, username, webhook_url]):
        print(message, username, webhook_url)
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
    auth = request.args.get("auth")

    if auth != os.getenv("AUTH_KEY"):
        return "Invalid auth key", 401
    return jsonify([message_log, ai_messages]), 200

# Endpoint to send private DM
@app.route('/messages/send_private', methods=['POST'])
def send_private():
    data = request.json
    message = data.get('message')
    username = data.get('name')
    tag = data.get('tag')
    auth = request.args.get("auth")

    if auth != os.getenv("AUTH_KEY"):
        return "Invalid auth key", 401

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
    auth = request.args.get("auth")

    if auth != os.getenv("AUTH_KEY"):
        return "Invalid auth key", 401

    if os.path.exists('webhooks.json'):
        with open('webhooks.json', 'r') as f:
            return jsonify(json.load(f))
    else:
        return jsonify({})

@app.route('/tag', methods=['POST'])
def get_user_tags():
    auth = request.args.get("auth")

    if auth != os.getenv("AUTH_KEY"):
        return "Invalid auth key", 401

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

@app.route('/llm', methods=['POST'])
def send_to_llm():
    global ai_messages
    auth = request.args.get("auth")

    if auth != os.getenv("AUTH_KEY"):
        return "Invalid auth key", 401

    data = request.json
    model = data.get("model")
    messages = data.get("messages")
    temperature = data.get("temperature")

    if not all([model, messages, temperature]):
        return "Missing fields", 400

    ai_messages = messages

    print(f"received {ai_messages}")

    payload = {
        "model": model,
        "messages": ai_messages.get(model),
        "temperature": temperature
    }

    response = requests.post(LLM_URL, json=payload)
    if response.status_code == 200:
        text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        ai_messages.get(model).append({"role": "assistant", "content": text})

        asyncio.run_coroutine_threadsafe(save_messages(), bot.loop)

        return text, 200
    else:
        return f"Error: {response.status_code} - {response.text}", response.status_code

@app.route("/models", methods = ["GET"])
def get_models():
    auth = request.args.get("auth")

    if auth != os.getenv("AUTH_KEY"):
        return "Invalid auth key", 401

    url = os.getenv("MODELS")
    response = requests.get(url)

    if response.ok:
        return response.json().get("data"), 200
    else:
        return f"Error: {response.status_code} - {response.text}", response.status_code

# Capture messages from all servers the bot is in
@bot.event
async def on_message(message : discord.Message):
    global message_log

    guild = str(message.guild) if not str(message.guild) == "None" else "DMs"

    channel = None if "Direct Message" in str(message.channel) else str(message.channel)

    if channel is None:
        if not message.author.bot:
            channels[message.channel.id] = str(message.author.name)
            with open("channels.json", "w") as f:
                json.dump(channels, f)

        channel = channels.get(message.channel.id)

    if channel is None:
        return

    if message_log.get(guild) is None:
        message_log[guild] = {}

    if message_log.get(guild).get(channel) is None:
        message_log[guild][channel] = []

    message_log[guild][channel].append({
        'author': f"{message.author.name}",
        'content': message.content,
        'channel': channel,
        'timestamp': str(message.created_at)
    })

    if len(message_log.get(guild).get(channel)) > 100:
        message_log[guild][channel] = message_log[guild][channel][1:]

    await save_messages()
    await bot.process_commands(message)

async def save_messages():
    with open("messages.json", "w") as f:
        json.dump(message_log, f)

    with open("ai_messages.json", "w") as f:
        json.dump(message_log, f)

@bot.event
async def on_guild_join(guild : discord.Guild):
    webhook_store[guild.name] = {}
    for channel in guild.text_channels:
        try:
            webhook = await channel.create_webhook(name='AutoWebhook')
            print(f"Created webhook: {webhook.url} in {channel.name}")
            webhook_store[guild.name][channel.name] = webhook.url
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
    flask_thread = threading.Thread(target=run_flask)
    try:
        flask_thread.start()
        bot.run(os.getenv("BOT_TOKEN"))
    except KeyboardInterrupt:
        print("Exiting...")
        flask_thread.join()