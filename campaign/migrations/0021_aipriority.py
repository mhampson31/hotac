# Generated by Django 3.2.4 on 2021-06-11 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0020_enemypilot_name_override'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIPriority',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('T', 'Target'), ('A', 'Action')], max_length=1)),
                ('step', models.PositiveSmallIntegerField(default=1)),
                ('desc', models.CharField(max_length=25)),
            ],
            options={
                'verbose_name_plural': 'AI Priorities',
                'ordering': ['-type', 'step'],
            },
        ),
    ]
