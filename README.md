# Discord-API
## Endpoints
- `/messages/send` - POST json `{"message": "{message}", "name": "{name of the bot}", "pfp": "{optional url}", "webhook": "{url of the webhook}"}` **This method is only for sending messages in servers, DMs have their own endpoint**
- `/messages/get` - GET json `{"{guild - DMs if it's a DM}": {"{channel name - tag of the person if DM}": [{"author": "{author}", "content": "{message content}", "channel": "{channel - same as the key}", "timestamp": "{timestamp}"}, ...]}}`
- `/messages/send_private` - POST json `{"message": "{message}", "name": "name of the sender", "tag": "tag of the receiver"}`
- `/webhooks` - GET json `{"{Server}": ["{channel}": "{webhook url}"}, ...]`
- `/tag` - POST json `{"username": "{username}"}` return `[{"username": "{tag}", "id": "{discord id}", "guild": "{discord server}"}, ...]`

You have to pass a correct auth key as well, you can pass the auth key like so: http://example.com/messages/send?auth=your_key