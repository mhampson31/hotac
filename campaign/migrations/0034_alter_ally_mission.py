# Generated by Django 3.2.4 on 2021-06-23 21:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0033_rename_init_ally_initiative'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ally',
            name='mission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='allies', to='campaign.mission'),
        ),
    ]
