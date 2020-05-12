from django.urls import path
from . import views

app_name = 'finance'
urlpatterns = [
    path('', views.home, name='home'),
    path('info/<int:pk>/<int:year_filter>-<str:month_filter>', views.ExpenseAddView.as_view(), name='info-detail'),
    path('info/<int:pk>/', views.ExpenseAddView.as_view(), name='info'),
    path('info/<int:pk>/detail/<str:date>/', views.DetailDayView.as_view(), name='detail'),
    path('info/<int:id>/update/<int:pk>/', views.DetailUpdateView.as_view(), name='update'),
    path('info/<int:id>/delete/<int:pk>/', views.DeleteDataView.as_view(), name='delete'),
    path('info/settings/<int:pk>/', views.SettingsCreateView.as_view(), name='settings'),
    path('info/settings/<int:id>/<int:pk>/', views.SettingsUpdateView.as_view(), name='settings-detail'),
    path('send-email/<int:pk>/', views.send_email, name='send-email'),
    path('add-bill/<int:pk>/', views.add_bill_photo, name='add-bill'),
]
