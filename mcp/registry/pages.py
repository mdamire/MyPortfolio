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
) -> str:
    """Create a new static page.

    Creates a new page as a draft. Use create_site_asset to add CSS, JS, images, or other files.

    Args:
        permalink: Unique URL-friendly identifier (letters, numbers, underscores only).
        heading: Page title (max 200 characters).
        content: Main HTML content (supports Django templates).
        navbar_title: Title to display in navbar. Only required if page should appear in navbar.
        navbar_serial: Order in navbar (default: 0). Not effective if no navbar_title.
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
) -> str:
    """Update an existing static page.

    Updates page fields. Only provided fields are updated.
    Use create_site_asset and delete_site_asset to manage CSS, JS, images, and other files.

    Args:
        permalink: Current permalink of the page.
        new_permalink: New permalink.
        heading: New title.
        content: New HTML content.
        navbar_title: New navbar title (set to empty string to remove from navbar).
        navbar_serial: New navbar order.
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
  - All assets are available as context variables: {{ filename_without_extension.url }}

**Optional Fields:**
- **navbar_title**: Title to display in the top navigation bar
  - Only provide this if the page should appear in the navbar
  - If the page is referenced from another page, you don't need to add it to the navbar
  - Example: "About", "Contact", "Projects"
- **navbar_serial**: Order position in navbar (default: 0)
  - Lower numbers appear first
  - Only effective if navbar_title is provided

**Adding Assets (CSS, JS, Images, JSON, etc.):**
Use the `create_site_asset` tool to add any type of file to your page:

**For CSS/JS Files (automatically linked):**
- These are automatically included when viewing the page
- Example: `create_site_asset(filename="custom.css", file_content=css_text, page_permalink="about-me")`
- Example: `create_site_asset(filename="custom.js", file_content=js_text, page_permalink="about-me")`

**For Images, JSON, and other files (available as template variables):**
- These are available in Django templates as context variables
- Access using: {{ filename_without_extension.url }}
- Example: For "banner.jpg", use {{ banner.url }} in the content
- Example: `create_site_asset(filename="banner.jpg", file_content=base64_encoded_image, page_permalink="about-me")`
- Example: `create_site_asset(filename="data.json", file_content=json_text, page_permalink="about-me")`

**File Content for Asset:**
- Binary files (images, audio): Provide base64-encoded content
- Text files (CSS, JS, JSON): Provide plain text content

""",
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
  - All assets are available as context variables: {{ filename_without_extension.url }}
- **navbar_title**: Update navbar title (set to empty string "" to remove from navbar)
- **navbar_serial**: Update navbar order position

**Managing Assets:**
Use `create_site_asset` and `delete_site_asset` to manage CSS, JS, images, JSON, and other files.

**To add a new asset:**
- `create_site_asset(filename="custom.css", file_content=css_text, page_permalink=page_permalink)`
- CSS/JS files are automatically linked; other files are available as template variables

**To update an asset:**
1. Delete: `delete_site_asset(filename="custom.css", page_permalink=page_permalink)`
2. Create: `create_site_asset(filename="custom.css", file_content=new_css_text, page_permalink=page_permalink)`

**To delete an asset:**
- `delete_site_asset(filename="banner.jpg", page_permalink=page_permalink)`

Only provided fields will be updated; others remain unchanged.""",
    )
    return result
