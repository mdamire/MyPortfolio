from typing import Optional

from mcp_serializer.features.tool.result import ToolsResult
from mcp_serializer.features.prompt.result import PromptsResult

from pages.models import HomePageSection
from common.models import SiteAsset
from ..schema import (
    HomePageSectionDetailResponse,
    HomePageSectionListResponse,
    _homepage_section_to_response,
)
from .registry import registry


## Tools
@registry.tool()
def create_homepage_section(
    name: str,
    content: str,
    navbar_title: Optional[str] = None,
    serial: int = 0,
) -> str:
    """Create a new homepage section.

    Creates a new section for the homepage. Use create_site_asset to add CSS, JS, images, or other files.

    Args:
        name: Descriptive name to identify this section (max 32 characters).
        content: Main HTML content (supports Django templates).
        navbar_title: Title to display in navbar. Only required if section should appear in navbar.
        serial: Order position on homepage (lower numbers appear first, default: 0).
    """
    if HomePageSection.objects.filter(name=name).exists():
        result = ToolsResult(is_error=True)
        result.add_text_content(f"Homepage section with name '{name}' already exists")
        return result

    section = HomePageSection.objects.create(
        name=name,
        content=content,
        navbar_title=navbar_title,
        serial=serial,
        requires_rendering=True,
        is_active=True,
    )

    return f"Homepage section '{section.name}' created successfully."


@registry.tool()
def get_homepage_section(name: str) -> HomePageSectionDetailResponse:
    """Retrieve a specific homepage section.

    Fetches section details and associated CSS/JS assets as embedded resources.
    Note: All assets from ALL active homepage sections are included, as they are shared across the homepage.

    Args:
        name: The unique name of the homepage section.
    """
    result = ToolsResult()
    try:
        section = HomePageSection.objects.get(name=name)
    except HomePageSection.DoesNotExist:
        result = ToolsResult(is_error=True)
        result.add_text_content(f"Homepage section with name '{name}' does not exist")
        return result

    result.add_structured_content(_homepage_section_to_response(section))

    # Add CSS and JS assets from ALL active homepage sections (assets are shared)
    active_sections = HomePageSection.objects.filter(is_active=True)
    for active_section in active_sections:
        assets = SiteAsset.objects.filter(homepage_section=active_section)
        for asset in assets:
            result.add_file(file=asset.file, title=asset.description or asset.key)
    return result


@registry.tool()
def list_homepage_sections(
    limit: Optional[int] = None,
) -> HomePageSectionListResponse:
    """List active homepage sections.

    Lists all active homepage sections, with option to limit the number of results.
    Only active sections are returned.

    Args:
        limit: Maximum number of sections to return.
    """
    queryset = HomePageSection.objects.filter(is_active=True)

    if limit:
        queryset = queryset[:limit]

    return HomePageSectionListResponse(
        section_list=[_homepage_section_to_response(section) for section in queryset]
    )


@registry.tool()
def update_homepage_section(
    name: str,
    new_name: Optional[str] = None,
    content: Optional[str] = None,
    navbar_title: Optional[str] = None,
    serial: Optional[int] = None,
    is_active: Optional[bool] = None,
) -> str:
    """Update an existing homepage section.

    Updates section fields. Only provided fields are updated.
    Use create_site_asset and delete_site_asset to manage CSS, JS, images, and other files.

    Args:
        name: Current name of the section.
        new_name: New name for the section.
        content: New HTML content.
        navbar_title: New navbar title (set to empty string to remove from navbar).
        serial: New order position.
        is_active: Toggle active status.
    """
    try:
        section = HomePageSection.objects.get(name=name)
    except HomePageSection.DoesNotExist:
        return f"Error: Homepage section with name '{name}' does not exist"

    if new_name is not None:
        section.name = new_name
    if content is not None:
        section.content = content
    if navbar_title is not None:
        section.navbar_title = navbar_title if navbar_title else None
    if serial is not None:
        section.serial = serial
    if is_active is not None:
        section.is_active = is_active

    section.save()

    return f"Homepage section '{section.name}' updated successfully."


## Prompts
@registry.prompt()
def homepage_section_create_prompt():
    """Create a homepage section"""
    result = PromptsResult()
    result.add_text(
        role=PromptsResult.Roles.USER,
        text="""Create engaging homepage sections with HTML content and Django template support.

**Required Fields:**
- **name**: Unique identifier for this section (max 32 chars, e.g., "hero", "about", "skills")
  - Must be unique across all homepage sections
  - Use descriptive names for easy management
- **content**: HTML body with full Django template language support
  - Bootstrap 5 CSS and JavaScript are already loaded and available
  - Supports Django template syntax: variables, conditionals, loops, filters
  - All assets are available as context variables: {{ filename_without_extension.url }}

**Optional Fields:**
- **navbar_title**: Title to display in the top navigation bar
  - Only provide this if the section should have a navbar link
  - Example: "About", "Skills", "Projects"
- **serial**: Order position on homepage (default: 0)
  - Lower numbers appear first
  - Example: 0 for hero section, 10 for about, 20 for skills

**Adding Assets (CSS, JS, Images, JSON, etc.):**
Use the `create_site_asset` tool to add any type of file to your section:

**IMPORTANT: Assets are SHARED across ALL homepage sections!**
- Any asset added to any section is available to ALL sections on the homepage
- This allows you to create consistent styling and shared resources
- CSS/JS files from all active sections are automatically loaded on the homepage

**For CSS/JS Files (automatically linked):**
- These are automatically included when viewing the homepage
- Available to ALL homepage sections
- Example: `create_site_asset(filename="hero.css", file_content=css_text, homepage_section_name="hero")`
- Example: `create_site_asset(filename="hero.js", file_content=js_text, homepage_section_name="hero")`

**For Images, JSON, and other files (available as template variables):**
- These are available in Django templates as context variables
- Access using: {{ filename_without_extension.url }}
- Available to ALL homepage sections
- Example: For "banner.jpg", use {{ banner.url }} in ANY section's content
- Example: `create_site_asset(filename="banner.jpg", file_content=base64_encoded_image, homepage_section_name="hero")`
- Example: `create_site_asset(filename="data.json", file_content=json_text, homepage_section_name="skills")`

**File Content for Asset:**
- Binary files (images, audio): Provide base64-encoded content
- Text files (CSS, JS, JSON): Provide plain text content

**Sections are displayed in order by serial number on the homepage.**
""",
    )
    return result


@registry.prompt()
def homepage_section_update_prompt():
    """Update an existing homepage section"""
    result = PromptsResult()
    result.add_text(
        role=PromptsResult.Roles.USER,
        text="""Update existing homepage sections. Use `get_homepage_section` first to see current content.

**Updatable Fields (all optional):**
- **new_name**: Change section identifier (must remain unique)
- **content**: Update HTML body (supports Django template language)
  - All assets are available as context variables: {{ filename_without_extension.url }}
- **navbar_title**: Update navbar title (set to empty string "" to remove from navbar)
- **serial**: Update order position on homepage
- **is_active**: Toggle section visibility (True/False)

**Managing Assets:**
Use `create_site_asset` and `delete_site_asset` to manage CSS, JS, images, JSON, and other files.

**IMPORTANT: Assets are SHARED across ALL homepage sections!**
- Any asset added to any section is available to ALL sections on the homepage
- When you add/update an asset for one section, it affects all sections
- This allows for consistent styling and shared resources across the homepage

**To add a new asset:**
- `create_site_asset(filename="custom.css", file_content=css_text, homepage_section_name=section_name)`
- CSS/JS files are automatically linked; other files are available as template variables
- The asset will be available to ALL homepage sections

**To update an asset:**
1. Delete: `delete_site_asset(filename="custom.css", homepage_section_name=section_name)`
2. Create: `create_site_asset(filename="custom.css", file_content=new_css_text, homepage_section_name=section_name)`

**To delete an asset:**
- `delete_site_asset(filename="banner.jpg", homepage_section_name=section_name)`

Only provided fields will be updated; others remain unchanged.""",
    )
    return result
