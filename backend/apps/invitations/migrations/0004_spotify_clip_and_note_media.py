from django.db import migrations, models
import apps.invitations.models


class Migration(migrations.Migration):
    dependencies = [
        ("invitations", "0003_invitation_finale_note_type_invitation_greeting_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="invitation",
            name="music_end_sec",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="invitation",
            name="music_start_sec",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="invitation",
            name="spotify_url",
            field=models.CharField(blank=True, max_length=400),
        ),
        migrations.AddField(
            model_name="recipientresponse",
            name="finale_note_kind",
            field=models.CharField(
                choices=[("text", "Text"), ("voice", "Voice"), ("video", "Video")],
                default="text",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="recipientresponse",
            name="finale_note_media",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=apps.invitations.models.finale_note_upload,
            ),
        ),
        migrations.AlterField(
            model_name="invitation",
            name="greeting",
            field=models.CharField(blank=True, default="", max_length=80),
        ),
        migrations.AlterField(
            model_name="invitation",
            name="unlock_hint",
            field=models.CharField(
                blank=True,
                default="Пароль это дата нашего первого свидания",
                max_length=240,
            ),
        ),
    ]
