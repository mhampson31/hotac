# Generated by Django 3.2.4 on 2021-07-06 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0051_alter_campaign_exclude_random'),
    ]

    operations = [
        migrations.AddField(
            model_name='mission',
            name='ground_assault',
            field=models.BooleanField(default=False),
        ),
    ]