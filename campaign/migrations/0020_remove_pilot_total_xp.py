# Generated by Django 3.0.6 on 2020-05-23 14:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0019_campaign_pool_xp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pilot',
            name='total_xp',
        ),
    ]