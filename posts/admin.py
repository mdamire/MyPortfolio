import re

from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from tinymce.widgets import TinyMCE
from django.urls import reverse
from django.utils.html import format_html

from common.static import get_css_full_list
from .models import PostDetail, PostTag


def publish_post(modeladmin, request, queryset):
    for obj in queryset:
        obj.is_published = True
        if not obj.publish_date:
            obj.publish_date = timezone.now()
        obj.save()


class PostDetailForm(forms.ModelForm):
    class Meta:
        fields = (
            'permalink', 'heading', 'tags', 'feature', 'introduction', 'content', 'requires_rendering', 
            'include_sublinks', 'is_published', 'publish_date'
        )
        widgets = {
            'introduction': TinyMCE(mce_attrs={'content_css': get_css_full_list(), 'height': 300}),
            'content': TinyMCE(
                mce_attrs={
                    'content_css': get_css_full_list(['posts/post-detail.css', 'posts/prism-tn.css'])
                }
            ),
        }
    
    def clean_permalink(self):
        permalink = self.cleaned_data['permalink']
        if not re.match('^[A-Za-z][-A-Za-z0-9_]*$', permalink):
            raise ValidationError("Invalid Value")
        
        return permalink


@admin.register(PostDetail)
class PostDetailAdmin(admin.ModelAdmin):
    list_display = ('permalink', 'heading', 'is_published', 'publish_date', 'feature', 'created', 'view_count', '_url')
    form = PostDetailForm
    readonly_fields = ('_url', )

    actions=(publish_post,)

    def _url(self, obj):
        try:
            url = reverse('post-detail', kwargs={'permalink': obj.permalink})
            return format_html(f'<a href="{url}" target="_blank">{url}</a>')
        except:
            return


@admin.register(PostTag)
class PostTagAdmin(admin.ModelAdmin):
    list_display = ('label', 'color', 'bg_color')
