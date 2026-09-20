from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resume', '0002_candidate_languages_candidate_projects'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='certifications',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='candidate',
            name='awards',
            field=models.JSONField(default=list),
        ),
    ]
