# Generated by Django 2.0.5 on 2019-07-09 18:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0004_auto_20190704_1159'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='job',
            options={'ordering': ['title'], 'verbose_name_plural': 'Jobs'},
        ),
    ]
