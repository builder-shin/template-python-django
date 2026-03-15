from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("comments", "0004_comment_deleted_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="deleted_by_cascade",
            field=models.BooleanField(default=False),
        ),
    ]
