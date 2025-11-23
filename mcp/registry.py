from mcp_serializer.registry import MCPRegistry
from mcp_serializer.features.tool.result import ToolsResult

from django.conf import settings
from posts.models import PostDetail, PostTag, PostAsset
from mcp_serializer.features.prompt.result import PromptsResult
from .schema import (
    PostDetailResponse,
    PostListResponse,
    PostAssetResponse,
    PostAssetListResponse,
    _post_to_response,
)

registry = MCPRegistry()


## Resources
base_dir = settings.BASE_DIR.parent
registry.add_file_resource(
    file=f"{base_dir}/posts/static/posts/post-detail.css",
    # file=get_full_url(static("posts/post-detail.css")),
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
# posts
@registry.tool()
def create_post(
    permalink: str,
    heading: str,
    content: str,
    introduction: str = None,
    include_sublinks: bool = True,
    tags: list = None,
) -> PostDetailResponse:
    """Create a new blog post.

    Creates a new post as a draft (unpublished). Use publish_post() to publish it later. The post will be
    rendered on a Django template.

    Args:
        permalink: Unique URL-friendly identifier for the post (starts with letter,
            followed by letters, numbers, or underscores).
        heading: Title of the post (max 200 characters).
        content: Main content of the post (supports HTML and Django templates).
        introduction: Optional brief introduction or summary of the post.
        include_sublinks: Whether to generate sublinks from header tags (default: True).
        tags: List of tags where each item is either:
            - A string (label) for an existing tag
            - A tuple/list (label, color, bg_color) to create a new tag
    """
    post = PostDetail.objects.create(
        permalink=permalink,
        heading=heading,
        content=content,
        introduction=introduction,
        requires_rendering=True,
        is_published=False,
        include_sublinks=include_sublinks,
    )

    if tags:
        tag_objects = []
        for tag_item in tags:
            if isinstance(tag_item, str):
                # It's a label string - get existing tag
                tag_obj = PostTag.objects.get(label=tag_item)
                tag_objects.append(tag_obj)
            elif isinstance(tag_item, (list, tuple)) and len(tag_item) == 3:
                # It's a tuple (label, color, bg_color) - create new tag
                label, color, bg_color = tag_item
                tag_obj, _ = PostTag.objects.get_or_create(
                    label=label, defaults={"color": color, "bg_color": bg_color}
                )
                tag_objects.append(tag_obj)

        post.tags.set(tag_objects)

    return _post_to_response(post)


@registry.tool()
def get_post(permalink: str) -> PostDetailResponse:
    """Retrieve a specific blog post by permalink.

    Fetches a single post using its permalink. It shows the post details in structured format.
    If there are any static files associated with the post, they are shown as embedded resource.

    Args:
        permalink: The unique permalink of the post.
    """
    result = ToolsResult()
    try:
        post = PostDetail.objects.get(permalink=permalink)
    except PostDetail.DoesNotExist:
        result = ToolsResult(is_error=True)
        result.add_text_content(f"Post with permalink {permalink} does not exist")
        return result

    result.add_structured_content(_post_to_response(post))

    assets = PostAsset.objects.filter(post=post)
    for asset in assets:
        result.add_file(file=asset.file, description=asset.description)
    return result


@registry.tool()
def publish_post(permalink: str) -> PostDetailResponse:
    """Publish a blog post.

    Marks a post as published and sets the publish date to today.

    Args:
        permalink: The unique permalink of the post to publish.
    """
    from datetime import date

    post = PostDetail.objects.get(permalink=permalink)
    post.is_published = True
    post.publish_date = date.today()
    post.save()

    return _post_to_response(post)


@registry.tool()
def list_posts(
    is_published: bool = None,
    tag_id: int = None,
    limit: int = None,
) -> PostListResponse:
    """List all blog posts with optional filtering.

    Retrieves a list of posts, optionally filtered by publication status or tag.
    Results are ordered by feature priority, then publish date, then creation date.

    Args:
        is_published: Filter by publication status (True for published, False for
            drafts, None for all).
        tag_id: Filter posts that have this specific tag ID.
        limit: Maximum number of posts to return (optional).
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
    new_permalink: str = None,
    heading: str = None,
    content: str = None,
    introduction: str = None,
    requires_rendering: bool = None,
    include_sublinks: bool = None,
    tags: list = None,
    feature: int = None,
) -> PostDetailResponse:
    """Update an existing blog post.

    Updates one or more fields of an existing post. Only provided fields will be
    updated; others remain unchanged. Use publish_post tool to publish the post.

    Args:
        permalink: The current permalink of the post to update.
        new_permalink: New permalink for the post (optional).
        heading: New title for the post (optional).
        content: New content for the post (optional).
        introduction: New introduction text (optional).
        requires_rendering: Update rendering requirement (optional).
        include_sublinks: Update sublinks generation preference (optional).
        tags: New list of tag IDs to replace existing tags (optional).
        feature: New feature priority value (optional).
    """
    post = PostDetail.objects.get(permalink=permalink)

    if new_permalink is not None:
        post.permalink = new_permalink
    if heading is not None:
        post.heading = heading
    if content is not None:
        post.content = content
    if introduction is not None:
        post.introduction = introduction
    if requires_rendering is not None:
        post.requires_rendering = requires_rendering
    if include_sublinks is not None:
        post.include_sublinks = include_sublinks
    if feature is not None:
        post.feature = feature

    post.save()

    if tags is not None:
        post.tags.set(tags)

    return _post_to_response(post)


@registry.tool()
def delete_post(permalink: str) -> str:
    """Delete a blog post.

    Permanently deletes a post and all its associated assets from the database.

    Args:
        permalink: The permalink of the post to delete.
    """
    post = PostDetail.objects.get(permalink=permalink)
    post.delete()

    return f"Post '{permalink}' deleted successfully, permalink: {permalink}"


# assets
@registry.tool()
def create_post_asset(
    post_permalink: str,
    key: str,
    filename: str,
    file_content: str,
    description: str = None,
) -> PostAssetResponse:
    """Create a new post asset.

    Creates a new asset (file) associated with a specific post. Assets can be
    images, CSS files, JavaScript files, or any other file type needed for the post.
    The file will be saved in the media directory for the post.

    Args:
        post_permalink: The permalink of the post this asset belongs to.
        key: Unique identifier key for the asset (one word or multiple words with
            underscores, max 128 characters). Used as context variable name in templates.
        filename: Name of the file to create (e.g., "style.css", "script.js", "image.png").
        file_content: The content of the file as a string (text content for CSS/JS/HTML files).
        description: Optional note about where or how this asset can be used.
    """
    from django.core.files.base import ContentFile

    post = PostDetail.objects.get(permalink=post_permalink)

    # Create ContentFile from the provided content
    content_file = ContentFile(file_content.encode("utf-8"), name=filename)

    # Create the asset with the file
    asset = PostAsset.objects.create(
        post=post,
        key=key,
        file=content_file,
        description=description,
    )

    return PostAssetResponse(
        id=asset.id,
        post_id=asset.post.id,
        key=asset.key,
        file=asset.file.url if asset.file else " ",
        description=asset.description or " ",
    )


@registry.tool()
def get_post_asset(asset_id: int) -> PostAssetResponse:
    """Retrieve a specific post asset by ID.

    Fetches a single asset using its database ID.

    Args:
        asset_id: The database ID of the asset.
    """
    asset = PostAsset.objects.get(id=asset_id)

    return PostAssetResponse(
        id=asset.id,
        post_id=asset.post.id,
        key=asset.key,
        file=asset.file.url if asset.file else "",
        description=asset.description,
    )


@registry.tool()
def list_post_assets(
    post_permalink: str = None,
    limit: int = None,
) -> PostAssetListResponse:
    """List post assets with optional filtering.

    Retrieves a list of assets, optionally filtered by post. Results are ordered
    by creation date (newest first).

    Args:
        post_permalink: Filter assets belonging to this specific post permalink (optional).
        limit: Maximum number of assets to return (optional).
    """
    queryset = PostAsset.objects.all()

    if post_permalink is not None:
        queryset = queryset.filter(post__permalink=post_permalink)

    if limit:
        queryset = queryset[:limit]

    assets = []
    for asset in queryset:
        assets.append(
            PostAssetResponse(
                id=asset.id,
                post_id=asset.post.id,
                key=asset.key,
                file=asset.file.url if asset.file else "",
                description=asset.description,
            )
        )

    return PostAssetListResponse(post_asset_list=assets)


@registry.tool()
def update_post_asset(
    asset_id: int,
    key: str = None,
    file_path: str = None,
    description: str = None,
) -> PostAssetResponse:
    """Update an existing post asset.

    Updates one or more fields of an existing asset. Only provided fields will be
    updated; others remain unchanged.

    Args:
        asset_id: The database ID of the asset to update.
        key: New key identifier for the asset (optional).
        file_path: New file path for the asset (optional).
        description: New description for the asset (optional).
    """
    asset = PostAsset.objects.get(id=asset_id)

    if key is not None:
        asset.key = key
    if file_path is not None:
        asset.file = file_path
    if description is not None:
        asset.description = description

    asset.save()

    return PostAssetResponse(
        id=asset.id,
        post_id=asset.post.id,
        key=asset.key,
        file=asset.file.url if asset.file else "",
        description=asset.description,
    )


@registry.tool()
def delete_post_asset(asset_id: int):
    """Delete a post asset.

    Permanently deletes an asset from the database. The associated post will not
    be affected.

    Args:
        asset_id: The database ID of the asset to delete.
    """
    asset = PostAsset.objects.get(id=asset_id)
    asset.delete()

    return f"Asset {asset_id} deleted successfully, asset_id: {asset_id}"


## Prompts
@registry.prompt()
def post_create_prompt():
    """Create a blog post

    Create a new blog post with the given details.
    """
    existing_tag_labels = [
        (tag.label, tag.color, tag.bg_color) for tag in PostTag.objects.all()
    ]
    existing_tag_labels_str = ", ".join(existing_tag_labels)

    result = PromptsResult()
    result.add_text(
        role=PromptsResult.Roles.USER,
        text=f"""You are a helpful assistant that can help create engaging blog posts. Here's the complete workflow:

**Post Creation Process**:
1. Prepare the content (heading, introduction, content)
2. Get approval from user (for text-based posts)
3. Check available tags with `list_tags` tool
4. Create new tags if needed with `create_tag` tool
5. Create the post with `create_post` tool (creates as draft)
6. Add any post-specific assets with `create_post_asset` tool
7. When ready, publish with `publish_post` tool

**IMPORTANT - Approval Workflow**:
Before creating any text-based post, you MUST present the content for review and approval:
1. Show the post details your are about to create in plain text format.
2. Wait for explicit approval from the user
3. Only after approval, proceed with creating the post using the `create_post` tool
4. If not approved then update the content and get approval again.

**Required Fields**:
- **Permalink**: Unique URL-friendly identifier (e.g., "my-first-post"). Must start with a letter, followed by letters, numbers, or underscores. Cannot be changed easily later, so choose carefully.
- **Heading**: A short, single-line title that attracts readers and captures the essence of the post (max 200 characters).
- **Content**: The main body of the post, written in HTML. The post has access to:
  - Bootstrap 5 CSS and JavaScript (already loaded)
  - `post-detail.css` (base styling for all posts)
  - `post-detail.js` (base functionality for all posts)
  - Django template language support for dynamic content

**Optional Fields**:
- **Introduction**: A brief, compelling summary (2-3 sentences) that will appear below the heading on the post list page. Entices readers to click and read more.
- **Include Sublinks**: Whether to automatically generate a table of contents from header tags in the content (default: True). If the content is not text 
- **Tags**:
    - Tags helps to categorize, sort and find related posts easily.
    - Here are the existing tags as (label, font_color, bg_color): {existing_tag_labels_str}
        - label: Unique display name of the tag
        - font_color: css color (hex, rgb or color name) for text color"
        - bg_color: css color (hex, rgb or color name) for background color
    - tags is list of either label or (label, font_color, bg_color)
    - if you want to create a new tag then use (label, font_color, bg_color)
    - if you want to use an existing tag then use only the label


**Assets**: 
You can add post-specific assets (CSS, JS, images, etc.) AFTER creating the post using the `create_post_asset` tool:
- Provide `filename` (e.g., "style.css", "script.js", "banner.png") and `file_content` (the actual file contents as text)
- **CSS/JS assets**: Automatically included and available for the post to use
- **Images and other files**: Access via Django template syntax: `{{asset_key.url}}` where `asset_key` is the key you assigned when creating the asset
- Multiple assets with the same extension are supported (e.g., multiple CSS files)

**Dynamic Features**:
- Need interactive functionality? Create a JavaScript asset file
- Need custom styling? Create a CSS asset file


Remember: The content supports full Django template language, so you can use conditionals, loops, and access context variables including asset objects.""",
    )
    return result


# Update Post prompt
registry.add_text_prompt(
    name="update_post_prompt",
    title="Update an existing blog post",
    description="Update an existing blog post's content, metadata, or assets.",
    role="user",
    text="""You are a helpful assistant that can help update existing blog posts. Here's how to update a post:

**IMPORTANT - Approval Workflow**:
Before updating any text content (heading, introduction, or content), you MUST present the changes for review:
1. Show the current version and the proposed changes in plain text format
2. Clearly indicate what is being changed
3. Wait for explicit approval from the user
4. Only after approval, proceed with updating the post using the `update_post` tool
5. If changes have already been approved in the conversation, you can proceed without asking again

**What Can Be Updated**:
- **Heading**: The post title
- **Introduction**: The summary shown on the post list page
- **Content**: The main body of the post (HTML with Django template support)
- **Permalink**: The URL identifier (use `new_permalink` parameter)
- **Tags**: Add or remove tags to recategorize the post
- **Include Sublinks**: Toggle automatic sublink generation from headers

**Updating Process**:
1. First, use `get_post` tool to retrieve the current post content
2. Show the user what currently exists
3. Present the proposed changes for approval (if text-based)
4. Use `update_post` tool with only the fields that need to change
5. Other fields will remain unchanged

**Assets Management**:
- To add new assets: Use `create_post_asset` tool
- To update existing assets: Use `update_post_asset` tool
- To remove assets: Use `delete_post_asset` tool
- CSS/JS assets are automatically included in the post
- Other files can be accessed via `{{asset_key.url}}` in Django templates

Remember: Only update the fields that actually need to change. The `update_post` tool accepts optional parameters, so you don't need to provide all fields.""",
)
