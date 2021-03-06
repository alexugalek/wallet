# Generated by Django 3.0.5 on 2020-04-21 07:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('finance', '0015_accountsettings_updated'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='financialexpenses',
            name='slug',
        ),
        migrations.RemoveField(
            model_name='financialexpenses',
            name='telegram_id',
        ),
        migrations.AlterField(
            model_name='accountsettings',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='finance.Categories'),
        ),
        migrations.AlterField(
            model_name='accountsettings',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='financialexpenses',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='financialexpenses',
            name='subcategory',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='finance.SubCategories'),
        ),
        migrations.AlterUniqueTogether(
            name='accountsettings',
            unique_together={('user', 'category')},
        ),
    ]
