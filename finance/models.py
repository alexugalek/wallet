from PIL import Image
from django.db import models
from djmoney.models.fields import MoneyField
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

# Create your models here.


def get_default_subcategory():
    return SubCategories.objects.first()


def get_default_category():
    return Categories.objects.first()


class Categories(models.Model):
    name = models.CharField(max_length=100, unique=True, default=None, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class SubCategories(models.Model):

    name = models.CharField(max_length=100, default=None, null=True, blank=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, default=get_default_category)

    class Meta:
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"

    def __str__(self):
        return '{}: {}'.format(self.category.name, self.name) or 'Unknown'


class FinancialExpenses(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expense_value = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', currency_choices=(('USD', 'USD'), ))
    subcategory = models.ForeignKey(SubCategories, on_delete=models.CASCADE, null=True, default=get_default_subcategory)
    comment = models.TextField(max_length=100, blank=True, default=None, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(default=timezone.now)
    publish = models.DateTimeField(auto_now_add=True)

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
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, null=True, blank=True, default=get_default_category)
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
                       args=[self.user.id, self.id])


class TelegramCredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.IntegerField(default=None, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)


class Bills(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bill_photo = models.ImageField(upload_to='all-bills/%Y/%m/%d/', blank=True)
    created = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Bill"
        verbose_name_plural = "Bills"

    def __str__(self):
        return '{}: {}'.format(self.user.username, self.id)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        if not self.bill_photo:
            return

        super().save()
        image = Image.open(self.bill_photo)
        (width, height) = image.size
        factor = height/width
        if width >= height:
            max_width = width if width < 1200 else 1200
            max_height = max_width * factor
        else:
            max_height = height if height < 1200 else 1200
            max_width = max_height / factor
        size = (int(max_width), int(max_height))
        image = image.resize(size, Image.ANTIALIAS)
        image.save(self.bill_photo.path)
