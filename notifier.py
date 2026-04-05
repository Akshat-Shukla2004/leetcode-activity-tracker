import random

def send_alert(body: str) -> bool:
    """
    Send a two-part stealth alert:
      Part 1 → Fake casual message (WITH notification)
      Part 2 → Real message (SILENT, hidden until opened)
    """

    fake_msgs = [
        "hop on fort",
        "bro come valo?",
        "1 game?",
        "queue?",
        "u online?",
        "come discord",
        "quick match?",
        "we need 1 more",
        "join fast",
        "playing?"
    ]

    bait = random.choice(fake_msgs)

    ok1 = _send_raw(bait, disable_notification=False)
    if not ok1:
        logger.error("Failed to send bait message; skipping body.")
        return False

    # Small delay so messages arrive in order
    time.sleep(0.7)

    ok2 = _send_raw(body, disable_notification=True)
    return ok1 and ok2