from pages.models import HomePageSection, StaticPage
from django.urls import reverse


class NavbarItem():

    def __init__(self, title, url):
        self.title = title
        self.url = url


def get_navbar_items(is_homepage):
    # Add homepage items
    haburl = '' if is_homepage else reverse('home')
    items = [
        NavbarItem(title=hs.navbar_title, url=haburl + '#' + hs.navbar_title) 
        for hs in HomePageSection.objects.filter(navbar_title__isnull=False)
    ]

    # Add staticpage items
    items += [
        NavbarItem(title=sp.navbar_title, url=reverse('static-page', kwargs={'permalink': sp.permalink})) 
        for sp in 
        StaticPage.objects.filter(navbar_title__isnull=False, is_published=True).order_by('navbar_serial', 'created')
    ]

    # Add posts
    items.append(NavbarItem(title='posts', url=reverse('post-list')))

    return items
