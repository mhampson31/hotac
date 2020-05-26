# Generated by Django 3.0.6 on 2020-05-23 21:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xwtools', '0016_auto_20200523_2146'),
    ]

    operations = [
        migrations.CreateModel(
            name='Faction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.RemoveField(
            model_name='dial',
            name='hyperdrive',
        ),
        migrations.AddField(
            model_name='chassis',
            name='hyperdrive',
            field=models.BooleanField(default=True),
        ),
    ]