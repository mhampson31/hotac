# Generated by Django 3.2.4 on 2021-06-11 18:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0021_aipriority'),
    ]

    operations = [
        migrations.AddField(
            model_name='aipriority',
            name='ai',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='priorities', to='campaign.ai'),
            preserve_default=False,
        ),
    ]