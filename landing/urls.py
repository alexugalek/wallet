from django.urls import path
from finance import views

app_name = 'landing'
urlpatterns = [
    path('', views.home, name='home'),
]
