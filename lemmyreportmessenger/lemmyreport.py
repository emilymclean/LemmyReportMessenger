import asyncio
import traceback
from time import sleep
from typing import List

from nio import AsyncClient
from plemmy import LemmyHttp
from plemmy.responses import GetCommunityResponse

from .data import ReportPersistence, LemmyFacade, Report
from .data.matrix_facade import MatrixFacade
from .reconnection_manager import ReconnectionDelayManager


class LemmyReportMessenger:
    community_ids: List[int]
    reconnection_manager: ReconnectionDelayManager = ReconnectionDelayManager()
    report_persistence: ReportPersistence
    lemmy_facade: LemmyFacade
    matrix_facade: MatrixFacade

    def __init__(
            self,
            community_ids: List[int],
            report_persistence: ReportPersistence,
            lemmy_facade: LemmyFacade,
            matrix_facade: MatrixFacade
    ):
        self.community_ids = community_ids
        self.report_persistence = report_persistence
        self.lemmy_facade = lemmy_facade
        self.matrix_facade = matrix_facade

    @staticmethod
    def create(
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

        community_ids = [GetCommunityResponse(
            lemmy_http.get_community(name=c)
        ).community_view.community.id for c in community_names]

        client = AsyncClient(matrix_instance)
        client.login(matrix_username, matrix_password)

        return LemmyReportMessenger(
            community_ids,
            ReportPersistence(),
            LemmyFacade(
                lemmy_http
            ),
            MatrixFacade(
                client,
                matrix_room,
                lemmy_instance
            )
        )

    def run(self):
        while True:
            # noinspection PyBroadException
            try:
                self.scan()
            except Exception:
                print(traceback.format_exc())
                self.reconnection_manager.wait()

            sleep(60)

    def scan(self):
        for community_id in self.community_ids:
            self._process_reports(self.lemmy_facade.get_post_reports(community_id))
            self._process_reports(self.lemmy_facade.get_comment_reports(community_id))

    def _process_reports(self, reports: List[Report]):
        for report in reports:
            acknowledged = (
                self.report_persistence.has_been_acknowledged(report.report_id, report.content_type))
            if acknowledged:
                continue

            asyncio.run(self.matrix_facade.send_report_message(report.content_id, report.content_type, report.reason))
