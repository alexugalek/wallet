from django import forms
from django.core.exceptions import ValidationError

from .models import FinancialExpenses, AccountSettings, Bills
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

    def clean_expense_value(self):
        cd = self.cleaned_data
        if not cd['expense_value'].amount:
            raise forms.ValidationError("We don't accept 0 value")
        return cd['expense_value']


class EditExpenseForm(LoginRequiredMixin, forms.ModelForm):

    class Meta:
        model = FinancialExpenses
        fields = ['expense_value', 'subcategory', 'comment', 'created']
        widgets = {
            'comment': forms.TextInput,
            'created': forms.DateInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean_expense_value(self):
        cd = self.cleaned_data
        if not cd['expense_value'].amount:
            raise forms.ValidationError("We don't accept 0 value")
        return cd['expense_value']


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


class AddBill(forms.ModelForm):
    class Meta:
        model = Bills
        fields = ['bill_photo']

    # Add some custom validation to our image field
    def clean_bill_photo(self):
        image = self.cleaned_data.get('bill_photo', False)
        if image:
            if image.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 10mb )")
            return image
        else:
            raise forms.ValidationError("Couldn't read uploaded image")
