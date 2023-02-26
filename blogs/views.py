from django.shortcuts import get_object_or_404, render

from basehome.utils import get_sidebar_section_links
from .models import BlogsPosts

# Create your views here.
def blogView(request):
    template_name = "blogs/list-page.html"
    post_list = BlogsPosts.objects.filter(
            is_published = True
        ).order_by(
            '-publish_date'
        )
    return render(request, template_name, {
            "page_heading": 'Blogs',
            "post_list": post_list,
        })

    
def blogPostDetailView(request, title):
    post = get_object_or_404(BlogsPosts, url_param=title)
    template_name = 'blogs/details.html'
    context = {
        'post': post,
    }

    context['sidebar'] = {}
    section_links = get_sidebar_section_links(post.body)
    if section_links:
        context['sidebar'][section_links[0]] = section_links[1]

    return render(request, template_name, context)
