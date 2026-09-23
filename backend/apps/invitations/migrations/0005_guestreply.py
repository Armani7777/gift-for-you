from django.db import migrations, models
import apps.invitations.models


class Migration(migrations.Migration):
    dependencies = [
        ("invitations", "0004_spotify_clip_and_note_media"),
    ]

    operations = [
        migrations.CreateModel(
            name="GuestReply",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_key", models.CharField(max_length=64, unique=True)),
                ("source", models.CharField(default="demo", max_length=16)),
                ("public_token", models.CharField(blank=True, max_length=32)),
                ("recipient_name", models.CharField(blank=True, max_length=120)),
                ("sender_name", models.CharField(blank=True, max_length=120)),
                ("answer", models.CharField(blank=True, max_length=16)),
                ("activities", models.JSONField(blank=True, default=list)),
                ("selected_date", models.CharField(blank=True, max_length=32)),
                ("selected_time", models.CharField(blank=True, max_length=16)),
                ("finale_note", models.TextField(blank=True)),
                ("finale_note_kind", models.CharField(blank=True, max_length=16)),
                (
                    "media",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to=apps.invitations.models.guest_reply_upload,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-updated_at"],
            },
        ),
    ]
