# Generated by Django 2.2.1 on 2019-06-01 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0003_pilot_total_xp'),
    ]

    operations = [
        migrations.AddField(
            model_name='pilot',
            name='upgrades',
            field=models.ManyToManyField(to='campaign.Upgrade'),
        ),
    ]
