# Generated by Django 2.2.3 on 2019-08-19 01:05

import django.core.validators
from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import recruit_api.apps.client.models.client


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0014_auto_20190810_0036'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='created',
            field=model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created'),
        ),
        migrations.AddField(
            model_name='contact',
            name='modified',
            field=model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified'),
        ),
        migrations.AddField(
            model_name='contact',
            name='notes',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='founded_year',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), recruit_api.apps.client.models.client.RecruitMinLengthValidator(4)]),
        ),
        migrations.AlterField(
            model_name='client',
            name='location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='website',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]