# Generated by Django 2.2.5 on 2019-10-02 04:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0012_job_recruiter'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisaStatusRates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('third_party_bill_rate', models.CharField(blank=True, default='1.18', max_length=255, null=True)),
                ('visa_1099_bill_rate', models.CharField(blank=True, default='1.15', max_length=255, null=True)),
                ('citizen_bill_rate', models.CharField(blank=True, default='1.18', max_length=255, null=True)),
                ('green_card_bill_rate', models.CharField(blank=True, default='1.18', max_length=255, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='job',
            options={'ordering': ['-created', 'title'], 'verbose_name_plural': 'Jobs'},
        ),
        migrations.RemoveField(
            model_name='job',
            name='citizen_bill_rate',
        ),
        migrations.RemoveField(
            model_name='job',
            name='green_card_bill_rate',
        ),
        migrations.RemoveField(
            model_name='job',
            name='third_party_bill_rate',
        ),
        migrations.RemoveField(
            model_name='job',
            name='visa_1099_bill_rate',
        ),
        migrations.AlterField(
            model_name='job',
            name='recruiter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]
