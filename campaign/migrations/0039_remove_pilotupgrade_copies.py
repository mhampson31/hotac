# Generated by Django 3.2.4 on 2021-06-25 21:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0038_alter_ally_abilities'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pilotupgrade',
            name='copies',
        ),
    ]