# Generated by Django 3.0.5 on 2020-04-17 10:59

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0003_auto_20200417_1102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountsettings',
            name='category',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='finance.Categories'),
            preserve_default=False,
        ),
    ]
