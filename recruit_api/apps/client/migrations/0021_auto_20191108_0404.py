# Generated by Django 2.0.5 on 2019-11-08 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0020_add_extra_fields_contact'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='client',
            options={'ordering': ['-created', 'name'], 'verbose_name_plural': 'Clients'},
        ),
        migrations.AddField(
            model_name='client',
            name='status',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
