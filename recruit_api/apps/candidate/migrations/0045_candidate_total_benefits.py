# Generated by Django 2.2.3 on 2019-08-20 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidate', '0044_contactemail_contactphone'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='total_benefits',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]