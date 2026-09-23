from __future__ import annotations

from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import HasManagementAccess, HasPublicInvitation
from .models import GuestReply
from .notify import notify_guest_reply
from .serializers import (
    GuestReplySerializer,
    InvitationCreatedSerializer,
    InvitationCreateSerializer,
    InvitationManageSerializer,
    InvitationPublicSerializer,
    MemoryImageUploadSerializer,
    MusicUploadSerializer,
    PhotoUploadSerializer,
    PlanInputSerializer,
    RecipientResponsePublicSerializer,
    ResponseInputSerializer,
)
from .services import (
    add_memory_image,
    add_photo,
    attach_music,
    confirm_plan,
    create_invitation,
    save_finale_note,
    save_plan,
    submit_response,
)
from .validators import validate_audio_file, validate_image_file, validate_note_media


class InvitationCreateView(APIView):
    def post(self, request):
        serializer = InvitationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invitation = create_invitation(serializer.validated_data)
        data = InvitationCreatedSerializer(invitation).data
        return Response(data, status=status.HTTP_201_CREATED)


class InvitationPublicView(APIView):
    permission_classes = [HasPublicInvitation]

    def get(self, request, public_token: str):
        serializer = InvitationPublicSerializer(self.invitation, context={"request": request})
        return Response(serializer.data)


class InvitationOpenView(APIView):
    permission_classes = [HasPublicInvitation]

    def post(self, request, public_token: str):
        self.invitation.mark_opened()
        serializer = InvitationPublicSerializer(self.invitation, context={"request": request})
        return Response(serializer.data)


class InvitationResponseView(APIView):
    permission_classes = [HasPublicInvitation]

    def post(self, request, public_token: str):
        serializer = ResponseInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = submit_response(
            self.invitation,
            serializer.validated_data["answer"],
            serializer.validated_data.get("decline_reason") or "",
        )
        return Response(RecipientResponsePublicSerializer(response).data, status=status.HTTP_201_CREATED)


class InvitationPlanView(APIView):
    permission_classes = [HasPublicInvitation]

    def post(self, request, public_token: str):
        serializer = PlanInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = save_plan(
            self.invitation,
            activity_ids=serializer.validated_data.get("activity_ids") or [],
            date_id=serializer.validated_data.get("date_id"),
            custom_date=serializer.validated_data.get("date"),
            selected_time=serializer.validated_data.get("time"),
        )
        return Response(RecipientResponsePublicSerializer(response).data)


class InvitationConfirmView(APIView):
    permission_classes = [HasPublicInvitation]

    def post(self, request, public_token: str):
        response = confirm_plan(self.invitation)
        return Response(RecipientResponsePublicSerializer(response).data)


class InvitationNoteView(APIView):
    permission_classes = [HasPublicInvitation]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request, public_token: str):
        text = str(request.data.get("text") or "").strip()
        kind = str(request.data.get("kind") or "text").strip()
        media = request.FILES.get("media")
        if not text and not media:
            return Response({"error": "Please write a few words first."}, status=status.HTTP_400_BAD_REQUEST)
        if media:
            validate_note_media(media)
        response = save_finale_note(self.invitation, text, kind, media)
        return Response(RecipientResponsePublicSerializer(response).data)


class InvitationManageView(APIView):
    permission_classes = [HasManagementAccess]

    def get(self, request, public_token: str, management_token: str):
        serializer = InvitationManageSerializer(self.invitation, context={"request": request})
        return Response(serializer.data)


class InvitationPhotoUploadView(APIView):
    permission_classes = [HasManagementAccess]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, public_token: str, management_token: str):
        serializer = PhotoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validate_image_file(serializer.validated_data["image"])
        photo = add_photo(
            self.invitation,
            serializer.validated_data["image"],
            serializer.validated_data.get("caption") or "",
        )
        invitation = InvitationManageSerializer(photo.invitation, context={"request": request})
        return Response(invitation.data, status=status.HTTP_201_CREATED)


class InvitationMemoryUploadView(APIView):
    permission_classes = [HasManagementAccess]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, public_token: str, management_token: str):
        serializer = MemoryImageUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validate_image_file(serializer.validated_data["image"])
        add_memory_image(
            self.invitation,
            serializer.validated_data["memory_id"],
            serializer.validated_data["image"],
        )
        data = InvitationManageSerializer(self.invitation, context={"request": request}).data
        return Response(data, status=status.HTTP_201_CREATED)


class InvitationMusicUploadView(APIView):
    permission_classes = [HasManagementAccess]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, public_token: str, management_token: str):
        serializer = MusicUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validate_audio_file(serializer.validated_data["music"])
        attach_music(self.invitation, serializer.validated_data["music"])
        data = InvitationManageSerializer(self.invitation, context={"request": request}).data
        return Response(data)


def _csv_or_json_list(value) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    text = str(value).strip()
    if text.startswith("["):
        import json

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = []
        if isinstance(parsed, list):
            return [str(item) for item in parsed if str(item).strip()]
    return [part.strip() for part in text.split(",") if part.strip()]


class GuestReplyView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        replies = GuestReply.objects.all()[:50]
        return Response(GuestReplySerializer(replies, many=True, context={"request": request}).data)

    def post(self, request):
        session_key = str(request.data.get("session_key") or "").strip()
        if not session_key:
            return Response({"error": "Missing session."}, status=status.HTTP_400_BAD_REQUEST)
        media = request.FILES.get("media")
        if media:
            validate_note_media(media)
        reply, _created = GuestReply.objects.get_or_create(session_key=session_key[:64])
        fields = [
            "source",
            "public_token",
            "recipient_name",
            "sender_name",
            "answer",
            "selected_date",
            "selected_time",
            "finale_note",
            "finale_note_kind",
        ]
        for field in fields:
            value = request.data.get(field)
            if value not in (None, ""):
                setattr(reply, field, str(value)[: 2000 if field == "finale_note" else 120])
        activities = _csv_or_json_list(request.data.get("activities"))
        if activities:
            reply.activities = activities
        update = ["updated_at"]
        if media is not None:
            reply.media = media
            update.append("media")
        reply.save()
        notify_guest_reply(reply)
        return Response(GuestReplySerializer(reply, context={"request": request}).data, status=status.HTTP_201_CREATED)
