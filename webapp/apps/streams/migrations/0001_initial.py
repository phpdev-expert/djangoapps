# Generated by Django 2.2 on 2020-09-03 10:51

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Modified at')),
                ('name', models.CharField(default='New Board', max_length=256)),
                ('user_id', models.PositiveIntegerField(db_index=True, max_length=255)),
                ('streams_position', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(blank=True), default=list, size=None)),
                ('archived_at', models.DateTimeField(blank=True, default=None, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
