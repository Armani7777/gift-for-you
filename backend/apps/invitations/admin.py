from django.contrib import admin

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


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("recipient_name", "sender_name", "status", "theme", "public_token", "created_at")
    search_fields = ("recipient_name", "sender_name", "public_token")
    readonly_fields = ("public_token", "management_token", "created_at", "updated_at")


admin.site.register(InvitationPhoto)
admin.site.register(MemoryCard)
admin.site.register(ActivityOption)
admin.site.register(AvailableDate)
admin.site.register(AvailableTime)
admin.site.register(RecipientResponse)


@admin.register(GuestReply)
class GuestReplyAdmin(admin.ModelAdmin):
    list_display = ("recipient_name", "selected_date", "selected_time", "finale_note_kind", "updated_at")
    search_fields = ("recipient_name", "sender_name", "finale_note")
    readonly_fields = ("session_key", "created_at", "updated_at")
