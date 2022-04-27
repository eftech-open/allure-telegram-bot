from datetime import datetime, timedelta
from pytz import utc


def change_to_timestamp(date_string):
    return datetime.timestamp(date_string) * 1000


def change_date_pattern(date_string, pattern: str):
    return datetime.strptime(date_string, format=pattern)


def form_nowdate(pattern: str = "%Y-%m-%d %H:%M:%S"):
    return datetime.strftime(datetime.now(), fmt=pattern)


def form_timedelta(days: int = 0, hours: int = 0, minutes: int = 0, pattern: str = "%Y-%m-%d %H:%M:%S"):
    return datetime.strftime(datetime.now() - timedelta(days=days, hours=hours, minutes=minutes), fmt=pattern)


def form_timezone():
    return utc.localize(datetime.utcnow()).astimezone().tzinfo
