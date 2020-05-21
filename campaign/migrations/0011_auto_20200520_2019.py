# Generated by Django 3.0.6 on 2020-05-20 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0010_auto_20200520_1153'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dialmaneuver',
            name='dial',
        ),
        migrations.RemoveField(
            model_name='ship',
            name='dial',
        ),
        migrations.RemoveField(
            model_name='slot',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='slot',
            name='ship',
        ),
        migrations.RemoveField(
            model_name='treeslot',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='treeslot',
            name='ship',
        ),
        migrations.DeleteModel(
            name='Upgrade',
        ),
        migrations.RemoveField(
            model_name='pilotship',
            name='unlocked',
        ),
        migrations.AddField(
            model_name='campaign',
            name='ship_initiative',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pilot',
            name='initiative',
            field=models.PositiveSmallIntegerField(default=2),
        ),
        migrations.AddField(
            model_name='pilotship',
            name='initiative',
            field=models.PositiveSmallIntegerField(default=2),
        ),
        migrations.DeleteModel(
            name='Dial',
        ),
        migrations.DeleteModel(
            name='DialManeuver',
        ),
        migrations.DeleteModel(
            name='Ship',
        ),
        migrations.DeleteModel(
            name='Slot',
        ),
        migrations.DeleteModel(
            name='TreeSlot',
        ),
    ]
