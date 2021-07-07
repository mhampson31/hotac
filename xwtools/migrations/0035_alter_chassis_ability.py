# Generated by Django 3.2.4 on 2021-07-06 22:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xwtools', '0034_auto_20210706_2203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chassis',
            name='ability',
            field=models.ForeignKey(blank=True, limit_choices_to={'type': 'SHP'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ship', to='xwtools.card'),
        ),
    ]
