# Generated by Django 3.0.6 on 2020-05-30 18:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0018_ai_campaign'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sessionenemy',
            options={'ordering': ['flight_group', '-level']},
        ),
    ]