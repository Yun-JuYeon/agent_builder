from datetime import datetime, timedelta, timezone


def get_KST_timestamp():
    KST = timezone(timedelta(hours=9))
    timestamp = datetime.now(KST).isoformat()
    return timestamp


def format_timestamp(timestamp: float) -> str:
  """Formats the timestamp of the memory entry."""
  return datetime.fromtimestamp(timestamp).isoformat()
