# Generated by Django 3.2.4 on 2021-06-24 12:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xwtools', '0005_auto_20210624_1211'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chassis',
            name='dial',
        ),
        migrations.AddField(
            model_name='dial',
            name='chassis',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dial', to='xwtools.chassis'),
        ),
    ]
