from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, \
    PasswordResetConfirmView
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User
from .forms import AuthUserForm, RegistrationLoginForm, PasswordResetFormCustom, SetPasswordFormCustom


# Create your views here.


class WalletLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = AuthUserForm

    # def get_success_url(self):
    #     return reverse('finance:info', args=[self.request.user.id])


class RegistrationLoginView(CreateView):
    model = User
    template_name = 'registration/registration.html'
    form_class = RegistrationLoginForm

    def form_valid(self, form):
        form_valid = super().form_valid(form)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        auth_user = authenticate(username=username, password=password)
        login(self.request, auth_user)

        # user settings creation

        return form_valid

    def get_success_url(self):
        return reverse('finance:home')


class WalletLogoutView(LogoutView):
    next_page = reverse_lazy('finance:home')


class PasswordResetViewCustom(PasswordResetView):
    success_url = reverse_lazy('permissions:password_reset_done')
    form_class = PasswordResetFormCustom


class PasswordResetConfirmViewCustom(PasswordResetConfirmView):
    success_url = reverse_lazy('permissions:password_reset_complete')
    form_class = SetPasswordFormCustom
