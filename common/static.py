from typing import List

from django.conf import settings
from django.templatetags.static import static

from .models import SiteAsset


class SiteStatic:
    def __init__(self, url: str, gtype=None) -> None:
        if url.startswith("http://") or url.startswith("https://"):
            self.url = url
        elif url.startswith(settings.MEDIA_URL):
            self.url = url
        else:
            self.url = static(url)

        if gtype:
            self.type = gtype
        elif url.endswith(".css"):
            self.type = "css"
        elif url.endswith(".js"):
            self.type = "js"
        else:
            self.type = None

    def __str__(self):
        return self.url

    def __repr__(self):
        return f"SiteStatic(url={self.url}, type={self.type})"


DEFAULT_STATIC_FILES = [
    SiteStatic(
        "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
    ),
    SiteStatic(
        "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"
    ),
    SiteStatic(
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"
    ),
    SiteStatic("https://fonts.googleapis.com/css?family=Roboto", "css"),
    SiteStatic("common/common.css"),
    SiteStatic("common/common.js"),
]


def get_custom_static_list():
    try:
        csl = [
            SiteStatic(sf.file.url)
            for sf in SiteAsset.objects.filter(is_active=True, is_static=True)
        ]
        return csl
    except Exception:
        return []


def get_static_full_list(extras: list = []) -> List[SiteStatic]:
    ss_extra = [
        extra if isinstance(extra, SiteStatic) else SiteStatic(extra)
        for extra in list(extras)
    ]
    sfl = DEFAULT_STATIC_FILES + ss_extra + get_custom_static_list()
    sfl = [ss for ss in sfl if ss.type in ["css", "js"]]

    return sfl


def get_css_url_list(extras: list = []) -> List[str]:
    cfl = [ss.url for ss in get_static_full_list(extras) if ss.type == "css"]

    return cfl
