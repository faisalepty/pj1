# Generated by Django 5.1.6 on 2025-03-08 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_additionaltask'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='image_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
