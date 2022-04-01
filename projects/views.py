from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.http import Http404

from .models import ProjectPosts

# Create your views here.
def projectView(request):
    template_name = "projects/projects.html"
    post_list = ProjectPosts.objects.filter(
            parent__isnull = True
        ).order_by(
            '-update_date'
        )
    return render(request, template_name, {
            "page_heading": 'Projects',
            "post_list": post_list,
        })

    
def projectPostDetailView(request, title):
    post = get_object_or_404(ProjectPosts, url_param=title)
    if post.is_parent:
        try:
            child = ProjectPosts.objects.filter(
                    parent = post    
                ).order_by(
                    'serial'
                )
        except ProjectPosts.DoesNotExist:
            raise Http404("Page not found")
        
        return render(request, "projects/projects.html", {
            "page_heading": post.title,
            "post_list": child,
        })

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