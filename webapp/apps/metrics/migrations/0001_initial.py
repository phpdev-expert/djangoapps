# Generated by Django 2.2 on 2020-03-06 08:30

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('user_id', models.CharField(blank=True, max_length=255, null=True)),
                ('page_id', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('facebook', 'facebook'), ('instagram', 'instagram'), ('linkedin', 'linkedin'), ('twitter', 'twitter')], max_length=20)),
                ('name', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('active', 'active'), ('inactive', 'inactive'), ('suspended', 'suspended')], max_length=20)),
                ('token', models.TextField(blank=True)),
                ('token_secret', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True)),
                ('last_synced', models.DateTimeField(blank=True, null=True)),
                ('sync_status', models.CharField(choices=[('pending', 'pending'), ('ok', 'ok'), ('failed', 'failed')], default='pending', max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AccountObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('object_id', models.CharField(max_length=255)),
                ('object_type', models.CharField(choices=[('page', 'page'), ('post', 'post'), ('video', 'video'), ('message', 'message')], max_length=10)),
                ('title', models.TextField(blank=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('date_posted', models.DateTimeField(null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metrics.Account')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Metrics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('metric', models.CharField(max_length=255)),
                ('slug', models.CharField(max_length=255)),
                ('platform', models.CharField(choices=[('facebook', 'facebook'), ('instagram', 'instagram'), ('linkedin', 'linkedin'), ('twitter', 'twitter')], max_length=20)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TwitterReply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('reply_id', models.CharField(max_length=255)),
                ('is_quote_status', models.CharField(blank=True, choices=[('true', 'true'), ('false', 'false')], max_length=10, null=True)),
                ('retweeted', models.CharField(blank=True, choices=[('true', 'true'), ('false', 'false')], max_length=10, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('date_posted', models.DateTimeField(null=True)),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='metrics.Account')),
                ('object_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='metrics.AccountObject')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TwitterMention',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('mention_id', models.CharField(max_length=255)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metrics.Account')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AccountMetrics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('date', models.DateTimeField(null=True)),
                ('value_type', models.CharField(choices=[('int', 'int'), ('float', 'float'), ('str', 'str'), ('dict', 'dict'), ('json', 'json')], max_length=255)),
                ('value', models.TextField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metrics.Account')),
                ('metrics', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metrics.Metrics')),
                ('object_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='metrics.AccountObject')),
                ('reply', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='metrics.TwitterReply')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
