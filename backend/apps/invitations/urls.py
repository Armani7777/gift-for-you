from django.urls import path

from .views import (
    GuestReplyView,
    InvitationConfirmView,
    InvitationCreateView,
    InvitationManageView,
    InvitationMemoryUploadView,
    InvitationMusicUploadView,
    InvitationNoteView,
    InvitationOpenView,
    InvitationPhotoUploadView,
    InvitationPlanView,
    InvitationPublicView,
    InvitationResponseView,
)

urlpatterns = [
    path("replies/", GuestReplyView.as_view(), name="guest-replies"),
    path("invitations/", InvitationCreateView.as_view(), name="invitation-create"),
    path("invitations/<str:public_token>/", InvitationPublicView.as_view(), name="invitation-public"),
    path("invitations/<str:public_token>/open/", InvitationOpenView.as_view(), name="invitation-open"),
    path(
        "invitations/<str:public_token>/response/",
        InvitationResponseView.as_view(),
        name="invitation-response",
    ),
    path("invitations/<str:public_token>/plan/", InvitationPlanView.as_view(), name="invitation-plan"),
    path(
        "invitations/<str:public_token>/confirm/",
        InvitationConfirmView.as_view(),
        name="invitation-confirm",
    ),
    path("invitations/<str:public_token>/note/", InvitationNoteView.as_view(), name="invitation-note"),
    path(
        "manage/<str:public_token>/<str:management_token>/",
        InvitationManageView.as_view(),
        name="invitation-manage",
    ),
    path(
        "manage/<str:public_token>/<str:management_token>/photos/",
        InvitationPhotoUploadView.as_view(),
        name="invitation-photos",
    ),
    path(
        "manage/<str:public_token>/<str:management_token>/memories/",
        InvitationMemoryUploadView.as_view(),
        name="invitation-memories",
    ),
    path(
        "manage/<str:public_token>/<str:management_token>/music/",
        InvitationMusicUploadView.as_view(),
        name="invitation-music",
    ),
]
