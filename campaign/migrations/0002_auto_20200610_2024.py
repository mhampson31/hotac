# Generated by Django 3.0.6 on 2020-06-10 20:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xwtools', '0001_initial'),
        ('campaign', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pilotupgrade',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='pilotupgrade',
            name='object_id',
        ),
        migrations.AddField(
            model_name='pilotupgrade',
            name='upgrade',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='xwtools.Upgrade'),
            preserve_default=False,
        ),
    ]