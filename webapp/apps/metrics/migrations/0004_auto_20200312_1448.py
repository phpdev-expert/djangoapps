# Generated by Django 2.2 on 2020-03-12 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metrics', '0003_auto_20200312_1444'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='token_secret',
            field=models.TextField(blank=True, null=True),
        ),
    ]