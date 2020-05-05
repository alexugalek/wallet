from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, \
    SetPasswordForm
from django import forms
from django.contrib.auth.models import User
import re


class AuthUserForm(AuthenticationForm, forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class RegistrationLoginForm(forms.ModelForm):

    password = forms.CharField(label='Pass',
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password',
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']
        help_texts = {
            'username': None,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords mismatch')
        if len(cd['password']) < 5:
            raise forms.ValidationError('Please enter password with more than 4 symbols')
        return cd['password']

    def clean_username(self):
        cd = self.cleaned_data
        if not re.fullmatch(r'[0-9a-zA-Z_]*', cd['username']):
            raise forms.ValidationError('Your username should contains only latin symbols, numbers and underscore')
        return cd['username']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class PasswordResetFormCustom(PasswordResetForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class SetPasswordFormCustom(SetPasswordForm):

    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=None,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class EditInfo(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'email']
        help_texts = {
            'username': None,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
