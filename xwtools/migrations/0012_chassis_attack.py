# Generated by Django 3.0.6 on 2020-05-22 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xwtools', '0011_auto_20200522_2018'),
    ]

    operations = [
        migrations.AddField(
            model_name='chassis',
            name='attack',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]