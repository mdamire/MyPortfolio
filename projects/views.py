from typing import Dict, Any

from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import ListView

from .models import ProjectPosts
from .repository import get_project_parents, get_project_children_link_html

class ProjectPostListView(ListView):
    template_name = "projects/list-page.html"
    queryset = ProjectPosts.objects.filter(
        parent__isnull = True,
        is_published = True
    ).order_by('-publish_date')
    context_object_name = "post_list"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["page_heading"] = 'Projects'
        return context

    
def projectPostDetailView(request, title):
    post = get_object_or_404(ProjectPosts, url_param=title)
    template_name = 'projects/details.html'
    context = {
        'post': post,
    }

    # Children posts
    if hasattr(post, 'children') and post.children:
        context['child_posts_html'] = get_project_children_link_html(post)
    
    # Sibling posts
    sibling_posts = ProjectPosts.objects.filter(parent=post.parent).order_by('serial', 'publish_date')
    if not post.is_parent and sibling_posts.count() > 1:
        sidebar_list = []
        for post in sibling_posts:
            sidebar_list.append({
                'label': post.title,
                'url': reverse('projects:details', kwargs={"title": post.url_param})
            })
            
        context['sidebar'] = {
            'Related posts' : sidebar_list
        }

    # Parent Post
    if post.parent:
        context['parent_posts'] = get_project_parents(post)

    return render(request, template_name, context)
