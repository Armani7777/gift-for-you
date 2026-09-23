from __future__ import annotations

import logging
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMessage

from .models import GuestReply

logger = logging.getLogger(__name__)


def notify_guest_reply(reply: GuestReply) -> None:
    to = (getattr(settings, "NOTIFY_EMAIL", "") or "").strip()
    if not to:
        logger.info("NOTIFY_EMAIL is empty; reply %s was saved without sending mail.", reply.session_key)
        return

    who = reply.recipient_name or "her"
    subject = f"Her answer: {who}"
    activities = ", ".join(str(item) for item in (reply.activities or [])) or "—"
    lines = [
        f"From: {who}",
        f"For: {reply.sender_name or '—'}",
        f"Answer: {reply.answer or '—'}",
        f"Activities: {activities}",
        f"Date: {reply.selected_date or '—'}",
        f"Time: {reply.selected_time or '—'}",
        f"Note type: {reply.finale_note_kind or '—'}",
        f"Note: {reply.finale_note or '—'}",
        "",
        "The same answers are saved on the site at /answers.",
    ]
    email = EmailMessage(
        subject,
        "\n".join(lines),
        settings.DEFAULT_FROM_EMAIL,
        [to],
    )
    if reply.media:
        try:
            reply.media.open("rb")
            content = reply.media.read()
            name = Path(reply.media.name).name
            kind = "video/webm" if reply.finale_note_kind == "video" else "audio/webm"
            if name.endswith(".mp4"):
                kind = "video/mp4"
            email.attach(name, content, kind)
        except OSError:
            logger.exception("Could not attach reply media for %s", reply.session_key)
        finally:
            try:
                reply.media.close()
            except OSError:
                pass
    try:
        email.send(fail_silently=False)
    except Exception:
        logger.exception("Could not send reply email for %s", reply.session_key)
