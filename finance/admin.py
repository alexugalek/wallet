from django.contrib import admin
from .models import FinancialExpenses
from .models import Categories, SubCategories, AccountSettings, TelegramCredentials, Bills

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


class BillsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Bills._meta.fields]
    list_filter = ['user__username']
    search_fields = ['user__username']

    class Meta:
        model = Bills


class CategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Categories._meta.fields]

    class Meta:
        model = Categories


admin.site.register(FinancialExpenses, FinancialExpensesAdmin)
admin.site.register(Categories, CategoryAdmin)
admin.site.register(SubCategories)
admin.site.register(AccountSettings, AccountSettingsAdmin)
admin.site.register(TelegramCredentials, TelegramCredentialsAdmin)
admin.site.register(Bills, BillsAdmin)
