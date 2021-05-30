from datetime import datetime, timezone


def isoformat(timestamp: datetime):
    timestamp = timestamp.astimezone(tz=timezone.utc)
    isostr = timestamp.isoformat(timespec='milliseconds')
    isostr = isostr.replace('+00:00', 'Z')
    return isostr
