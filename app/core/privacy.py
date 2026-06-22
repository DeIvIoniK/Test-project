from datetime import datetime, timedelta, timezone

DIALOGUE_TTL = timedelta(minutes=30)


def should_delete_dialogue(last_activity_at: datetime | None, now: datetime | None = None) -> bool:
    if last_activity_at is None:
        return False
    current = now or datetime.now(timezone.utc)
    return current - last_activity_at > DIALOGUE_TTL
