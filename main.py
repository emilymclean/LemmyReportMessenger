import asyncio
import os

from lemmyreportmessenger import LemmyReportMessenger


async def instantiate_and_run():
    if os.getenv("LEMMY_USERNAME") is not None and os.getenv("LEMMY_PASSWORD") is not None:
        messenger = await LemmyReportMessenger.create(
            [x.strip() for x in os.getenv("LEMMY_COMMUNITIES").split(',')],
            os.getenv("LEMMY_INSTANCE"),
            os.getenv("LEMMY_USERNAME"),
            os.getenv("LEMMY_PASSWORD"),
            os.getenv("MATRIX_INSTANCE"),
            os.getenv("MATRIX_USERNAME"),
            os.getenv("MATRIX_PASSWORD"),
            os.getenv("MATRIX_ROOM")
        )
    elif os.getenv("LEMMY_JWT") is not None:
        messenger = await LemmyReportMessenger.create_jwt(
            [x.strip() for x in os.getenv("LEMMY_COMMUNITIES").split(',')],
            os.getenv("LEMMY_INSTANCE"),
            os.getenv("LEMMY_JWT"),
            os.getenv("MATRIX_INSTANCE"),
            os.getenv("MATRIX_USERNAME"),
            os.getenv("MATRIX_PASSWORD"),
            os.getenv("MATRIX_ROOM")
        )
    else:
        raise Exception("Please provide LEMMY_USERNAME and LEMMY_PASSWORD, or LEMMY_JWT")

    await messenger.run()

if __name__ == "__main__":
    asyncio.run(instantiate_and_run())