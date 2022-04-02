from django.urls import path

from .views import blogView, blogPostDetailView

app_name = "blogs"
urlpatterns = [
    path('<str:title>', blogPostDetailView, name='details'),
    path('', blogView, name='blogs'),
]