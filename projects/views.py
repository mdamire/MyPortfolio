from django.shortcuts import render
from django.views.generic import ListView

from .models import ProjectPosts

# Create your views here.
class ProjectView(ListView):
    template_name = "projects/projects.html"
    context_object_name = 'post_list'

    def get_queryset(self):
        return ProjectPosts.objects.filter(parent__isnull = True)
    
