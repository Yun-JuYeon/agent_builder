from datetime import datetime, timedelta, timezone


def get_KST_timestamp():
    KST = timezone(timedelta(hours=9))
    timestamp = datetime.now(KST).isoformat()
    return timestamp
    