from sqlalchemy import select

from .base import session_scope, Report
from .content_type import ContentType


class ReportPersistence:

    # noinspection PyMethodMayBeStatic
    def acknowledge_report(self, report_id: int, report_type: ContentType, community_id: int):
        with session_scope() as session:
            session.add(
                Report(
                    report_id=report_id,
                    report_type=report_type,
                    community_id=community_id
                )
            )

    # noinspection PyMethodMayBeStatic
    def has_been_acknowledged(self, report_id: int, report_type: ContentType) -> bool:
        with session_scope() as session:
            report = (session.execute(select(Report).filter(
                Report.report_id == report_id and Report.report_type == report_type)
            )).scalar_one_or_none()

            return report is not None
