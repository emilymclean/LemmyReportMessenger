import os

from lemmyreportmessenger import LemmyReportMessenger

if __name__ == "__main__":
    LemmyReportMessenger.create(
        [x.strip() for x in os.getenv("LEMMY_COMMUNITIES").split(',')],
        os.getenv("LEMMY_INSTANCE"),
        os.getenv("LEMMY_USERNAME"),
        os.getenv("LEMMY_PASSWORD"),
        os.getenv("MATRIX_INSTANCE"),
        os.getenv("MATRIX_USERNAME"),
        os.getenv("MATRIX_PASSWORD"),
        os.getenv("MATRIX_ROOM")
    ).run()
