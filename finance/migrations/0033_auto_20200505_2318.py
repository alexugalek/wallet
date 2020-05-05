# Generated by Django 3.0.5 on 2020-05-05 20:18

from django.db import migrations
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0032_auto_20200505_1031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialexpenses',
            name='expense_value',
            field=djmoney.models.fields.MoneyField(currency_choices=(('USD', 'USD'),), decimal_places=2, default_currency='USD', max_digits=14),
        ),
    ]
