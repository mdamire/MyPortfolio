from django.urls import path

from .views import homeView, AboutView

urlpatterns = [
    path('', homeView, name='home'),
    path('about/', AboutView.as_view(), name='about'),
]