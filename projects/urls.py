from django.urls import path

from .views import ProjectPostListView, projectPostDetailView

app_name = "projects"
urlpatterns = [
    path('<str:title>', projectPostDetailView, name='details'),
    path('', ProjectPostListView.as_view(), name='projects'),
]
