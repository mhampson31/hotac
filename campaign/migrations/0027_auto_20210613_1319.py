# Generated by Django 3.2.4 on 2021-06-13 13:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xwtools', '0004_auto_20210613_1255'),
        ('campaign', '0026_auto_20210613_1255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aimaneuver',
            name='roll_1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roll_1', to='xwtools.dialmaneuver'),
        ),
        migrations.AlterField(
            model_name='aimaneuver',
            name='roll_2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roll_2', to='xwtools.dialmaneuver'),
        ),
        migrations.AlterField(
            model_name='aimaneuver',
            name='roll_3',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roll_3', to='xwtools.dialmaneuver'),
        ),
        migrations.AlterField(
            model_name='aimaneuver',
            name='roll_4',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roll_4', to='xwtools.dialmaneuver'),
        ),
        migrations.AlterField(
            model_name='aimaneuver',
            name='roll_5',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roll_5', to='xwtools.dialmaneuver'),
        ),
        migrations.AlterField(
            model_name='aimaneuver',
            name='roll_6',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roll_6', to='xwtools.dialmaneuver'),
        ),
    ]
