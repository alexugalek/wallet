# Generated by Django 3.0.5 on 2020-04-30 14:51

from django.db import migrations, models
import django.db.models.deletion
import finance.models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0025_auto_20200429_2215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountsettings',
            name='category',
            field=models.ForeignKey(blank=True, default=finance.models.get_default_category, null=True, on_delete=django.db.models.deletion.CASCADE, to='finance.Categories'),
        ),
        migrations.AlterField(
            model_name='financialexpenses',
            name='subcategory',
            field=models.ForeignKey(default=finance.models.get_default_subcategory, null=True, on_delete=django.db.models.deletion.CASCADE, to='finance.SubCategories'),
        ),
        migrations.AlterField(
            model_name='subcategories',
            name='category',
            field=models.ForeignKey(default=finance.models.get_default_category, on_delete=django.db.models.deletion.CASCADE, to='finance.Categories'),
        ),
    ]
