# Generated by Django 2.0.5 on 2019-05-14 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidate', '0008_auto_20190514_1318'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='linkedin_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]