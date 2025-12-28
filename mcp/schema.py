from pydantic import BaseModel
from posts.models import PostDetail, PostTag
from pages.models import StaticPage
from common.models import SiteAsset
from typing import Optional


class PostDetailResponse(BaseModel):
    """Response model for PostDetail."""

    id: int
    permalink: str
    heading: str
    introduction: Optional[str]
    content: str
    is_published: bool
    publish_date: Optional[str]
    view_count: int
    include_sublinks: bool
    tags: list
    feature: int


class PageDetailResponse(BaseModel):
    """Response model for StaticPage."""

    id: int
    permalink: str
    heading: str
    content: str
    is_published: bool
    navbar_title: Optional[str]
    navbar_serial: int


class PostListResponse(BaseModel):
    """Response model for list of posts."""

    post_list: list


class PageListResponse(BaseModel):
    """Response model for list of pages."""

    page_list: list


class PostAssetListResponse(BaseModel):
    """Response model for list of post assets."""

    post_asset_list: list


# Helper Functions
def _post_to_response(post: PostDetail) -> PostDetailResponse:
    """Convert a PostDetail model instance to PostDetailResponse.

    Args:
        post: PostDetail model instance.
    """
    return PostDetailResponse(
        id=post.id,
        permalink=post.permalink,
        heading=post.heading,
        introduction=post.introduction or None,
        content=post.content,
        is_published=post.is_published,
        publish_date=str(post.publish_date) if post.publish_date else None,
        view_count=post.view_count,
        include_sublinks=post.include_sublinks,
        tags=list(post.tags.values_list("label", flat=True)),
        feature=post.feature,
    )


def _page_to_response(page: StaticPage) -> PageDetailResponse:
    """Convert a StaticPage model instance to PageDetailResponse.

    Args:
        page: StaticPage model instance.
    """
    return PageDetailResponse(
        id=page.id,
        permalink=page.permalink,
        heading=page.heading,
        content=page.content,
        is_published=page.is_published,
        navbar_title=page.navbar_title or None,
        navbar_serial=page.navbar_serial,
    )
