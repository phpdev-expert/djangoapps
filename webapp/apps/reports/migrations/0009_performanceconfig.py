# Generated by Django 2.1.7 on 2020-05-06 15:43

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("reports", "0008_auto_20200502_1642")]

    operations = [
        migrations.CreateModel(
            name="PerformanceConfig",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("date_updated", models.DateTimeField(auto_now=True)),
                ("user_id", models.CharField(max_length=20)),
                ("platform", models.CharField(max_length=20)),
                ("page_ids", django.contrib.postgres.fields.jsonb.JSONField()),
                ("slugs", django.contrib.postgres.fields.jsonb.JSONField()),
            ],
            options={"db_table": "report_performance_config"},
        )
    ]