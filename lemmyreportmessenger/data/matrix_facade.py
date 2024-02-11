import asyncio

from nio import AsyncClient

from lemmyreportmessenger.data import ContentType


class MatrixFacade:
    client: AsyncClient
    room_id: str
    instance_url: str

    def __init__(self, client: AsyncClient, room_id: str, instance_url: str):
        self.client = client
        self.room_id = room_id
        self.instance_url = instance_url
        asyncio.run(self.join_room())

    async def join_room(self):
        if self.room_id not in (await self.client.joined_rooms()).rooms:
            await self.client.join(self.room_id)

    async def send_report_message(self, content_id: int, content_type: ContentType, reason: str):
        await self.join_room()
        url = f"{self.instance_url}/{'post' if content_type == ContentType.POST else 'comment'}/{content_id}"

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