# Generated by Django 2.0.5 on 2020-01-31 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidate', '0052_auto_20200128_0426'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='invoice_no',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='candidate',
            name='paid',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]