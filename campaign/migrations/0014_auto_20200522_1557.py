# Generated by Django 3.0.6 on 2020-05-22 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0013_auto_20200522_1508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='long_desc',
            field=models.CharField(max_length=120),
        ),
    ]