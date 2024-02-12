import asyncio

from nio import AsyncClient

from lemmyreportmessenger.data import ContentType
from .lemmy_facade import Report


class MatrixFacade:
    client: AsyncClient
    room_id: str
    lemmy_instance: str

    def __init__(self, client: AsyncClient, room_id: str, instance_url: str):
        self.client = client
        self.room_id = room_id
        self.lemmy_instance = instance_url

    async def setup(self, password: str):
        print(await self.client.login(password=password, device_name="lemmy-report-bot"))

        if self.room_id in (await self.client.joined_rooms()).rooms:
            return
        await self.client.join(self.room_id)

    async def send_report_message(self, report: Report, community_name: str):
        url = report.get_url(self.lemmy_instance)
        print(f"Sending report on {url} for reason: {report.reason}")

        await self.client.room_send(
            room_id=self.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.notice",
                "format": "org.matrix.custom.html",
                "body": f"The post in /c/{community_name} at {url} has been reported by "
                        f"{report.actor_display_name} for {report.reason}",
                "formatted_body": f"The post in /c/{community_name} at <a href='{url}'>{url}</a> has been reported by "
                                  f"<a href='{report.actor_id}'>{report.actor_display_name}</a> for <i>{report.reason}</i>"
            }
        )
