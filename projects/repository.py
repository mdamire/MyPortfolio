from django.urls import reverse

from .models import ProjectPosts


def get_project_parents(project_post:ProjectPosts):
    parent_list = []
    current_post = project_post
    while(current_post.parent):
        parent_list.append(current_post.parent)
        current_post = current_post.parent
    
    parent_list.reverse()
    return parent_list


def get_project_children_link_html(project_post:ProjectPosts, depth=0, title_prefix=''):
    """This will return a html string containing list of the child post links.
    It can travel to highest depth of children relationship.
    """
    full_html = ''
    children_posts = project_post.children.order_by('serial', 'publish_date')
    count = 0
    for child_post in children_posts:
        count += 1
        title_number = title_prefix + str(count) + '.'
        
        url = reverse(child_post.url_name, kwargs={'title':child_post.url_param})
        link_html = '<div class=pb-2>{}<a href={}>{}</a></div>\n'.format(
            '&nbsp' * depth * 4, url, title_number + ' ' + child_post.title.title()
        )
        full_html = full_html + link_html + get_project_children_link_html(
            child_post, depth=depth+1, title_prefix=title_number
        )

    return full_html
