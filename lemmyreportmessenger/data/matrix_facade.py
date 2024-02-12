import asyncio

from nio import AsyncClient

from lemmyreportmessenger.data import ContentType


class MatrixFacade:
    client: AsyncClient
    room_id: str
    lemmy_instance: str

    def __init__(self, client: AsyncClient, room_id: str, instance_url: str):
        self.client = client
        self.room_id = room_id
        self.lemmy_instance = instance_url
        asyncio.run(self._join_room())

    async def _join_room(self):
        if self.room_id in (await self.client.joined_rooms()).rooms:
            return
        await self.client.join(self.room_id)

    async def send_report_message(self, content_id: int, content_type: ContentType, reason: str):
        await self._join_room()
        url = f"{self.lemmy_instance}/{'post' if content_type == ContentType.POST else 'comment'}/{content_id}"

        await self.client.room_send(
            room_id=self.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.notice",
                "format": "org.matrix.custom.html",
                "body": f"The post at {url} has been reported for {reason}",
                "formatted_body": f"The post at <a href='{url}'>{url}</a> has been reported for <i>{reason}</i>"
            }
        )