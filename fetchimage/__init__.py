from maubot import Plugin, MessageEvent
from maubot.handlers import command
from mautrix.types import MessageType, MediaMessageEventContent

import imghdr
import io
import random
import string
import urllib.request

class FetchImageBot(Plugin):
    @command.new()
    @command.argument("image_url", required=True)
    async def fetch_image(self, evt: MessageEvent, image_url: str) -> None:
        resp = await self.http.get(image_url)
        if resp.status == 200:
            data = await resp.read()
            if not imghdr.what(io.BytesIO(data)):
                await evt.reply("There doesn't seem to be an image here... 🤔")
                return
            file_name = image_url.split("/")[-1][-40:]
            uri = await self.client.upload_media(data)
            content = MediaMessageEventContent(url=uri, body=file_name,
                                               msgtype=MessageType.IMAGE,
                                               external_url=image_url)
            await self.client.send_message(evt.room_id, content)
        else:
            await evt.reply(f"Fetching \"{image_url}\" failed: {resp.status} {await resp.text()}")
