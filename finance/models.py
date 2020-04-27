from django.db import models
from djmoney.models.fields import MoneyField
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from wallet.settings import TODAY_IS

# Create your models here.


def get_default(model):
    return model.objects.first()


class Categories(models.Model):
    name = models.CharField(max_length=100, default=None, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name or 'Unknown'


class SubCategories(models.Model):

    name = models.CharField(max_length=100, default=None, null=True, blank=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"

    def __str__(self):
        return '{}: {}'.format(self.category.name, self.name) or 'Unknown'


class FinancialExpenses(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expense_value = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', default=0, currency_choices=(('USD', 'USD'), ))
    subcategory = models.ForeignKey(SubCategories, on_delete=models.CASCADE, null=True)
    comment = models.TextField(max_length=100, blank=True, default=None, null=True)
    publish = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Financial expense"
        verbose_name_plural = "Financial expenses"

    def __str__(self):
        return '{} expenses {} in {} category in {}'.format(self.user.username, self.expense_value, self.subcategory.category, self.publish)

    def get_absolute_url_update_record(self):
        return reverse('finance:update',
                       args=[
                           self.user.id,
                           self.id,
                       ])

    def get_absolute_url_delete_record(self):
        return reverse('finance:delete',
                       args=[
                           self.user.id,
                           self.id,
                       ])


class AccountSettings(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True, blank=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, null=True, blank=True)
    limit_value = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', default=100, currency_choices=(('USD', 'USD'),))
    report = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Account settings"
        verbose_name_plural = "Accounts settings"

        unique_together = (
            'user',
            'category',
        )

    def get_absolute_url_settings(self):
        return reverse('finance:settings-detail',
                       args=[self.id, self.user.id])


class TelegramCredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.IntegerField(default=None, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
