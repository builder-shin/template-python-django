import django.db.models.functions.text
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0002_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="post",
            name="unique_post_title_per_user",
        ),
        migrations.AddField(
            model_name="post",
            name="deleted_at",
            field=models.DateTimeField(blank=True, db_index=True, default=None, null=True),
        ),
        migrations.AddConstraint(
            model_name="post",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("title"),
                models.F("user"),
                condition=models.Q(("deleted_at__isnull", True)),
                name="unique_post_title_per_user",
            ),
        ),
    ]
