# Generated by Django 3.2.4 on 2021-07-05 03:52

import campaign.models.campaigns
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xwtools', '0033_alter_card_options'),
        ('campaign', '0049_auto_20210705_0018'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='exclude_random',
            field=models.ManyToManyField(to='xwtools.Chassis'),
        ),
    ]
