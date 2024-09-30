import asyncio
import traceback
from typing import List

from nio import AsyncClient
from pythonlemmy import LemmyHttp

from .data import ReportPersistence, LemmyFacade, Report
from .data.matrix_facade import MatrixFacade
from .reconnection_manager import ReconnectionDelayManager


class LemmyReportMessenger:
    community_names: List[str]
    reconnection_manager: ReconnectionDelayManager = ReconnectionDelayManager()
    report_persistence: ReportPersistence
    lemmy_facade: LemmyFacade
    matrix_facade: MatrixFacade

    def __init__(
            self,
            community_names: List[str],
            report_persistence: ReportPersistence,
            lemmy_facade: LemmyFacade,
            matrix_facade: MatrixFacade
    ):
        self.community_names = community_names
        self.report_persistence = report_persistence
        self.lemmy_facade = lemmy_facade
        self.matrix_facade = matrix_facade

    @staticmethod
    async def create(
            community_names: List[str],
            lemmy_instance: str,
            lemmy_username: str,
            lemmy_password: str,
            matrix_instance: str,
            matrix_username: str,
            matrix_password: str,
            matrix_room: str
    ):
        lemmy_http = LemmyHttp(lemmy_instance)
        lemmy_http.login(lemmy_username, lemmy_password)

        matrix = MatrixFacade(
            AsyncClient(matrix_instance, user=matrix_username),
            matrix_room,
            lemmy_instance
        )
        await matrix.setup(matrix_password)

        return LemmyReportMessenger(
            community_names,
            ReportPersistence(),
            LemmyFacade(
                lemmy_http
            ),
            matrix
        )

    @staticmethod
    async def create_jwt(
            community_names: List[str],
            lemmy_instance: str,
            lemmy_jwt: str,
            matrix_instance: str,
            matrix_username: str,
            matrix_password: str,
            matrix_room: str
    ):
        lemmy_http = LemmyHttp(lemmy_instance)
        lemmy_http.set_jwt(lemmy_jwt)

        matrix = MatrixFacade(
            AsyncClient(matrix_instance, user=matrix_username),
            matrix_room,
            lemmy_instance
        )
        await matrix.setup(matrix_password)

        return LemmyReportMessenger(
            community_names,
            ReportPersistence(),
            LemmyFacade(
                lemmy_http
            ),
            matrix
        )

    async def run(self):
        while True:
            # noinspection PyBroadException
            try:
                await self.scan()
            except Exception:
                print(traceback.format_exc())
                self.reconnection_manager.wait()

            print("Sleeping for 60 seconds")
            await asyncio.sleep(60)

    async def scan(self):
        for community_name in self.community_names:
            print(f"Scanning community {community_name}")
            community_id = self.lemmy_facade.get_community_id(community_name)
            await self._process_reports(self.lemmy_facade.get_post_reports(community_id), community_id, community_name)
            await self._process_reports(self.lemmy_facade.get_comment_reports(community_id), community_id, community_name)

    async def _process_reports(self, reports: List[Report], community_id: int, community_name: str):
        for report in reports:
            if report.resolved:
                continue
            acknowledged = (
                self.report_persistence.has_been_acknowledged(report.report_id, report.content_type))
            if acknowledged:
                continue

            await self.matrix_facade.send_report_message(report, community_name)

            self.report_persistence.acknowledge_report(report.report_id, report.content_type, community_id)
