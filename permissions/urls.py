from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.WalletLoginView.as_view(), name='login'),
    path('registration/', views.RegistrationLoginView.as_view(), name='registration'),
    path('logout/', views.WalletLogoutView.as_view(), name='logout'),

]
