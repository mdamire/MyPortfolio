from typing import List

from django.templatetags.static import static

from .models import SiteAsset


class SiteStatic():

    def __init__(self, url: str) -> None:
        self.url = url
        if url.endswith('.css'):
            self.type = 'css'
        elif url.endswith('.js'):
            self.type = 'js'
        else:
            self.type = None


DEFAULT_CSS_FILES = [
    SiteStatic('https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css'),
    SiteStatic('https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js'),
    SiteStatic('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'),
    SiteStatic(static('common/css/default.css')),
]

CUSTOM_STYLE_KEY = 'style'
STATIC_LIST_CONTEXT_KEY = 'statics'


def get_custom_static_list():
    csl = [SiteStatic(sf.file.url) for sf in SiteAsset.objects.filter(key=CUSTOM_STYLE_KEY)]

    return csl


def get_static_full_list() -> List[SiteStatic]:
    sfl = DEFAULT_CSS_FILES + get_custom_static_list()

    return sfl


def get_css_full_list() -> List[str]:
    cfl = [ss.url for ss in get_static_full_list()]

    return cfl


def get_static_context() -> dict:
    sc = {STATIC_LIST_CONTEXT_KEY: get_static_full_list()}

    return sc
