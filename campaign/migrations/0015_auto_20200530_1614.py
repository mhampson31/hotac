# Generated by Django 3.0.6 on 2020-05-30 16:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0014_remove_event_target'),
    ]

    operations = [
        migrations.AlterField(
            model_name='achievement',
            name='target',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='campaign.SessionEnemy'),
        ),
        migrations.AlterField(
            model_name='event',
            name='xp',
            field=models.SmallIntegerField(default=1),
        ),
    ]