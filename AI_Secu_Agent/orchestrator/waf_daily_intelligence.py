from datetime import datetime
from datetime import timedelta

@classmethod
def get_weekly_range(
    cls
):

    today = datetime.now()

    this_monday = (
        today
        - timedelta(days=today.weekday())
    )

    current_start = (
        this_monday
        - timedelta(days=7)
    )

    current_end = (
        this_monday
        - timedelta(days=1)
    )

    previous_start = (
        current_start
        - timedelta(days=7)
    )

    previous_end = (
        current_start
        - timedelta(days=1)
    )

    return {
        "current_start":
            current_start.strftime("%Y-%m-%d"),

        "current_end":
            current_end.strftime("%Y-%m-%d"),

        "previous_start":
            previous_start.strftime("%Y-%m-%d"),

        "previous_end":
            previous_end.strftime("%Y-%m-%d")
    }
