from operator import attrgetter

from django.views.generic import DetailView, ListView

from common.mixins import SiteContextMixin, SingleObjectContentRendererMixin, MultipleObjectContentRendererMixin
from .models import PostDetail, PostTag
from .sublink import parse_sublinks


class PostDetailView(DetailView, SiteContextMixin, SingleObjectContentRendererMixin):
    model = PostDetail
    extra_statics = ['posts/post-detail.css', 'posts/post-detail.js']

    # The name of the field on the model that contains the slug. 
    slug_field = 'permalink'
    # The name of the URLConf keyword argument that contains the slug.
    slug_url_kwarg = 'permalink'

    context_object_name = 'post'
    template_name = 'posts/post-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = context[self.context_object_name]
        if obj.include_sublinks:
            content, sublinks = parse_sublinks(obj.content)
            obj.content = content
            context['sublinks'] = sublinks
        
        context['related_posts'] = PostDetail.objects.filter(tags__in=obj.tags.all()).exclude(id=obj.id)[:5]
        
        return context


class PostListView(ListView, SiteContextMixin, MultipleObjectContentRendererMixin):
    model = PostDetail
    template_name = 'posts/post-list.html'
    extra_statics = ['posts/post-list.css', 'posts/post-list.js']
    context_object_name = 'post_list'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag_list'] = [
            {
                'label': pt.label, 
                'color': pt.color, 
                'bg_color': pt.bg_color, 
                'count': len(pt.postdetail_set.all())
            }
            for pt in PostTag.objects.prefetch_related(
                    'postdetail_set'
                ).filter(
                    postdetail__isnull=False
                ).distinct()
        ]
        context['sort_list'] = ['featured', 'latest', 'oldest']

        sort_param = self.request.GET.get('sort')
        if sort_param:
            context['sort_param'] = sort_param
        tags_param = self.request.GET.get('tags')
        if tags_param:
            context['tags_param'] = str(tags_param).split(',')

        return context
    
    def get_queryset(self):
        qs = super().get_queryset()

        tags_param = self.request.GET.get('tags')
        sort_param = self.request.GET.get('sort')

        if not any([tags_param, sort_param]):
            return qs
        
        order = ['-feature', '-publish_date', '-created']
        if sort_param == 'latest':
            order = ['-publish_date', '-created']
        if sort_param == 'oldest':
            order = ['publish_date', 'created']
        
        filters = {'tags__id__in': str(tags_param).split(',')} if tags_param else {}

        qs = qs.filter(**filters).order_by(*order)
        return qs

        