# Generated by Django 2.2.5 on 2019-10-21 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0015_job_priority'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='priority',
            field=models.IntegerField(choices=[(1, 'High'), (2, 'Low')], default=2),
        ),
    ]
