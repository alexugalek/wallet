# Generated by Django 3.0.5 on 2020-05-03 07:36

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('finance', '0026_auto_20200430_1751'),
    ]

    operations = [
        migrations.AddField(
            model_name='categories',
            name='user',
            field=models.ManyToManyField(through='finance.AccountSettings', to=settings.AUTH_USER_MODEL),
        ),
    ]