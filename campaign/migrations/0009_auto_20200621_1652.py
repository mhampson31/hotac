# Generated by Django 3.0.6 on 2020-06-21 16:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xwtools', '0002_auto_20200610_2143'),
        ('campaign', '0008_auto_20200621_1641'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PlayerShip',
            new_name='PlayableShip',
        ),
    ]
