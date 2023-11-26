from datetime import datetime, timezone


def period_to_date(period_date: str) -> datetime:
    """
    Transform a string into a date object.
    The string comes with the format "January 2023"
    :param period_date: String to be transformed in date object
    :return: Datetime time object
    """
    return datetime.strptime(period_date, '%B %Y')


def date_to_str(date_obj: datetime) -> str:
    """Transform a datetime object into a string
    with the format "2022-12-31"
    """
    return date_obj.strftime('%Y-%m-%d')


def datetime_now() -> datetime:
    """Get the current datetime with utc timezone"""
    return datetime.now(timezone.utc)
