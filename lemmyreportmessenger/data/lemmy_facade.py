from dataclasses import dataclass
from typing import List

from plemmy import LemmyHttp
from plemmy.responses import ListPostReportsResponse, ListCommentReportsResponse

from lemmyreportmessenger.data import ContentType


@dataclass
class Report:
    report_id: int
    content_id: int
    content_type: ContentType
    reason: str


class LemmyFacade:
    lemmy: LemmyHttp

    def __init__(self, lemmy: LemmyHttp):
        self.lemmy = lemmy

    def get_post_reports(self, community_id: int) -> List[Report]:
        reports = ListPostReportsResponse(self.lemmy.list_post_reports(community_id)).post_reports
        return [Report(
            report_id=r.post_report.id,
            content_id=r.post.id,
            content_type=ContentType.POST,
            reason=r.post_report.reason
        ) for r in reports]

    def get_comment_reports(self, community_id: int) -> List[Report]:
        reports = ListCommentReportsResponse(self.lemmy.list_comment_reports(community_id)).comment_reports
        return [Report(
            report_id=r.comment_report.id,
            content_id=r.comment.id,
            content_type=ContentType.COMMENT,
            reason=r.comment_report.reason
        ) for r in reports]
