# Generated by Django 3.0.6 on 2020-05-22 15:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xwtools', '0010_auto_20200522_0108'),
        ('campaign', '0012_auto_20200522_0108'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CampaignShip',
            new_name='Squadron',
        ),
        migrations.RemoveField(
            model_name='pilotship',
            name='ship',
        ),
        migrations.AddField(
            model_name='pilotship',
            name='chassis',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='xwtools.Chassis'),
        ),
    ]
