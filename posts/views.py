from operator import attrgetter

from django.views.generic import DetailView, ListView

from common.mixins import SiteContextMixin, SingleObjectContentRendererMixin, MultipleObjectContentRendererMixin
from common.static import SiteStatic
from .models import PostDetail
from .sublink import parse_sublinks


class PostDetailView(DetailView, SiteContextMixin, SingleObjectContentRendererMixin):
    model = PostDetail
    extra_statics = [SiteStatic('posts/post.css'), SiteStatic('posts/posts.js')]

    # The name of the field on the model that contains the slug. 
    slug_field = 'permalink'
    # The name of the URLConf keyword argument that contains the slug.
    slug_url_kwarg = 'permalink'

    context_object_name = 'post'
    template_name = 'posts/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = context[self.context_object_name]
        if obj.include_sublinks:
            content, sublinks = parse_sublinks(obj.content)
            obj.content = content
            context['sublinks'] = sublinks
        
        return context


class PostListView(ListView, SiteContextMixin, MultipleObjectContentRendererMixin):
    model = PostDetail
    template_name = 'posts/post-list.html'
    extra_statics = [SiteStatic('posts/post-list.css'), SiteStatic('posts/post-list.js')]
    context_object_name = 'post_list'
    paginate_by = 6
