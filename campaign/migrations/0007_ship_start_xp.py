# Generated by Django 2.2.1 on 2019-06-03 02:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0006_remove_upgrade_ability'),
    ]

    operations = [
        migrations.AddField(
            model_name='ship',
            name='start_xp',
            field=models.PositiveSmallIntegerField(default=10),
            preserve_default=False,
        ),
    ]
