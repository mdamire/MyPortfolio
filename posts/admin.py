import re

from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from tinymce.widgets import TinyMCE
from django.templatetags.static import static

from common.static import get_css_full_list
from .models import PostDetail, PostTag


class PostDetailForm(forms.ModelForm):
    class Meta:
        fields = (
            'permalink', 'heading', 'tags', 'feature', 'introduction', 'content', 'requires_rendering', 
            'include_sublinks', 'is_published', 'publish_date'
        )
        widgets = {
            'introduction': TinyMCE(mce_attrs={'content_css': get_css_full_list(), 'height': 300}),
            'content': TinyMCE(mce_attrs={'content_css': get_css_full_list() + [static('posts/post-detail.css')]}),
        }
    
    def clean_permalink(self):
        permalink = self.cleaned_data['permalink']
        if not re.match('^[A-Za-z][-A-Za-z0-9_]*$', permalink):
            raise ValidationError("Invalid Value")
        
        return permalink


@admin.register(PostDetail)
class PostDetailAdmin(admin.ModelAdmin):
    list_display = ('permalink', 'heading', 'is_published', 'created')
    form = PostDetailForm


@admin.register(PostTag)
class PostTagAdmin(admin.ModelAdmin):
    list_display = ('label', 'color', 'bg_color')
