# Generated by Django 3.0.6 on 2020-05-29 18:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0007_sessionenemy_elite'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sessionenemy',
            name='elite',
        ),
    ]