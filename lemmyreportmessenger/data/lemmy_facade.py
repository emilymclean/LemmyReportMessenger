from dataclasses import dataclass
from typing import List, Dict

from pythonlemmy import LemmyHttp
from pythonlemmy.responses import ListPostReportsResponse, ListCommentReportsResponse, GetCommunityResponse

from lemmyreportmessenger.data import ContentType, content_type


@dataclass
class Report:
    report_id: int
    content_id: int
    content_type: ContentType
    reason: str
    resolved: bool
    actor_id: str
    actor_display_name: str

    def get_url(self, instance: str) -> str:
        return f"{instance}/{'post' if self.content_type == ContentType.POST else 'comment'}/{self.content_id}"


class LemmyFacade:
    lemmy: LemmyHttp
    cached_community_id: Dict[str, int] = {}

    def __init__(self, lemmy: LemmyHttp):
        self.lemmy = lemmy

    def get_post_reports(self, community_id: int) -> List[Report]:
        reports = ListPostReportsResponse(self.lemmy.list_post_reports(community_id)).post_reports
        return [Report(
            report_id=r.post_report.id,
            content_id=r.post.id,
            content_type=ContentType.POST,
            reason=r.post_report.reason,
            resolved=r.post_report.resolved,
            actor_id=r.creator.actor_id,
            actor_display_name=r.creator.display_name
        ) for r in reports]

    def get_comment_reports(self, community_id: int) -> List[Report]:
        reports = ListCommentReportsResponse(self.lemmy.list_comment_reports(community_id)).comment_reports

        return [Report(
            report_id=r.comment_report.id,
            content_id=r.comment.id,
            content_type=ContentType.COMMENT,
            reason=r.comment_report.reason,
            resolved=r.comment_report.resolved,
            actor_id=r.creator.actor_id,
            actor_display_name=r.creator.display_name
        ) for r in reports]

    def get_community_id(self, community_name: str) -> int:
        if community_name in self.cached_community_id:
            return self.cached_community_id[community_name]

        community_id = GetCommunityResponse(self.lemmy.get_community(name=community_name)).community_view.community.id
        self.cached_community_id[community_name] = community_id
        return community_id
