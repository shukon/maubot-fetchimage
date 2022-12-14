from aiohttp.client_exceptions import ClientConnectorError, ClientSSLError
import imghdr
import io
import random
import string
from typing import Optional
import urllib.request

from maubot import Plugin, MessageEvent
from maubot.handlers import command
from mautrix.types import MessageType, MediaMessageEventContent

class FetchImageBot(Plugin):

    @command.new()
    @command.argument("image_url", required=True)
    async def fetch_image(self, evt: MessageEvent, image_url: str) -> None:
        try:
            await self._fetch_image(evt, image_url, ssl=True)
        except ClientSSLError as err:
            await evt.reply(f"Warning: SSL certificate error (Error: {err})!")
            await self._fetch_image(evt, image_url, ssl=False)
        except ClientConnectorError as err:
            await evt.reply(f"Fetching \"{image_url}\" failed: {err}")

    async def _fetch_image(self, evt: MessageEvent, image_url: str, ssl: Optional[bool] = None) -> None:
        self.log.debug(f'Fetching {image_url} with ssl: {ssl}')
        if ssl is True:
            # pass ssl=None to enable default ssl checks
            ssl = None
        resp = await self.http.get(image_url, ssl=ssl)
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
            await evt.reply(content)
        else:
            await evt.reply(f"Fetching \"{image_url}\" failed: {resp.status} {await resp.text()}")
