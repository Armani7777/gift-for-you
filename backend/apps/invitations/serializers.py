from __future__ import annotations

from rest_framework import serializers

from .models import (
    ActivityOption,
    AvailableDate,
    AvailableTime,
    GuestReply,
    Invitation,
    InvitationPhoto,
    MemoryCard,
    RecipientResponse,
)


class InvitationPhotoSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = InvitationPhoto
        fields = ("id", "url", "caption", "order")

    def get_url(self, obj: InvitationPhoto) -> str | None:
        if not obj.image:
            return None
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url


class MemoryCardSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = MemoryCard
        fields = ("id", "title", "description", "image_url", "order")

    def get_image_url(self, obj: MemoryCard) -> str | None:
        if not obj.image:
            return None
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url


class ActivityOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityOption
        fields = ("id", "name", "icon", "enabled", "order")


class AvailableDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableDate
        fields = ("id", "date")


class AvailableTimeSerializer(serializers.ModelSerializer):
    date_id = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta:
        model = AvailableTime
        fields = ("id", "date_id", "time")


class ActivityInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=80)
    icon = serializers.CharField(max_length=16, required=False, allow_blank=True)
    enabled = serializers.BooleanField(required=False, default=True)


class MemoryInputSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=80)
    description = serializers.CharField(max_length=240, required=False, allow_blank=True)


class TimeInputSerializer(serializers.Serializer):
    time = serializers.TimeField()
    date = serializers.DateField(required=False, allow_null=True)


class InvitationCreateSerializer(serializers.Serializer):
    sender_name = serializers.CharField(max_length=80)
    recipient_name = serializers.CharField(max_length=80)
    main_message = serializers.CharField(max_length=240)
    personal_message = serializers.CharField(required=False, allow_blank=True)
    question_text = serializers.CharField(max_length=240, required=False)
    decline_message = serializers.CharField(max_length=240, required=False, allow_blank=True)
    theme = serializers.ChoiceField(choices=Invitation.Theme.choices, required=False)
    show_welcome = serializers.BooleanField(required=False, default=True)
    show_personal_message = serializers.BooleanField(required=False, default=True)
    show_memories = serializers.BooleanField(required=False, default=False)
    allow_multiple_activities = serializers.BooleanField(required=False, default=False)
    greeting = serializers.CharField(max_length=80, required=False, allow_blank=True)
    unlock_code = serializers.CharField(max_length=16, required=False, allow_blank=True)
    unlock_hint = serializers.CharField(max_length=240, required=False, allow_blank=True)
    finale_note_type = serializers.ChoiceField(
        choices=["letter", "review", "none"],
        required=False,
    )
    spotify_url = serializers.CharField(max_length=400, required=False, allow_blank=True)
    music_start_sec = serializers.IntegerField(required=False, min_value=0)
    music_end_sec = serializers.IntegerField(required=False, min_value=0, allow_null=True)
    activities = ActivityInputSerializer(many=True, required=False)
    available_dates = serializers.ListField(child=serializers.DateField(), required=False)
    available_times = TimeInputSerializer(many=True, required=False)
    memories = MemoryInputSerializer(many=True, required=False)

    def validate_activities(self, value):
        if len(value) > 8:
            raise serializers.ValidationError("Please keep activity options to 8 or fewer.")
        return value

    def validate_available_dates(self, value):
        if len(value) > 30:
            raise serializers.ValidationError("Please choose fewer available dates.")
        return value

    def validate_memories(self, value):
        if len(value) > 5:
            raise serializers.ValidationError("You can add up to 5 memory cards.")
        return value


class RecipientResponsePublicSerializer(serializers.ModelSerializer):
    selected_activity_ids = serializers.PrimaryKeyRelatedField(
        source="selected_activities",
        many=True,
        read_only=True,
    )
    selected_date = serializers.SerializerMethodField()

    class Meta:
        model = RecipientResponse
        fields = (
            "answer",
            "selected_activity_ids",
            "selected_date",
            "selected_time",
            "decline_reason",
            "finale_note",
            "finale_note_kind",
            "confirmed_at",
        )

    def get_selected_date(self, obj: RecipientResponse):
        return obj.selected_date.date if obj.selected_date_id else None


class InvitationPublicSerializer(serializers.ModelSerializer):
    photos = InvitationPhotoSerializer(many=True, read_only=True)
    memories = MemoryCardSerializer(many=True, read_only=True)
    activities = serializers.SerializerMethodField()
    available_dates = AvailableDateSerializer(many=True, read_only=True)
    available_times = AvailableTimeSerializer(many=True, read_only=True)
    music_url = serializers.SerializerMethodField()
    has_music = serializers.SerializerMethodField()

    class Meta:
        model = Invitation
        fields = (
            "public_token",
            "sender_name",
            "recipient_name",
            "main_message",
            "personal_message",
            "question_text",
            "decline_message",
            "theme",
            "status",
            "show_welcome",
            "show_personal_message",
            "show_memories",
            "allow_multiple_activities",
            "photos",
            "memories",
            "activities",
            "available_dates",
            "available_times",
            "has_music",
            "music_url",
            "spotify_url",
            "music_start_sec",
            "music_end_sec",
            "greeting",
            "unlock_code",
            "unlock_hint",
            "finale_note_type",
        )

    def get_activities(self, obj: Invitation):
        items = [item for item in obj.activities.all() if item.enabled]
        return ActivityOptionSerializer(items, many=True).data

    def get_music_url(self, obj: Invitation) -> str | None:
        if not obj.music:
            return None
        request = self.context.get("request")
        url = obj.music.url
        return request.build_absolute_uri(url) if request else url

    def get_has_music(self, obj: Invitation) -> bool:
        return bool(obj.music or obj.spotify_url)


class InvitationCreatedSerializer(serializers.Serializer):
    public_token = serializers.CharField()
    management_token = serializers.CharField()
    status = serializers.CharField()


class RecipientResponseManageSerializer(serializers.ModelSerializer):
    selected_activities = ActivityOptionSerializer(many=True, read_only=True)
    selected_date = serializers.SerializerMethodField()

    def get_selected_date(self, obj: RecipientResponse):
        return obj.selected_date.date if obj.selected_date_id else None

    class Meta:
        model = RecipientResponse
        fields = (
            "answer",
            "selected_activities",
            "selected_date",
            "selected_time",
            "decline_reason",
            "finale_note",
            "finale_note_kind",
            "finale_note_media_url",
            "confirmed_at",
            "created_at",
            "updated_at",
        )

    finale_note_media_url = serializers.SerializerMethodField()

    def get_finale_note_media_url(self, obj: RecipientResponse) -> str | None:
        if not obj.finale_note_media:
            return None
        request = self.context.get("request")
        url = obj.finale_note_media.url
        return request.build_absolute_uri(url) if request else url


class InvitationManageSerializer(InvitationPublicSerializer):
    management_token = serializers.CharField()
    opened_at = serializers.DateTimeField(allow_null=True)
    responded_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()
    response = serializers.SerializerMethodField()
    activities = ActivityOptionSerializer(many=True, read_only=True)

    class Meta(InvitationPublicSerializer.Meta):
        fields = InvitationPublicSerializer.Meta.fields + (
            "management_token",
            "opened_at",
            "responded_at",
            "created_at",
            "response",
        )

    def get_response(self, obj: Invitation):
        if not hasattr(obj, "response"):
            return None
        return RecipientResponseManageSerializer(obj.response, context=self.context).data


class ResponseInputSerializer(serializers.Serializer):
    answer = serializers.ChoiceField(choices=RecipientResponse.Answer.choices)
    decline_reason = serializers.CharField(max_length=400, required=False, allow_blank=True)


class PlanInputSerializer(serializers.Serializer):
    activity_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    date_id = serializers.IntegerField(required=False, allow_null=True)
    date = serializers.DateField(required=False, allow_null=True)
    time = serializers.TimeField(required=False, allow_null=True)


class PhotoUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()
    caption = serializers.CharField(max_length=160, required=False, allow_blank=True)


class MemoryImageUploadSerializer(serializers.Serializer):
    memory_id = serializers.IntegerField()
    image = serializers.ImageField()


class MusicUploadSerializer(serializers.Serializer):
    music = serializers.FileField()


class GuestReplySerializer(serializers.ModelSerializer):
    media_url = serializers.SerializerMethodField()

    class Meta:
        model = GuestReply
        fields = (
            "id",
            "session_key",
            "source",
            "public_token",
            "recipient_name",
            "sender_name",
            "answer",
            "activities",
            "selected_date",
            "selected_time",
            "finale_note",
            "finale_note_kind",
            "media_url",
            "created_at",
            "updated_at",
        )

    def get_media_url(self, obj: GuestReply) -> str | None:
        if not obj.media:
            return None
        request = self.context.get("request")
        url = obj.media.url
        return request.build_absolute_uri(url) if request else url
