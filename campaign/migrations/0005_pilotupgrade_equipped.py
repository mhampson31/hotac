# Generated by Django 3.0.6 on 2020-06-11 01:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0004_auto_20200610_2057'),
    ]

    operations = [
        migrations.AddField(
            model_name='pilotupgrade',
            name='equipped',
            field=models.BooleanField(default=False),
        ),
    ]
