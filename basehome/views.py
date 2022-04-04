from django.shortcuts import render
from django.views.generic import TemplateView
from itertools import chain
from operator import attrgetter

from projects.models import ProjectPosts
from blogs.models import BlogsPosts

# Create your views here.
def homeView(request):
    template_name = "basic/home.html"
    projects = ProjectPosts.objects.order_by('-update_date')[:5]
    blogs = BlogsPosts.objects.order_by('-update_date')[:5]

    post_list = sorted(
        chain(projects, blogs), 
        key=attrgetter('update_date'),
        reverse=True
    )[:5]

    return render(request, template_name, {
            "post_list": post_list,
        })


class AboutView(TemplateView):
    template_name = "basic/about.html"