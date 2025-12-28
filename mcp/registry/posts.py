from typing import Optional, List, Tuple
from django.conf import settings

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


## Resouces
base_dir = settings.BASE_DIR.parent
registry.add_file_resource(
    file=f"{base_dir}/posts/static/posts/post-detail.css",
    title="Base CSS for the post detail page",
    description=(
        "Core styling for post detail pages, ensuring consistency in appearance and "
        "user experience across all such pages. This is available for every post."
    ),
)

registry.add_file_resource(
    file=f"{base_dir}/posts/static/posts/post-detail.js",
    title="Base JavaScript for the post detail page",
    description=(
        "Core JavaScript for post detail pages, ensuring consistency in appearance and "
        "user experience across all such pages. This is available for every post."
    ),
)


## Tools
@registry.tool()
def create_post(
    permalink: str,
    heading: str,
    content: str,
    tags: List[Tuple[str, str, str]],
    introduction: Optional[str] = None,
    include_sublinks: bool = False,
) -> str:
    """Create a new blog post.

    Creates a new post as a draft. Use create_site_asset to add CSS, JS, images, or other files.

    Args:
        permalink: Unique URL-friendly identifier (letters, numbers, underscores only).
        heading: Post title (max 200 characters).
        content: Main HTML content (supports Django templates).
        tags: List of tuples [(label, text_color, bg_color)]. At least one required.
        introduction: Brief summary for post list page.
        include_sublinks: Auto-generate table of contents from headers (default: True).
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
) -> str:
    """Update an existing blog post.

    Updates post fields. Only provided fields are updated.
    Use create_site_asset and delete_site_asset to manage CSS, JS, images, and other files.

    Args:
        permalink: Current permalink of the post.
        new_permalink: New permalink.
        heading: New title.
        content: New HTML content.
        introduction: New summary.
        include_sublinks: Toggle sublink generation.
        tags: New list of tuples [(label, text_color, bg_color)].
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

**Adding Assets (CSS, JS, Images, JSON, etc.):**
Use the `create_site_asset` tool to add any type of file to your post:

**For CSS/JS Files (automatically linked):**
- These are automatically included when viewing the post
- Example: `create_site_asset(filename="custom.css", file_content=css_text, post_permalink="my-post")`
- Example: `create_site_asset(filename="custom.js", file_content=js_text, post_permalink="my-post")`

**For Images, JSON, and other files (available as template variables):**
- These are available in Django templates as context variables
- Access using: {{{{ filename_without_extension.url }}}}
- Example: For "banner.jpg", use {{{{ banner.url }}}} in the content
- Example: `create_site_asset(filename="banner.jpg", file_content=base64_encoded_image, post_permalink="my-post")`
- Example: `create_site_asset(filename="data.json", file_content=json_text, post_permalink="my-post")`

**File Content for Asset:**
- Binary files (images, audio): Provide base64-encoded content
- Text files (CSS, JS, JSON): Provide plain text content

Base styling (post-detail.css) and scripts (post-detail.js) are automatically available.""",
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
  - All assets are available as context variables: {{{{ filename_without_extension.url }}}}
- **introduction**: Update summary
- **include_sublinks**: Toggle table of contents
- **tags**: Replace tags with new list [(label, text_color, bg_color)]
  - Existing tags: {existing_tags_str}

**Managing Assets:**
Use `create_site_asset` and `delete_site_asset` to manage CSS, JS, images, JSON, and other files.

**To add a new asset:**
- `create_site_asset(filename="custom.css", file_content=css_text, post_permalink=post_permalink)`
- CSS/JS files are automatically linked; other files are available as template variables

**To update an asset:**
1. Delete: `delete_site_asset(filename="custom.css", post_permalink=post_permalink)`
2. Create: `create_site_asset(filename="custom.css", file_content=new_css_text, post_permalink=post_permalink)`

**To delete an asset:**
- `delete_site_asset(filename="banner.jpg", post_permalink=post_permalink)`

Only provided fields will be updated; others remain unchanged.""",
    )
    return result
