from django.contrib import admin
from .models import FinancialExpenses
from .models import Categories, SubCategories, AccountSettings, TelegramCredentials

# Register your models here.


class FinancialExpensesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in FinancialExpenses._meta.fields]
    list_filter = ['subcategory', 'created']
    search_fields = ['user__username']

    class Meta:
        model = FinancialExpenses


class AccountSettingsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in AccountSettings._meta.fields]
    list_filter = ['user__username']
    search_fields = ['user__username']

    class Meta:
        model = AccountSettings


class TelegramCredentialsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TelegramCredentials._meta.fields]
    list_filter = ['user__username']
    search_fields = ['user__username']

    class Meta:
        model = TelegramCredentials


admin.site.register(FinancialExpenses, FinancialExpensesAdmin)
admin.site.register(Categories)
admin.site.register(SubCategories)
admin.site.register(AccountSettings, AccountSettingsAdmin)
admin.site.register(TelegramCredentials, TelegramCredentialsAdmin)
