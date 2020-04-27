from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User
from .forms import AuthUserForm, RegistrationLoginForm


# Create your views here.


class WalletLoginView(LoginView):
    template_name = 'login.html'
    form_class = AuthUserForm

    def get_success_url(self):
        return reverse('finance:info', args=[self.request.user.id])


class RegistrationLoginView(CreateView):
    model = User
    template_name = 'registration.html'
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
        return reverse('finance:info', args=[self.object.id])


class WalletLogoutView(LogoutView):
    next_page = reverse_lazy('finance:home')
