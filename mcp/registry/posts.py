from typing import Optional, List, Tuple
from django.core.files.base import ContentFile

from mcp_serializer.features.tool.result import ToolsResult

from posts.models import PostDetail, PostTag
from common.models import SiteAsset
from mcp_serializer.features.prompt.result import PromptsResult
from ..schema import (
    PostDetailResponse,
    PostListResponse,
    _post_to_response,
)
from .registry import registry


## Tools
# posts
@registry.tool()
def create_post(
    permalink: str,
    heading: str,
    content: str,
    tags: List[Tuple[str, str, str]],
    introduction: Optional[str] = None,
    include_sublinks: bool = False,
    css_file_content: Optional[str] = None,
    js_file_content: Optional[str] = None,
) -> str:
    """Create a new blog post.

    Creates a new post as a draft with optional custom CSS and JavaScript files.

    Args:
        permalink: Unique URL-friendly identifier (letters, numbers, underscores only).
        heading: Post title (max 200 characters).
        content: Main HTML content (supports Django templates).
        tags: List of tuples [(label, text_color, bg_color)]. At least one required.
        introduction: Brief summary for post list page.
        include_sublinks: Auto-generate table of contents from headers (default: True).
        css_file_content: Custom CSS content for this post.
        js_file_content: Custom JavaScript content for this post.
    """
    if PostDetail.objects.filter(permalink=permalink).exists():
        result = ToolsResult(is_error=True)
        result.add_text_content(f"Post with permalink '{permalink}' already exists")
        return result

    post = PostDetail.objects.create(
        permalink=permalink,
        heading=heading,
        content=content,
        introduction=introduction,
        requires_rendering=True,
        is_published=False,
        include_sublinks=include_sublinks,
    )

    # Handle tags
    tag_objects = []
    for tag_label, color, bg_color in tags:
        label_lower = tag_label.lower()
        tag, created = PostTag.objects.get_or_create(
            label=label_lower, defaults={"color": color, "bg_color": bg_color}
        )
        if not created and (tag.color != color or tag.bg_color != bg_color):
            tag.color = color
            tag.bg_color = bg_color
            tag.save()
        tag_objects.append(tag)
    post.tags.set(tag_objects)

    # Handle CSS file
    if css_file_content:
        css_file = ContentFile(
            css_file_content.encode("utf-8"), name=f"{permalink}.css"
        )
        SiteAsset.objects.create(
            post=post,
            key=f"css_{permalink}",
            file=css_file,
            description="Custom CSS for this post",
            is_static=True,
            is_active=True,
        )

    # Handle JS file
    if js_file_content:
        js_file = ContentFile(js_file_content.encode("utf-8"), name=f"{permalink}.js")
        SiteAsset.objects.create(
            post=post,
            key=f"js_{permalink}",
            file=js_file,
            description="Custom JavaScript for this post",
            is_static=True,
            is_active=True,
        )

    return f"Post with permalink {post.permalink} created successfully."


@registry.tool()
def get_post(permalink: str) -> PostDetailResponse:
    """Retrieve a specific blog post.

    Fetches post details and associated CSS/JS assets as embedded resources.

    Args:
        permalink: The unique permalink of the post.
    """
    result = ToolsResult()
    try:
        post = PostDetail.objects.get(permalink=permalink)
    except PostDetail.DoesNotExist:
        result = ToolsResult(is_error=True)
        result.add_text_content(f"Post with permalink '{permalink}' does not exist")
        return result

    result.add_structured_content(_post_to_response(post))

    # Add CSS and JS assets as embedded files
    assets = SiteAsset.objects.filter(post=post)
    for asset in assets:
        result.add_file(file=asset.file, title=asset.description or asset.key)
    return result


@registry.tool()
def list_posts(
    is_published: Optional[bool] = None,
    tag_id: Optional[int] = None,
    limit: Optional[int] = None,
) -> PostListResponse:
    """List blog posts with optional filtering.

    Lists all the available blog posts, with options to filter by publication status
    and tags, and to limit the number of results.

    Args:
        is_published: Filter by publication status (True/False/None for all).
        tag_id: Filter by specific tag ID.
        limit: Maximum number of posts to return.
    """
    queryset = PostDetail.objects.all()

    if is_published is not None:
        queryset = queryset.filter(is_published=is_published)

    if tag_id is not None:
        queryset = queryset.filter(tags__id=tag_id)

    if limit:
        queryset = queryset[:limit]

    return PostListResponse(post_list=[_post_to_response(post) for post in queryset])


@registry.tool()
def update_post(
    permalink: str,
    new_permalink: Optional[str] = None,
    heading: Optional[str] = None,
    content: Optional[str] = None,
    introduction: Optional[str] = None,
    include_sublinks: Optional[bool] = None,
    tags: Optional[List[Tuple[str, str, str]]] = None,
    css_file_content: Optional[str] = None,
    js_file_content: Optional[str] = None,
) -> str:
    """Update an existing blog post.

    Updates post fields and/or CSS/JS assets. Only provided fields are updated.

    Args:
        permalink: Current permalink of the post.
        new_permalink: New permalink.
        heading: New title.
        content: New HTML content.
        introduction: New summary.
        include_sublinks: Toggle sublink generation.
        tags: New list of tuples [(label, text_color, bg_color)].
        css_file_content: Updated CSS content (replaces existing).
        js_file_content: Updated JS content (replaces existing).
    """
    from django.core.files.base import ContentFile

    post = PostDetail.objects.get(permalink=permalink)

    if new_permalink is not None:
        post.permalink = new_permalink
    if heading is not None:
        post.heading = heading
    if content is not None:
        post.content = content
    if introduction is not None:
        post.introduction = introduction
    if include_sublinks is not None:
        post.include_sublinks = include_sublinks

    post.save()

    # Handle tags update
    if tags is not None:
        tag_objects = []
        for tag_label, color, bg_color in tags:
            label_lower = tag_label.lower()
            tag, created = PostTag.objects.get_or_create(
                label=label_lower, defaults={"color": color, "bg_color": bg_color}
            )
            if not created and (tag.color != color or tag.bg_color != bg_color):
                tag.color = color
                tag.bg_color = bg_color
                tag.save()
            tag_objects.append(tag)
        post.tags.set(tag_objects)

    # Handle CSS file update
    if css_file_content is not None:
        # Delete existing CSS asset
        SiteAsset.objects.filter(post=post, key="custom_css").delete()
        # Create new one
        css_file = ContentFile(
            css_file_content.encode("utf-8"), name=f"{post.permalink}.css"
        )
        SiteAsset.objects.create(
            post=post,
            key="custom_css",
            file=css_file,
            description="Custom CSS for this post",
        )

    # Handle JS file update
    if js_file_content is not None:
        # Delete existing JS asset
        SiteAsset.objects.filter(post=post, key="custom_js").delete()
        # Create new one
        js_file = ContentFile(
            js_file_content.encode("utf-8"), name=f"{post.permalink}.js"
        )
        SiteAsset.objects.create(
            post=post,
            key="custom_js",
            file=js_file,
            description="Custom JavaScript for this post",
        )

    return f"Post with permalink {post.permalink} updated successfully."


## Prompts
@registry.prompt()
def post_create_prompt():
    """Create a blog post"""
    existing_tags = PostTag.objects.all()
    existing_tags_info = []
    for tag in existing_tags:
        existing_tags_info.append(f'("{tag.label}", "{tag.color}", "{tag.bg_color}")')

    existing_tags_str = (
        ", ".join(existing_tags_info) if existing_tags_info else "(none yet)"
    )

    result = PromptsResult()
    result.add_text(
        role=PromptsResult.Roles.USER,
        text=f"""Create engaging blog posts with HTML content and Django template support.

**Required Fields:**
- **permalink**: Unique URL identifier (letters/numbers/underscores, e.g., "my-first-post")
  - Must be unique across all posts
  - Cannot be changed easily later, choose carefully
- **heading**: Post title (max 200 chars)
- **content**: HTML body with full Django template language support
  - Bootstrap 5 CSS and JavaScript are already loaded and available
  - Supports Django template syntax: variables, conditionals, loops, filters
  - All media files are available as context variables (see Media Files section below)
  - If media file is needed add it's reference like this: {{{{ filename_without_extension.url }}}} even before creating it.
- **tags**: At least 1 tag as list of tuples: [(label, text_color, bg_color)]
  - Existing tags: {existing_tags_str}
  - Labels are lowercase, single words for categorizing/filtering posts
  - Example: [("python", "#FFFFFF", "#3776AB"), ("tutorial", "#000000", "#FFC107")]

**Optional Fields:**
- **introduction**: Brief summary (2-3 sentences) shown on post list
- **include_sublinks**: Auto-generate table of contents (default: False). If the content has more than 500 words then set this to true. 
- **css_file_content**: Custom CSS for this post only (scoped to this post, won't affect other posts)
- **js_file_content**: Custom JavaScript for this post only (scoped to this post, won't affect other posts)

**Media Files:**
To add images or audio files to a post, use `create_media_file` tool after creating the post:
- Set content_type="post" and provide the post permalink
- Provide base64-encoded content for binary files (images, audio)
- Make sure the name has the correct extension (e.g., .jpg, .png, .mp3)
- Files are automatically available in Django templates as context variables
- Access in content using: {{{{ filename_without_extension.url }}}}
- Example: For "banner.jpg", use {{{{ banner.url }}}} in the content.
- Supported formats: images (jpg, png, gif, svg, etc.), audio (mp3, wav, etc.)

Posts are created as drafts (is_published=False). Base styling (post-detail.css) and scripts (post-detail.js) are automatically available.""",
    )
    return result


@registry.prompt()
def post_update_prompt():
    """Update an existing blog post"""
    existing_tags = PostTag.objects.all()
    existing_tags_info = []
    for tag in existing_tags:
        existing_tags_info.append(f'("{tag.label}", "{tag.color}", "{tag.bg_color}")')

    existing_tags_str = (
        ", ".join(existing_tags_info) if existing_tags_info else "(none yet)"
    )

    result = PromptsResult()
    result.add_text(
        role=PromptsResult.Roles.USER,
        text=f"""Update existing blog posts. Use `get_post` first to see current content.

**Updatable Fields (all optional):**
- **new_permalink**: Change URL identifier (must remain unique)
- **heading**: Update title
- **content**: Update HTML body (supports Django template language)
  - All media files are available as context variables: {{{{ filename.url }}}}
- **introduction**: Update summary
- **include_sublinks**: Toggle table of contents
- **tags**: Replace tags with new list [(label, text_color, bg_color)]
  - Existing tags: {existing_tags_str}
- **css_file_content**: Replace custom CSS (scoped to this post only)
- **js_file_content**: Replace custom JavaScript (scoped to this post only)

**Media Files:**
To update a media file, first delete it using `delete_media_file`, then create a new one with `create_media_file`.
- Delete: `delete_media_file(content_type="post", permalink=post_permalink, filename=filename)`
- Create: `create_media_file(content_type="post", permalink=post_permalink, filename=filename, file_content=base64_content)`

Only provided fields will be updated; others remain unchanged.""",
    )
    return result
