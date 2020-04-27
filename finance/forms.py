from django import forms
from .models import FinancialExpenses, AccountSettings
from django.contrib.auth.mixins import LoginRequiredMixin


class ExpenseAddForm(LoginRequiredMixin, forms.ModelForm):
    class Meta:
        model = FinancialExpenses
        fields = ['expense_value', 'subcategory', 'comment']
        widgets = {
            'comment': forms.TextInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class AccountSettingsForm(LoginRequiredMixin, forms.ModelForm):
    class Meta:
        model = AccountSettings

        fields = ['limit_value', 'report']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class SendEmailForm(forms.Form):
    pk = forms.IntegerField()
    year = forms.IntegerField()
    month = forms.IntegerField()
