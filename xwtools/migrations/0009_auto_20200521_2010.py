# Generated by Django 3.0.6 on 2020-05-21 20:10

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('xwtools', '0008_auto_20200521_1253'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dialmaneuver',
            options={'ordering': ['-speed', django.db.models.expressions.CombinedExpression(django.db.models.expressions.Case(django.db.models.expressions.When(bearing='XX', then=django.db.models.expressions.Value(1)), django.db.models.expressions.When(bearing='S', then=django.db.models.expressions.Value(2)), django.db.models.expressions.When(bearing='B', then=django.db.models.expressions.Value(3)), django.db.models.expressions.When(bearing='T', then=django.db.models.expressions.Value(4)), django.db.models.expressions.When(bearing='TR', then=django.db.models.expressions.Value(5)), django.db.models.expressions.When(bearing='SL', then=django.db.models.expressions.Value(6)), django.db.models.expressions.When(bearing='KT', then=django.db.models.expressions.Value(8)), output_field=models.SmallIntegerField()), '*', django.db.models.expressions.Case(django.db.models.expressions.When(direction='L', then=django.db.models.expressions.Value(-1)), default=django.db.models.expressions.Value(1), output_field=models.SmallIntegerField()))]},
        ),
    ]
