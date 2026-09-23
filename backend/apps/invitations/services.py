from __future__ import annotations

import secrets
from datetime import date, time

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .exceptions import InvitationError
from .models import (
    ActivityOption,
    AvailableDate,
    AvailableTime,
    Invitation,
    InvitationPhoto,
    MemoryCard,
    RecipientResponse,
)


def generate_public_token() -> str:
    alphabet = "abcdefghijkmnopqrstuvwxyz23456789"
    return "".join(secrets.choice(alphabet) for _ in range(10))


def generate_management_token() -> str:
    return secrets.token_urlsafe(32)


def _unique_token(field_name: str, factory, attempts: int = 12) -> str:
    for _ in range(attempts):
        token = factory()
        if not Invitation.objects.filter(**{field_name: token}).exists():
            return token
    raise InvitationError("Could not create a unique invitation link. Please try again.")


DEFAULT_ACTIVITIES = (
    ("Coffee", "☕"),
    ("Dinner", "🍝"),
    ("Movie", "🎬"),
    ("Walk", "🌆"),
    ("Something different", "🎨"),
)


@transaction.atomic
def create_invitation(payload: dict) -> Invitation:
    invitation = Invitation(
        public_token=_unique_token("public_token", generate_public_token),
        management_token=_unique_token("management_token", generate_management_token),
        sender_name=payload["sender_name"].strip(),
        recipient_name=payload["recipient_name"].strip(),
        main_message=payload["main_message"].strip(),
        personal_message=(payload.get("personal_message") or "").strip(),
        question_text=(payload.get("question_text") or Invitation._meta.get_field("question_text").default).strip(),
        decline_message=(payload.get("decline_message") or "Maybe another time?").strip(),
        theme=payload.get("theme") or Invitation.Theme.ELEGANT,
        show_welcome=payload.get("show_welcome", True),
        show_personal_message=payload.get("show_personal_message", True),
        show_memories=payload.get("show_memories", False),
        allow_multiple_activities=payload.get("allow_multiple_activities", False),
        greeting=(payload.get("greeting") or "").strip(),
        unlock_code=(payload.get("unlock_code") or "").strip(),
        unlock_hint=(payload.get("unlock_hint") or "Пароль это дата нашего первого свидания").strip(),
        finale_note_type=payload.get("finale_note_type") or "letter",
        spotify_url=(payload.get("spotify_url") or "").strip()[:400],
        music_start_sec=int(payload.get("music_start_sec") or 0),
        music_end_sec=int(payload["music_end_sec"]) if payload.get("music_end_sec") else None,
    )
    invitation.full_clean()
    invitation.save()

    activities = payload.get("activities")
    if activities:
        for index, item in enumerate(activities):
            ActivityOption.objects.create(
                invitation=invitation,
                name=item["name"].strip(),
                icon=(item.get("icon") or "").strip()[:16],
                enabled=item.get("enabled", True),
                order=index,
            )
    else:
        for index, (name, icon) in enumerate(DEFAULT_ACTIVITIES):
            ActivityOption.objects.create(
                invitation=invitation,
                name=name,
                icon=icon,
                enabled=True,
                order=index,
            )

    date_map: dict[date, AvailableDate] = {}
    for value in payload.get("available_dates") or []:
        parsed = value if isinstance(value, date) else date.fromisoformat(str(value))
        if parsed in date_map:
            continue
        date_map[parsed] = AvailableDate.objects.create(invitation=invitation, date=parsed)

    for item in payload.get("available_times") or []:
        raw_time = item["time"] if isinstance(item, dict) else item
        parsed_time = raw_time if isinstance(raw_time, time) else time.fromisoformat(str(raw_time))
        related_date = None
        if isinstance(item, dict) and item.get("date"):
            date_value = item["date"] if isinstance(item["date"], date) else date.fromisoformat(str(item["date"]))
            related_date = date_map.get(date_value)
        AvailableTime.objects.create(
            invitation=invitation,
            date=related_date,
            time=parsed_time,
        )

    for index, memory in enumerate((payload.get("memories") or [])[: settings.MAX_MEMORY_CARDS]):
        MemoryCard.objects.create(
            invitation=invitation,
            title=memory["title"].strip(),
            description=(memory.get("description") or "").strip(),
            order=index,
        )
        if memory.get("title"):
            invitation.show_memories = True
            invitation.save(update_fields=["show_memories", "updated_at"])

    return invitation


def get_public_invitation(public_token: str) -> Invitation:
    try:
        return Invitation.objects.prefetch_related(
            "photos",
            "memories",
            "activities",
            "available_dates",
            "available_times",
        ).get(public_token=public_token)
    except Invitation.DoesNotExist as exc:
        raise InvitationError("This invitation is no longer available.", status_code=404) from exc


def get_managed_invitation(public_token: str, management_token: str) -> Invitation:
    invitation = get_public_invitation(public_token)
    try:
        if not secrets.compare_digest(invitation.management_token, management_token):
            raise InvitationError("You do not have access to manage this invitation.", status_code=403)
    except ValueError as exc:
        raise InvitationError("You do not have access to manage this invitation.", status_code=403) from exc
    return invitation


@transaction.atomic
def submit_response(invitation: Invitation, answer: str, decline_reason: str = "") -> RecipientResponse:
    if invitation.status in {Invitation.Status.DECLINED, Invitation.Status.CONFIRMED}:
        raise InvitationError("This invitation has already been answered.")
    if hasattr(invitation, "response"):
        raise InvitationError("A response has already been saved.")
    if answer not in RecipientResponse.Answer.values:
        raise InvitationError("Please choose yes or not this time.")

    response = RecipientResponse.objects.create(
        invitation=invitation,
        answer=answer,
        decline_reason=decline_reason.strip() if answer == RecipientResponse.Answer.DECLINED else "",
    )
    invitation.responded_at = timezone.now()
    invitation.status = (
        Invitation.Status.ACCEPTED if answer == RecipientResponse.Answer.ACCEPTED else Invitation.Status.DECLINED
    )
    invitation.save(update_fields=["responded_at", "status", "updated_at"])
    return response


def _times_for_date(invitation: Invitation, selected_date: AvailableDate | None) -> list[time]:
    times = list(invitation.available_times.all())
    matching = []
    for item in times:
        if item.date_id is None or (selected_date and item.date_id == selected_date.id):
            matching.append(item.time)
    return matching


@transaction.atomic
def save_plan(
    invitation: Invitation,
    *,
    activity_ids: list[int] | None,
    date_id: int | None,
    selected_time: time | None,
    custom_date: date | None = None,
) -> RecipientResponse:
    if invitation.status not in {Invitation.Status.ACCEPTED, Invitation.Status.PLANNING}:
        raise InvitationError("Please accept the invitation before choosing a date.")
    if not hasattr(invitation, "response") or invitation.response.answer != RecipientResponse.Answer.ACCEPTED:
        raise InvitationError("This invitation was not accepted.")

    response = invitation.response
    enabled_activities = invitation.activities.filter(enabled=True)
    if enabled_activities.exists():
        if not activity_ids:
            raise InvitationError("Please choose an activity.")
        activities = list(enabled_activities.filter(id__in=activity_ids))
        if len(activities) != len(set(activity_ids)):
            raise InvitationError("One of the selected activities is not available.")
        if not invitation.allow_multiple_activities and len(activities) != 1:
            raise InvitationError("Please choose one activity.")
        response.selected_activities.set(activities)

    dates = invitation.available_dates.all()
    selected_date = None
    if date_id:
        try:
            selected_date = dates.get(id=date_id)
        except AvailableDate.DoesNotExist as exc:
            raise InvitationError("That date is not available.") from exc
    elif custom_date:
        selected_date, _created = AvailableDate.objects.get_or_create(
            invitation=invitation,
            date=custom_date,
        )
    elif dates.exists():
        raise InvitationError("Please choose a date.")
    if selected_date:
        response.selected_date = selected_date

    times = _times_for_date(invitation, selected_date)
    if times:
        if not selected_time:
            raise InvitationError("Please choose a time.")
        if selected_time not in times:
            raise InvitationError("That time is not available.")
        response.selected_time = selected_time

    invitation.status = Invitation.Status.PLANNING
    invitation.save(update_fields=["status", "updated_at"])
    response.save()
    return response


@transaction.atomic
def confirm_plan(invitation: Invitation) -> RecipientResponse:
    if invitation.status not in {Invitation.Status.ACCEPTED, Invitation.Status.PLANNING}:
        raise InvitationError("This invitation cannot be confirmed yet.")
    if not hasattr(invitation, "response"):
        raise InvitationError("Please answer the invitation first.")
    if invitation.response.answer != RecipientResponse.Answer.ACCEPTED:
        raise InvitationError("This invitation was not accepted.")

    response = invitation.response
    if invitation.activities.filter(enabled=True).exists() and not response.selected_activities.exists():
        raise InvitationError("Please choose an activity first.")
    if invitation.available_dates.exists() and response.selected_date_id is None:
        raise InvitationError("Please choose a date first.")
    if invitation.available_times.exists() and response.selected_time is None:
        raise InvitationError("Please choose a time first.")

    response.confirmed_at = timezone.now()
    response.save(update_fields=["confirmed_at", "updated_at"])
    invitation.status = Invitation.Status.CONFIRMED
    invitation.save(update_fields=["status", "updated_at"])
    return response


def add_photo(invitation: Invitation, image, caption: str = "") -> InvitationPhoto:
    if invitation.photos.count() >= settings.MAX_PHOTOS:
        raise InvitationError("You can add up to 5 photos.")
    photo = InvitationPhoto(
        invitation=invitation,
        image=image,
        caption=caption[:160],
        order=invitation.photos.count(),
    )
    photo.save()
    return photo


def add_memory_image(invitation: Invitation, memory_id: int, image) -> MemoryCard:
    try:
        memory = invitation.memories.get(id=memory_id)
    except MemoryCard.DoesNotExist as exc:
        raise InvitationError("That memory card was not found.") from exc
    memory.image = image
    memory.save(update_fields=["image"])
    invitation.show_memories = True
    invitation.save(update_fields=["show_memories", "updated_at"])
    return memory


def attach_music(invitation: Invitation, music) -> Invitation:
    invitation.music = music
    invitation.save(update_fields=["music", "updated_at"])
    return invitation


def save_finale_note(invitation: Invitation, text: str, kind: str = "text", media=None) -> RecipientResponse:
    if not hasattr(invitation, "response"):
        raise InvitationError("Please finish the invitation first.")
    response = invitation.response
    note_kind = kind if kind in {"text", "voice", "video"} else "text"
    body = (text or "").strip()[:2000]
    if not body and media:
        body = "Voice note" if note_kind == "voice" else "Video note"
    response.finale_note = body
    response.finale_note_kind = note_kind
    update = ["finale_note", "finale_note_kind", "updated_at"]
    if media is not None:
        response.finale_note_media = media
        update.append("finale_note_media")
    response.save(update_fields=update)
    return response
