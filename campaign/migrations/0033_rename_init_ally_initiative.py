# Generated by Django 3.2.4 on 2021-06-23 21:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0032_ally'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ally',
            old_name='init',
            new_name='initiative',
        ),
    ]