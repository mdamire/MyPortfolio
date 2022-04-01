from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from .models import ProjectPosts

# Create your views here.
class ProjectView(ListView):
    template_name = "projects/projects.html"
    context_object_name = 'post_list'

    def get_queryset(self):
        return ProjectPosts.objects.filter(
                parent__isnull = True
            ).order_by(
                '-update_date'
            )
    
def ProjectPostDetailView(request, title):
    post = get_object_or_404(ProjectPosts, url_param=title)
    group_posts = ProjectPosts.objects.filter(
            parent=post.parent
        ).order_by(
            'serial'
        )
    template_name = 'projects/details.html'
    context = {
        'post': post,
        'group': group_posts,
    }
    return render(request, template_name, context)