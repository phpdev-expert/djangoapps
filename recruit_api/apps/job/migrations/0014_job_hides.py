# Generated by Django 2.2.5 on 2019-10-05 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0013_auto_20191002_0455'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='hides',
            field=models.TextField(blank=True, null=True),
        ),
    ]
