# Generated by Django 3.0.6 on 2020-06-12 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0006_auto_20200612_2231'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pilotupgrade',
            options={'ordering': ['upgrade__type', 'status']},
        ),
        migrations.AlterField(
            model_name='pilotupgrade',
            name='status',
            field=models.CharField(choices=[('E', 'Equipped'), ('U', 'Unequipped'), ('X', 'Lost')], default='E', max_length=1),
        ),
    ]