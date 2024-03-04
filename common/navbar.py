from pages.models import HomePageSection
from django.urls import reverse


class NavbarItem():

    def __init__(self, title, url):
        self.title = title
        self.url = url


NAVBAR_ITEMS_CONTEXT_KEY = 'navbar_items'


def get_navbar_items(is_homepage):
    haburl = '' if is_homepage else reverse('home')
    items = [
        NavbarItem(title=hs.navbar_title, url= haburl + '#' + hs.navbar_title) 
        for hs in HomePageSection.objects.filter(navbar_title__isnull=False)
    ]

    return items


def get_navbar_context(is_homepage):
    nc = {NAVBAR_ITEMS_CONTEXT_KEY: get_navbar_items(is_homepage)}

    return nc
