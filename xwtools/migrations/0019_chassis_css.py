# Generated by Django 3.0.6 on 2020-05-23 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xwtools', '0018_dial_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='chassis',
            name='css',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
    ]
