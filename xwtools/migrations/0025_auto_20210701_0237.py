# Generated by Django 3.2.4 on 2021-07-01 02:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xwtools', '0024_remove_chassis_ability'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chassis',
            name='new_ability',
        ),
        migrations.AddField(
            model_name='chassis',
            name='ability',
            field=models.OneToOneField(blank=True, limit_choices_to={'type': 'SHP'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ship', to='xwtools.card'),
        ),
    ]
