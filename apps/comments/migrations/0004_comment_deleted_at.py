from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("comments", "0003_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="deleted_at",
            field=models.DateTimeField(blank=True, db_index=True, default=None, null=True),
        ),
    ]
