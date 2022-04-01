from django.urls import path

from .views import ProjectView, ProjectPostDetailView

app_name = "projects"
urlpatterns = [
    path('<str:title>', ProjectPostDetailView, name='details'),
    path('', ProjectView.as_view(), name='projects'),
]