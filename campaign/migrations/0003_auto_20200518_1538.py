# Generated by Django 3.0.6 on 2020-05-18 15:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0002_auto_20200518_1511'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dialmaneuver',
            old_name='move',
            new_name='bearing',
        ),
    ]
