# Generated by Django 3.0.5 on 2020-05-04 18:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0027_categories_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialexpenses',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 4, 18, 44, 54, 79180)),
        ),
    ]
