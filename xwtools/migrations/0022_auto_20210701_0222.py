# Generated by Django 3.2.4 on 2021-07-01 02:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xwtools', '0021_auto_20210630_1424'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PilotCard2',
        ),
        migrations.CreateModel(
            name='PilotCard',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('xwtools.card',),
        ),
        migrations.CreateModel(
            name='ShipAbility',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('xwtools.card',),
        ),
        migrations.AlterModelOptions(
            name='oldpilotcard',
            options={'ordering': ['type', '-type2', 'name']},
        ),
        migrations.AlterModelOptions(
            name='upgrade',
            options={'ordering': ['type', '-type2', 'name']},
        ),
        migrations.RemoveField(
            model_name='attack',
            name='requires',
        ),
        migrations.AddField(
            model_name='chassis',
            name='new_ability',
            field=models.OneToOneField(blank=True, limit_choices_to={'type': 'SHP'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='xwtools.upgrade'),
        ),
        migrations.AlterField(
            model_name='attack',
            name='arc',
            field=models.CharField(choices=[('F', 'Front Arc'), ('R', 'Rear Arc'), ('T', 'Single Turret Arc'), ('TT', 'Double Turret Arc'), ('FF', 'Full Front Arc'), ('RR', 'Full Rear Arc'), ('B', 'Bullseye Arc'), ('SL', 'Left Arc'), ('SR', 'Right Arc')], default='F', max_length=2),
        ),
        migrations.AlterField(
            model_name='chassis',
            name='ability',
            field=models.OneToOneField(blank=True, limit_choices_to={'type': 'SHP'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ship', to='xwtools.upgrade'),
        ),
        migrations.AlterField(
            model_name='chassis',
            name='attack2_arc',
            field=models.CharField(blank=True, choices=[('F', 'Front Arc'), ('R', 'Rear Arc'), ('T', 'Single Turret Arc'), ('TT', 'Double Turret Arc'), ('FF', 'Full Front Arc'), ('RR', 'Full Rear Arc'), ('B', 'Bullseye Arc'), ('SL', 'Left Arc'), ('SR', 'Right Arc')], max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='chassis',
            name='attack_arc',
            field=models.CharField(choices=[('F', 'Front Arc'), ('R', 'Rear Arc'), ('T', 'Single Turret Arc'), ('TT', 'Double Turret Arc'), ('FF', 'Full Front Arc'), ('RR', 'Full Rear Arc'), ('B', 'Bullseye Arc'), ('SL', 'Left Arc'), ('SR', 'Right Arc')], default='F', max_length=2),
        ),
    ]