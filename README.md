# Discord-API
## Installation

### Basic Setup
This has no functionality

1. Download or clone this Repository
2. Run `pip install -r requirements.txt`

### Discord
With this can use Discord

1. Create your [Discord bot](https://discord.com/developers/)
2. Create a file called `.env` looking something like this:
```
BOT_TOKEN = {Your bot token}
AUTH_KEY = {Your auth key}
```
3. To generate your auth key, run `py generate_key.py`, If you have suspicion that someone has your key, or you want to stay secure, you can always change this

**Don't forget to set up the raspberry pi for Discord, you can see everything [here](https://github.com/FAV-SmartGlasses/SmartGlasses/tree/main?tab=readme-ov-file#how-to-set-up-the-discord-client)**

### LLMs
With this, you can use LLMs

1. Download [LM studio](https://lmstudio.ai)
2. Add this to `.env`:
```
LLM_SERVER = http://{LM studio's IP}:1234/v1/chat/completions
MODELS = http://{LM studio's IP}:1234/v1/models
AUTH_KEY = {Your Auth Key}
```

## Running
1. Run `py discord_api.py`
2. If you want to use LLMs, start your LM studio server

## Endpoint Docs
| Endpoint                 | Method      | Description                                                                                                                                                                                                         |
|--------------------------|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/messages/send`         | `POST` json | `{"message": "{message}", "name": "{name of the bot}", "pfp": "{optional url}", "webhook": "{url of the webhook}"}` **This method is only for sending messages in servers, DMs have their own endpoint**            |
| `/messages/get`          | `GET` json  | `{"{guild - DMs if it's a DM}": {"{channel name - tag of the person if DM}": [{"author": "{author}", "content": "{message content}", "channel": "{channel - same as the key}", "timestamp": "{timestamp}"}, ...]}}` |
| `/messages/send_private` | `POST` json | `{"message": "{message}", "name": "name of the sender", "tag": "tag of the receiver"}`                                                                                                                              |
| `/webhooks`              | `GET` json  | `{"{Server}": ["{channel}": "{webhook url}"}, ...], ...}`                                                                                                                                                           |
| `/tag`                   | `POST` json | `{"username": "{username}"}` return `[{"username": "{tag}", "id": "{discord id}", "guild": "{discord server}"}, ...]`                                                                                               |
| `/llm`                   | `POST` json | `{"model": "{model}", "temperature": "{temperature}", "messages": {"{model}": [{"role": "{role}", "content": "content"}] }`                                                                                         |
| `/models`                | `GET` json  | `[{"id": "{model name}", ...}, ...]`                                                                                                                                                                                |

You have to pass a correct auth key as well, you can pass the auth key like so: http://example.com/messages/send?auth=your_key