# Generated by Django 3.0.5 on 2020-05-12 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0034_remove_categories_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categories',
            name='name',
            field=models.CharField(blank=True, default=None, max_length=100, null=True, unique=True),
        ),
    ]
