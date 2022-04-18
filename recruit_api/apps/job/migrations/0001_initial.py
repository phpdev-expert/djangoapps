# Generated by Django 2.0.5 on 2019-05-10 15:16

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('client', '0001_initial'),
        ('category', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('employment_type', models.IntegerField(choices=[(1, 'Contract Job'), (2, 'Contract To Hire'), (3, 'Permanent Job')], default=1)),
                ('status', models.IntegerField(choices=[(1, 'Active'), (2, 'Draft')], default=1)),
                ('title', models.CharField(max_length=255)),
                ('location', models.CharField(max_length=255)),
                ('min_salary', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('max_salary', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('skills', models.CharField(blank=True, max_length=255, null=True)),
                ('short_description', models.CharField(max_length=150, validators=[django.core.validators.MinLengthValidator(5)])),
                ('long_description', models.TextField(validators=[django.core.validators.MinLengthValidator(10)])),
                ('publish_at', models.DateField(blank=True, null=True)),
                ('publish_until', models.DateField(blank=True, null=True)),
                ('short_description_public', models.BooleanField(default=True)),
                ('employment_type_public', models.BooleanField(default=True)),
                ('annual_pay_public', models.BooleanField(default=True)),
                ('long_description_public', models.BooleanField(default=True)),
                ('location_public', models.BooleanField(default=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='category.Category')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='client.Client')),
            ],
            options={
                'verbose_name_plural': 'Jobs',
            },
        ),
    ]
