from .models import PostDetail
from common.static import SiteStatic


def get_related_posts(post: PostDetail, limit: int = 5) -> list[PostDetail]:
    """Get related posts based on shared tags, excluding the current post."""
    all_related_posts = PostDetail.objects.filter(tags__in=post.tags.all()).exclude(
        id=post.id
    )

    related_posts = []
    related_post_ids = set()
    for related_post in all_related_posts:
        if related_post.id not in related_post_ids:
            related_posts.append(related_post)
            related_post_ids.add(related_post.id)
            if len(related_posts) == limit:
                break

    return related_posts
