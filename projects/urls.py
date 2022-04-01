from django.urls import path

from .views import projectView, projectPostDetailView

app_name = "projects"
urlpatterns = [
    path('<str:title>', projectPostDetailView, name='details'),
    path('', projectView, name='projects'),
]