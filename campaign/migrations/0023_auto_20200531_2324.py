# Generated by Django 3.0.6 on 2020-05-31 23:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0022_auto_20200531_2015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='achievement',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='achievements', to='campaign.Session'),
        ),
    ]
