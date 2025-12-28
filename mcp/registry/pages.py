from typing import Optional
from django.core.files.base import ContentFile

from mcp_serializer.features.tool.result import ToolsResult

from pages.models import StaticPage
from common.models import SiteAsset
from mcp_serializer.features.prompt.result import PromptsResult
from ..schema import (
    PageDetailResponse,
    PageListResponse,
    _page_to_response,
)
from .registry import registry


## Tools
# pages
@registry.tool()
def create_page(
    permalink: str,
    heading: str,
    content: str,
    navbar_title: Optional[str] = None,
    navbar_serial: int = 0,
    css_file_content: Optional[str] = None,
    js_file_content: Optional[str] = None,
) -> str:
    """Create a new static page.

    Creates a new page as a draft with optional custom CSS and JavaScript files.

    Args:
        permalink: Unique URL-friendly identifier (letters, numbers, underscores only).
        heading: Page title (max 200 characters).
        content: Main HTML content (supports Django templates).
        navbar_title: Title to display in navbar. Only required if page should appear in navbar.
        navbar_serial: Order in navbar (default: 0). Not effective if no navbar_title.
        css_file_content: Custom CSS content for this page.
        js_file_content: Custom JavaScript content for this page.
    """
    if StaticPage.objects.filter(permalink=permalink).exists():
        result = ToolsResult(is_error=True)
        result.add_text_content(f"Page with permalink '{permalink}' already exists")
        return result

    page = StaticPage.objects.create(
        permalink=permalink,
        heading=heading,
        content=content,
        navbar_title=navbar_title,
        navbar_serial=navbar_serial,
        requires_rendering=True,
        is_published=False,
    )

    # Handle CSS file
    if css_file_content:
        css_file = ContentFile(
            css_file_content.encode("utf-8"), name=f"{permalink}.css"
        )
        SiteAsset.objects.create(
            page=page,
            key=f"css_{permalink}",
            file=css_file,
            description="Custom CSS for this page",
            is_static=True,
            is_active=True,
        )

    # Handle JS file
    if js_file_content:
        js_file = ContentFile(js_file_content.encode("utf-8"), name=f"{permalink}.js")
        SiteAsset.objects.create(
            page=page,
            key=f"js_{permalink}",
            file=js_file,
            description="Custom JavaScript for this page",
            is_static=True,
            is_active=True,
        )

    return f"Page with permalink {page.permalink} created successfully."


@registry.tool()
def get_page(permalink: str) -> PageDetailResponse:
    """Retrieve a specific static page.

    Fetches page details and associated CSS/JS assets as embedded resources.

    Args:
        permalink: The unique permalink of the page.
    """
    result = ToolsResult()
    try:
        page = StaticPage.objects.get(permalink=permalink)
    except StaticPage.DoesNotExist:
        result = ToolsResult(is_error=True)
        result.add_text_content(f"Page with permalink '{permalink}' does not exist")
        return result

    result.add_structured_content(_page_to_response(page))

    # Add CSS and JS assets as embedded files
    assets = SiteAsset.objects.filter(page=page)
    for asset in assets:
        result.add_file(file=asset.file, title=asset.description or asset.key)
    return result


@registry.tool()
def list_pages(
    is_published: Optional[bool] = None,
    limit: Optional[int] = None,
) -> PageListResponse:
    """List static pages with optional filtering.

    Lists all the available static pages, with options to filter by publication status
    and to limit the number of results.

    Args:
        is_published: Filter by publication status (True/False/None for all).
        limit: Maximum number of pages to return.
    """
    queryset = StaticPage.objects.all()

    if is_published is not None:
        queryset = queryset.filter(is_published=is_published)

    if limit:
        queryset = queryset[:limit]

    return PageListResponse(page_list=[_page_to_response(page) for page in queryset])


@registry.tool()
def update_page(
    permalink: str,
    new_permalink: Optional[str] = None,
    heading: Optional[str] = None,
    content: Optional[str] = None,
    navbar_title: Optional[str] = None,
    navbar_serial: Optional[int] = None,
    css_file_content: Optional[str] = None,
    js_file_content: Optional[str] = None,
) -> str:
    """Update an existing static page.

    Updates page fields and/or CSS/JS assets. Only provided fields are updated.

    Args:
        permalink: Current permalink of the page.
        new_permalink: New permalink.
        heading: New title.
        content: New HTML content.
        navbar_title: New navbar title (set to empty string to remove from navbar).
        navbar_serial: New navbar order.
        css_file_content: Updated CSS content (replaces existing).
        js_file_content: Updated JS content (replaces existing).
    """
    from django.core.files.base import ContentFile

    page = StaticPage.objects.get(permalink=permalink)

    if new_permalink is not None:
        page.permalink = new_permalink
    if heading is not None:
        page.heading = heading
    if content is not None:
        page.content = content
    if navbar_title is not None:
        page.navbar_title = navbar_title if navbar_title else None
    if navbar_serial is not None:
        page.navbar_serial = navbar_serial

    page.save()

    # Handle CSS file update
    if css_file_content is not None:
        # Delete existing CSS asset
        SiteAsset.objects.filter(page=page, key="custom_css").delete()
        # Create new one
        css_file = ContentFile(
            css_file_content.encode("utf-8"), name=f"{page.permalink}.css"
        )
        SiteAsset.objects.create(
            page=page,
            key="custom_css",
            file=css_file,
            description="Custom CSS for this page",
        )

    # Handle JS file update
    if js_file_content is not None:
        # Delete existing JS asset
        SiteAsset.objects.filter(page=page, key="custom_js").delete()
        # Create new one
        js_file = ContentFile(
            js_file_content.encode("utf-8"), name=f"{page.permalink}.js"
        )
        SiteAsset.objects.create(
            page=page,
            key="custom_js",
            file=js_file,
            description="Custom JavaScript for this page",
        )

    return f"Page with permalink {page.permalink} updated successfully."


## Prompts
@registry.prompt()
def page_create_prompt():
    """Create a static page"""
    result = PromptsResult()
    result.add_text(
        role=PromptsResult.Roles.USER,
        text="""Create engaging static pages with HTML content and Django template support.

**Required Fields:**
- **permalink**: Unique URL identifier (letters/numbers/underscores, e.g., "about-me", "contact")
  - Must be unique across all pages
  - Cannot be changed easily later, choose carefully
- **heading**: Page title (max 200 chars)
- **content**: HTML body with full Django template language support
  - Bootstrap 5 CSS and JavaScript are already loaded and available
  - Supports Django template syntax: variables, conditionals, loops, filters
  - All media files are available as context variables (see Media Files section below)
  - If media file is needed add it's reference like this: {{ filename_without_extension.url }} even before creating it.

**Optional Fields:**
- **navbar_title**: Title to display in the top navigation bar
  - Only provide this if the page should appear in the navbar
  - If the page is referenced from another page, you don't need to add it to the navbar
  - Example: "About", "Contact", "Projects"
- **navbar_serial**: Order position in navbar (default: 0)
  - Lower numbers appear first
  - Only effective if navbar_title is provided
- **css_file_content**: Custom CSS for this page only (scoped to this page, won't affect other pages)
- **js_file_content**: Custom JavaScript for this page only (scoped to this page, won't affect other pages)

**Media Files:**
To add images or audio files to a page, use `create_media_file` tool after creating the page:
- Provide base64-encoded content for binary files (images, audio)
- Make sure the name has the correct extension (e.g., .jpg, .png, .mp3)
- Files are automatically available in Django templates as context variables
- Access in content using: {{ filename_without_extension.url }}
- Example: For "banner.jpg", use {{ banner.url }} in the content.
- Supported formats: images (jpg, png, gif, svg, etc.), audio (mp3, wav, etc.)

Pages are created as drafts (is_published=False). Base styling from staticpage.html template is automatically available.""",
    )
    return result


@registry.prompt()
def page_update_prompt():
    """Update an existing static page"""
    result = PromptsResult()
    result.add_text(
        role=PromptsResult.Roles.USER,
        text="""Update existing static pages. Use `get_page` first to see current content.

**Updatable Fields (all optional):**
- **new_permalink**: Change URL identifier (must remain unique)
- **heading**: Update title
- **content**: Update HTML body (supports Django template language)
  - All media files are available as context variables: {{ filename.url }}
- **navbar_title**: Update navbar title (set to empty string "" to remove from navbar)
- **navbar_serial**: Update navbar order position
- **css_file_content**: Replace custom CSS (scoped to this page only)
- **js_file_content**: Replace custom JavaScript (scoped to this page only)

**Media Files:**
To update a media file, first delete it using `delete_media_file`, then create a new one with `create_media_file`.
- Delete: `delete_media_file(content_type="page", permalink=page_permalink, filename=filename)`
- Create: `create_media_file(content_type="page", permalink=page_permalink, filename=filename, file_content=base64_content)`

Only provided fields will be updated; others remain unchanged.""",
    )
    return result
