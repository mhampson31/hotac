# Generated by Django 3.0.6 on 2020-05-19 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0005_auto_20200519_0031'),
    ]

    operations = [
        migrations.AddField(
            model_name='ship',
            name='slug',
            field=models.SlugField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='ship',
            name='name',
            field=models.CharField(max_length=40),
        ),
    ]