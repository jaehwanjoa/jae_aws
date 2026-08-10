def extract_time_range(question):

    q = question.lower()

    if "최근 1시간" in q:
        return "1h"

    if "최근 24시간" in q:
        return "24h"

    if "오늘" in q:
        return "24h"

    if "최근 7일" in q:
        return "7d"

    if "이번주" in q:
        return "7d"

    return None
