# Generated by Django 5.1.6 on 2025-02-15 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('barber', 'Barber'), ('masseuse', 'Masseuse')], max_length=50)),
                ('availability', models.JSONField(default=dict)),
                ('commission_rate', models.DecimalField(decimal_places=2, default=0.1, max_digits=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
