# Generated by Django 5.1.6 on 2025-03-05 16:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0002_alter_appointment_staff_alter_appointment_status'),
        ('services', '0002_additionaltask'),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('additional_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='services.additionaltask')),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_assignments', to='appointments.appointment')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='services.service')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='staff.staff')),
            ],
        ),
    ]
