# Generated by Django 5.1.6 on 2025-02-27 16:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0001_initial'),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='staff',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.staff'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('completed', 'Completed'), ('transacted', 'Transacted'), ('cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
    ]
