from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView
from django.http import Http404

from .models import ProjectPosts

# Create your views here.
def projectView(request):
    template_name = "projects/list-page.html"
    post_list = ProjectPosts.objects.filter(
            parent__isnull = True,
            is_published = True
        ).order_by(
            '-publish_date'
        )
    return render(request, template_name, {
            "page_heading": 'Projects',
            "post_list": post_list,
        })

    
def projectPostDetailView(request, title):
    post = get_object_or_404(ProjectPosts, url_param=title)

    if post.is_parent:
        childrens = ProjectPosts.objects.filter(
                parent = post    
            )
        if childrens.count() < 1:
            raise Http404("No page for this post")
        
        child = childrens.order_by('serial')[0]
        return redirect(reverse('projects:details', kwargs={
                "title": child.url_param
            }))

    template_name = 'projects/details.html'
    context = {
        'post': post,
    }

    if post.is_child():
        group_posts = ProjectPosts.objects.filter(
                parent=post.parent
            ).order_by(
                'serial'
            )

        template_name = 'projects/details-sidebar.html'
        context['group'] = group_posts

    return render(request, template_name, context)