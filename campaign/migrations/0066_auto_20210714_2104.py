# Generated by Django 3.2.4 on 2021-07-14 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0065_fgsetup_enemy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessionpilot',
            name='assists',
            field=models.SmallIntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='sessionpilot',
            name='bonus',
            field=models.SmallIntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='sessionpilot',
            name='emplacements',
            field=models.SmallIntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='sessionpilot',
            name='guards',
            field=models.SmallIntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='sessionpilot',
            name='hits',
            field=models.SmallIntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='sessionpilot',
            name='penalty',
            field=models.SmallIntegerField(blank=True, default=0),
        ),
    ]
