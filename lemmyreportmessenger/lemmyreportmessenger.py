import asyncio
import traceback
from time import sleep
from typing import List

from lemmyreportmessenger.data import ReportPersistence, LemmyFacade, Report
from lemmyreportmessenger.data.matrix_facade import MatrixFacade
from lemmyreportmessenger.reconnection_manager import ReconnectionDelayManager


class LemmyReportMessenger:
    community_ids: List[int]
    reconnection_manager: ReconnectionDelayManager
    report_persistence: ReportPersistence
    lemmy_facade: LemmyFacade
    matrix_facade: MatrixFacade

    def run(self):
        while True:
            # noinspection PyBroadException
            try:
                self.scan()
                sleep(60)
            except Exception:
                print(traceback.format_exc())
                self.reconnection_manager.wait()

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
