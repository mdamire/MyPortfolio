from django.urls import path

from .views import ProjectView

app_name = "projects"
urlpatterns = [
    path('', ProjectView.as_view(), name='projects'),
]