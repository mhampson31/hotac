# Generated by Django 3.2.4 on 2021-06-10 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0015_sessionpilot_initiative'),
    ]

    operations = [
        migrations.AddField(
            model_name='mission',
            name='bonus_1',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mission',
            name='bonus_2',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mission',
            name='objective',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mission',
            name='penalty',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='session',
            name='bonus_1_achieved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='session',
            name='bonus_2_achieved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='session',
            name='penalty_received',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sessionpilot',
            name='bonus',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='sessionpilot',
            name='penalty',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='aimaneuver',
            name='range',
            field=models.CharField(choices=[('1', 'R1/R2 Closing'), ('2', 'R3/R2 Fleeing'), ('3', 'R4+'), ('4', 'Stressed'), ('5', 'Hyperspace')], max_length=1),
        ),
    ]
