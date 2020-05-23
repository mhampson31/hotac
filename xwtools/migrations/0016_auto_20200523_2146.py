# Generated by Django 3.0.6 on 2020-05-23 21:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xwtools', '0015_chassis_cloaking'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chassis',
            name='dial',
        ),
        migrations.AddField(
            model_name='dial',
            name='chassis',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='xwtools.Chassis'),
        ),
    ]
