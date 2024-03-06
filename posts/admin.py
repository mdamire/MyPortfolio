import re

from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from tinymce.widgets import TinyMCE

from common.static import get_css_full_list
from .models import PostDetail


class PostDetailForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields["introduction"].widget = TinyMCE(mce_attrs={'content_css': get_css_full_list()})
    
    class Meta:
        fields = (
            'permalink', 'heading', 'introduction', 'content', 'requires_rendering', 'is_published', 'publish_date'
        )
        widgets = {
            'introduction': TinyMCE(mce_attrs={'content_css': get_css_full_list(), 'height': 300}),
            'content': TinyMCE(mce_attrs={'content_css': get_css_full_list()}),
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