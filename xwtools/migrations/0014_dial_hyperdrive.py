# Generated by Django 3.0.6 on 2020-05-23 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xwtools', '0013_auto_20200522_2136'),
    ]

    operations = [
        migrations.AddField(
            model_name='dial',
            name='hyperdrive',
            field=models.BooleanField(default=True),
        ),
    ]
