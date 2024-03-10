from pages.models import HomePageSection
from django.urls import reverse


class NavbarItem():

    def __init__(self, title, url):
        self.title = title
        self.url = url


def get_navbar_items(is_homepage):
    haburl = '' if is_homepage else reverse('home')
    items = [
        NavbarItem(title=hs.navbar_title, url=haburl + '#' + hs.navbar_title) 
        for hs in HomePageSection.objects.filter(navbar_title__isnull=False)
    ]

    items.append(NavbarItem(title='posts', url=reverse('post-list')))

    return items
