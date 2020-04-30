# Generated by Django 3.0.5 on 2020-04-29 19:15

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0024_bills'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bills',
            options={'verbose_name': 'Bill', 'verbose_name_plural': 'Bills'},
        ),
        migrations.AddField(
            model_name='bills',
            name='created',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
