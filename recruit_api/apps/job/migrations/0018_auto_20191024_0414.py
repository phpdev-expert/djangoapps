# Generated by Django 2.0.5 on 2019-10-24 04:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0017_auto_20191024_0119'),
    ]

    operations = [
        migrations.RenameField(
            model_name='hiringphone',
            old_name='email',
            new_name='phone',
        ),
        migrations.RenameField(
            model_name='hiringtitle',
            old_name='email',
            new_name='title',
        ),
        migrations.AlterField(
            model_name='job',
            name='recruiter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
