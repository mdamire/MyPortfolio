from pydantic import BaseModel
from posts.models import PostDetail, PostTag, PostAsset
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


class PostAssetResponse(BaseModel):
    """Response model for PostAsset."""

    id: int
    post_id: int
    key: str
    file: str
    description: str


class PostListResponse(BaseModel):
    """Response model for list of posts."""

    post_list: list


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
