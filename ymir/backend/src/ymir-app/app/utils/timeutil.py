from datetime import datetime, timezone


def convert_datetime_to_timestamp(dt: datetime) -> float:
    """
    Convert utc datetime to timestamp
    """
    return dt.replace(tzinfo=timezone.utc).timestamp()
