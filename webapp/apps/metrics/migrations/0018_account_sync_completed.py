# Generated by Django 2.2 on 2020-05-08 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metrics', '0017_auto_20200508_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='sync_completed',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
