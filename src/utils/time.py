from datetime import datetime, timezone


def utc_signed_now():
    return datetime.now(timezone.utc)
