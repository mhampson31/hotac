# Generated by Django 3.2.4 on 2021-06-08 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0014_sessionenemy_callsign'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionpilot',
            name='initiative',
            field=models.PositiveSmallIntegerField(default=2),
        ),
    ]