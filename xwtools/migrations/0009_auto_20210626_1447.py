# Generated by Django 3.2.4 on 2021-06-26 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xwtools', '0008_upgrade_repeat'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pilot',
            options={'verbose_name': 'Pilot Card'},
        ),
        migrations.AlterModelOptions(
            name='upgrade',
            options={'verbose_name': 'Upgrade Card'},
        ),
        migrations.AlterField(
            model_name='pilot',
            name='type',
            field=models.CharField(choices=[('TLN', 'Talent'), ('AST', 'Astromech'), ('CNN', 'Cannon'), ('CNF', 'Config'), ('CRW', 'Crew'), ('DVC', 'Device'), ('FRC', 'Force Power'), ('PLT', 'Pilot'), ('GNR', 'Gunner'), ('ILC', 'Illicit'), ('MSL', 'Missile'), ('MOD', 'Modification'), ('SNS', 'Sensor'), ('TAC', 'Tactical Relay'), ('TCH', 'Tech'), ('TRP', 'Torpedo'), ('TTL', 'Title'), ('TRT', 'Turret'), ('SHP', 'Ship'), ('COM', 'Command'), ('HRD', 'Hardpoint'), ('CRG', 'Cargo'), ('TEM', 'Team')], default='PLT', max_length=3),
        ),
        migrations.AlterField(
            model_name='upgrade',
            name='type',
            field=models.CharField(choices=[('TLN', 'Talent'), ('AST', 'Astromech'), ('CNN', 'Cannon'), ('CNF', 'Config'), ('CRW', 'Crew'), ('DVC', 'Device'), ('FRC', 'Force Power'), ('GNR', 'Gunner'), ('ILC', 'Illicit'), ('MSL', 'Missile'), ('MOD', 'Modification'), ('SNS', 'Sensor'), ('TAC', 'Tactical Relay'), ('TCH', 'Tech'), ('TRP', 'Torpedo'), ('TTL', 'Title'), ('TRT', 'Turret'), ('SHP', 'Ship'), ('COM', 'Command'), ('HRD', 'Hardpoint'), ('CRG', 'Cargo'), ('TEM', 'Team')], max_length=3),
        ),
    ]
