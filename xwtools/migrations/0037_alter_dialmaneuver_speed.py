# Generated by Django 3.2.4 on 2021-07-06 23:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xwtools', '0036_auto_20210706_2344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dialmaneuver',
            name='speed',
            field=models.SmallIntegerField(),
        ),
    ]
