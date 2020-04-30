from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'permissions'

urlpatterns = [
    path('accounts/login/', views.WalletLoginView.as_view(), name='login'),
    path('registration/', views.RegistrationLoginView.as_view(), name='registration'),
    path('logout/', views.WalletLogoutView.as_view(), name='logout'),
    path('password_reset/', views.PasswordResetViewCustom.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmViewCustom.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('edit/', views.edit_info, name='edit'),

]
