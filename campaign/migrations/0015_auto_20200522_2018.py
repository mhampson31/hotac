# Generated by Django 3.0.6 on 2020-05-22 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0014_auto_20200522_1557'),
    ]

    operations = [
        migrations.AddField(
            model_name='pilotship',
            name='hull_upgrades',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pilotship',
            name='shield_upgrades',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
