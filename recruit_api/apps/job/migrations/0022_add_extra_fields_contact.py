# Generated by Django 2.2.6 on 2019-11-05 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0021_auto_20191105_0339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='long_description_public',
            field=models.BooleanField(blank=True, default=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='short_description_public',
            field=models.BooleanField(blank=True, default=True),
        ),
    ]
