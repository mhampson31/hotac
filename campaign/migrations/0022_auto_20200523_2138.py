# Generated by Django 3.0.6 on 2020-05-23 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0021_auto_20200523_1739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aimaneuver',
            name='range',
            field=models.CharField(choices=[('1', 'R1/R2 Closing'), ('2', 'R3/R2 Fleeing'), ('3', 'R4+'), ('4', 'Stressed'), ('5', 'Fleeing')], max_length=1),
        ),
    ]