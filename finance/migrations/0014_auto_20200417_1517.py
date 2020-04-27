# Generated by Django 3.0.5 on 2020-04-17 12:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0013_accountsettings_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountsettings',
            name='category',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='finance.Categories'),
        ),
    ]
