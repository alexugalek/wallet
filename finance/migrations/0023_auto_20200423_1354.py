# Generated by Django 3.0.5 on 2020-04-23 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0022_auto_20200423_1345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialexpenses',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
