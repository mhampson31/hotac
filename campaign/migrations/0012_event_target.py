# Generated by Django 3.0.6 on 2020-05-30 14:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0011_auto_20200529_2053'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='target',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='campaign.SessionEnemy'),
        ),
    ]
