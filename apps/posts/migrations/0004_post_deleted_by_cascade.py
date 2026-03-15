from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0003_remove_post_unique_post_title_per_user_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="deleted_by_cascade",
            field=models.BooleanField(default=False),
        ),
    ]
