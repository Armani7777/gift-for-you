from __future__ import annotations

import uuid
from pathlib import Path

from django.db import models
from django.utils import timezone


def _upload_to(folder: str, instance, filename: str) -> str:
    suffix = Path(filename).suffix.lower()[:8] or ".bin"
    token = getattr(getattr(instance, "invitation", None), "public_token", "draft")
    return f"invitations/{token}/{folder}/{uuid.uuid4().hex}{suffix}"


def invitation_photo_upload(instance, filename: str) -> str:
    return _upload_to("photos", instance, filename)


def memory_image_upload(instance, filename: str) -> str:
    return _upload_to("memories", instance, filename)


def invitation_music_upload(instance, filename: str) -> str:
    suffix = Path(filename).suffix.lower()[:8] or ".mp3"
    return f"invitations/{instance.public_token}/music/{uuid.uuid4().hex}{suffix}"


def finale_note_upload(instance, filename: str) -> str:
    return _upload_to("notes", instance, filename)


class Invitation(models.Model):
    class Theme(models.TextChoices):
        MINIMAL = "minimal", "Minimal"
        ROMANTIC = "romantic", "Romantic"
        SUNSET = "sunset", "Sunset"
        NIGHT = "night", "Night"
        SOFT = "soft", "Soft"
        ELEGANT = "elegant", "Elegant"

    class Status(models.TextChoices):
        CREATED = "created", "Created"
        OPENED = "opened", "Opened"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        PLANNING = "planning", "Planning"
        CONFIRMED = "confirmed", "Confirmed"

    public_token = models.CharField(max_length=64, unique=True, db_index=True)
    management_token = models.CharField(max_length=64, unique=True, db_index=True)

    sender_name = models.CharField(max_length=80)
    recipient_name = models.CharField(max_length=80)
    main_message = models.CharField(max_length=240)
    personal_message = models.TextField(blank=True)
    question_text = models.CharField(
        max_length=240,
        default="Would you go on a date with me?",
    )
    decline_message = models.CharField(
        max_length=240,
        blank=True,
        default="Maybe another time?",
    )

    theme = models.CharField(
        max_length=20,
        choices=Theme.choices,
        default=Theme.ELEGANT,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED,
        db_index=True,
    )

    show_welcome = models.BooleanField(default=True)
    show_personal_message = models.BooleanField(default=True)
    show_memories = models.BooleanField(default=False)
    allow_multiple_activities = models.BooleanField(default=False)
    greeting = models.CharField(max_length=80, blank=True, default="")
    unlock_code = models.CharField(max_length=16, blank=True)
    unlock_hint = models.CharField(
        max_length=240,
        blank=True,
        default="Пароль это дата нашего первого свидания",
    )
    finale_note_type = models.CharField(
        max_length=16,
        default="letter",
        choices=[
            ("letter", "Letter"),
            ("review", "Review"),
            ("none", "None"),
        ],
    )

    music = models.FileField(upload_to=invitation_music_upload, blank=True, null=True)
    spotify_url = models.CharField(max_length=400, blank=True)
    music_start_sec = models.PositiveIntegerField(default=0)
    music_end_sec = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.recipient_name} ← {self.sender_name} ({self.public_token})"

    @property
    def is_terminal(self) -> bool:
        return self.status in {self.Status.DECLINED, self.Status.CONFIRMED}

    def mark_opened(self) -> None:
        if self.opened_at is None:
            self.opened_at = timezone.now()
        if self.status == self.Status.CREATED:
            self.status = self.Status.OPENED
        self.save(update_fields=["opened_at", "status", "updated_at"])


class InvitationPhoto(models.Model):
    invitation = models.ForeignKey(
        Invitation,
        related_name="photos",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(upload_to=invitation_photo_upload)
    caption = models.CharField(max_length=160, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"Photo {self.order} for {self.invitation.public_token}"


class MemoryCard(models.Model):
    invitation = models.ForeignKey(
        Invitation,
        related_name="memories",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=240, blank=True)
    image = models.ImageField(upload_to=memory_image_upload, blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title


class ActivityOption(models.Model):
    invitation = models.ForeignKey(
        Invitation,
        related_name="activities",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=80)
    icon = models.CharField(max_length=16, blank=True)
    enabled = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.name


class AvailableDate(models.Model):
    invitation = models.ForeignKey(
        Invitation,
        related_name="available_dates",
        on_delete=models.CASCADE,
    )
    date = models.DateField()

    class Meta:
        ordering = ["date"]
        constraints = [
            models.UniqueConstraint(
                fields=["invitation", "date"],
                name="unique_invitation_date",
            )
        ]

    def __str__(self) -> str:
        return str(self.date)


class AvailableTime(models.Model):
    invitation = models.ForeignKey(
        Invitation,
        related_name="available_times",
        on_delete=models.CASCADE,
    )
    date = models.ForeignKey(
        AvailableDate,
        related_name="times",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    time = models.TimeField()

    class Meta:
        ordering = ["time", "id"]

    def __str__(self) -> str:
        return str(self.time)


class RecipientResponse(models.Model):
    class Answer(models.TextChoices):
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"

    invitation = models.OneToOneField(
        Invitation,
        related_name="response",
        on_delete=models.CASCADE,
    )
    answer = models.CharField(max_length=16, choices=Answer.choices)
    selected_activities = models.ManyToManyField(
        ActivityOption,
        related_name="responses",
        blank=True,
    )
    selected_date = models.ForeignKey(
        AvailableDate,
        related_name="responses",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    selected_time = models.TimeField(null=True, blank=True)
    decline_reason = models.CharField(max_length=400, blank=True)
    finale_note = models.TextField(blank=True)
    finale_note_kind = models.CharField(
        max_length=16,
        default="text",
        choices=[
            ("text", "Text"),
            ("voice", "Voice"),
            ("video", "Video"),
        ],
    )
    finale_note_media = models.FileField(upload_to=finale_note_upload, blank=True, null=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.invitation.public_token}: {self.answer}"


def guest_reply_upload(instance, filename: str) -> str:
    suffix = Path(filename).suffix.lower()[:8] or ".webm"
    key = getattr(instance, "session_key", "reply")[:32]
    return f"replies/{key}/{uuid.uuid4().hex}{suffix}"


class GuestReply(models.Model):
    session_key = models.CharField(max_length=64, unique=True)
    source = models.CharField(max_length=16, default="demo")
    public_token = models.CharField(max_length=32, blank=True)
    recipient_name = models.CharField(max_length=120, blank=True)
    sender_name = models.CharField(max_length=120, blank=True)
    answer = models.CharField(max_length=16, blank=True)
    activities = models.JSONField(default=list, blank=True)
    selected_date = models.CharField(max_length=32, blank=True)
    selected_time = models.CharField(max_length=16, blank=True)
    finale_note = models.TextField(blank=True)
    finale_note_kind = models.CharField(max_length=16, blank=True)
    media = models.FileField(upload_to=guest_reply_upload, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"{self.recipient_name or 'guest'} · {self.selected_date or self.answer}"
