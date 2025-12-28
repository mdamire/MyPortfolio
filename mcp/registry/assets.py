import base64
from typing import Optional
from django.core.files.base import ContentFile

from mcp_serializer.features.tool.result import ToolsResult

from posts.models import PostDetail
from pages.models import StaticPage, HomePageSection
from common.models import SiteAsset
from .registry import registry


@registry.tool()
def create_site_asset(
    filename: str,
    file_content: str,
    description: Optional[str] = None,
    post_permalink: Optional[str] = None,
    page_permalink: Optional[str] = None,
    homepage_section_name: Optional[str] = None,
) -> str:
    """Create a site asset (CSS, JS, image, JSON, etc.) for a post, page, homepage section, or globally.

    Creates any type of file asset. The file will be automatically configured based on its extension:
    - CSS/JS files: Automatically linked as static resources (is_static=True)
    - Other files (images, JSON, etc.): Available as Django template context variables (is_static=False)

    If no reference is provided (post, page, or homepage_section), the asset is global
    and will be available across the entire site.

    Args:
        filename: Name of the file with extension (e.g., "banner.jpg", "custom.css", "data.json").
        file_content: Base64 encoded content for binary files, or plain text for text files.
        description: Optional description of the asset.
        post_permalink: Link to a specific post (optional).
        page_permalink: Link to a specific page (optional).
        homepage_section_name: Link to a specific homepage section (optional).

    """
    # Determine if file is static based on extension
    file_ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    is_static = file_ext in ["css", "js"]

    # Extract key from filename (without extension)
    key = filename.rsplit(".", 1)[0]

    # Decode file content
    # For text files (CSS, JS, etc.), treat as plain text - don't attempt base64 decode
    text_extensions = ["css", "js", "txt", "json", "xml", "html", "htm", "md", "csv"]

    if file_ext in text_extensions:
        # Text file - use content directly
        content_file = ContentFile(file_content.encode("utf-8"), name=filename)
    else:
        # Binary file - expect base64 encoding
        try:
            decoded_content = base64.b64decode(file_content, validate=True)
            content_file = ContentFile(decoded_content, name=filename)
        except Exception:
            # If base64 decode fails, fall back to treating as text
            content_file = ContentFile(file_content.encode("utf-8"), name=filename)

    # Build asset kwargs
    asset_kwargs = {
        "key": key,
        "file": content_file,
        "description": description or f"Asset: {filename}",
        "is_static": is_static,
        "is_active": True,
    }

    # Handle references
    reference_count = sum(
        [
            post_permalink is not None,
            page_permalink is not None,
            homepage_section_name is not None,
        ]
    )

    if reference_count > 1:
        tool_result = ToolsResult(is_error=True)
        tool_result.add_text_content(
            "Error: Can only specify one reference (post, page, or homepage_section)"
        )
        return tool_result

    # Get reference objects
    if post_permalink:
        try:
            post = PostDetail.objects.get(permalink=post_permalink)
            asset_kwargs["post"] = post
            scope = f"post '{post_permalink}'"
        except PostDetail.DoesNotExist:
            tool_result = ToolsResult(is_error=True)
            tool_result.add_text_content(
                f"Error: Post with permalink '{post_permalink}' does not exist"
            )
            return tool_result
    elif page_permalink:
        try:
            page = StaticPage.objects.get(permalink=page_permalink)
            asset_kwargs["page"] = page
            scope = f"page '{page_permalink}'"
        except StaticPage.DoesNotExist:
            tool_result = ToolsResult(is_error=True)
            tool_result.add_text_content(
                f"Error: Page with permalink '{page_permalink}' does not exist"
            )
            return tool_result
    elif homepage_section_name:
        try:
            homepage_section = HomePageSection.objects.get(name=homepage_section_name)
            asset_kwargs["homepage_section"] = homepage_section
            scope = f"homepage section '{homepage_section_name}'"
        except HomePageSection.DoesNotExist:
            tool_result = ToolsResult(is_error=True)
            tool_result.add_text_content(
                f"Error: Homepage section with name '{homepage_section_name}' does not exist"
            )
            return tool_result
    else:
        scope = "globally (site-wide)"

    # Create the asset
    asset = SiteAsset.objects.create(**asset_kwargs)

    # Build response message
    if is_static:
        usage_msg = f"CSS/JS file '{filename}' will be automatically linked when viewing {scope}."
    else:
        usage_msg = (
            f"Asset '{filename}' is available in templates as: {{{{ {key}.url }}}}"
        )

    return f"Asset '{filename}' created successfully for {scope}. {usage_msg}"


@registry.tool()
def delete_site_asset(
    filename: str,
    post_permalink: Optional[str] = None,
    page_permalink: Optional[str] = None,
    homepage_section_name: Optional[str] = None,
) -> str:
    """Delete a site asset by filename.

    Removes an asset from a specific post, page, homepage section, or global assets.
    If no reference is provided, will search for global assets.

    Args:
        filename: Name of the file to delete.
        post_permalink: Post permalink if asset belongs to a post (optional).
        page_permalink: Page permalink if asset belongs to a page (optional).
        homepage_section_name: Homepage section name if asset belongs to a section (optional).

    """
    # Build filter kwargs
    filter_kwargs = {}

    reference_count = sum(
        [
            post_permalink is not None,
            page_permalink is not None,
            homepage_section_name is not None,
        ]
    )

    if reference_count > 1:
        return "Error: Can only specify one reference (post, page, or homepage_section)"

    # Get reference objects and build filter
    if post_permalink:
        try:
            post = PostDetail.objects.get(permalink=post_permalink)
            filter_kwargs["post"] = post
            scope = f"post '{post_permalink}'"
        except PostDetail.DoesNotExist:
            return f"Error: Post with permalink '{post_permalink}' does not exist"
    elif page_permalink:
        try:
            page = StaticPage.objects.get(permalink=page_permalink)
            filter_kwargs["page"] = page
            scope = f"page '{page_permalink}'"
        except StaticPage.DoesNotExist:
            return f"Error: Page with permalink '{page_permalink}' does not exist"
    elif homepage_section_name:
        try:
            homepage_section = HomePageSection.objects.get(name=homepage_section_name)
            filter_kwargs["homepage_section"] = homepage_section
            scope = f"homepage section '{homepage_section_name}'"
        except HomePageSection.DoesNotExist:
            return f"Error: Homepage section with name '{homepage_section_name}' does not exist"
    else:
        # Global assets have all references as None
        filter_kwargs["post__isnull"] = True
        filter_kwargs["page__isnull"] = True
        filter_kwargs["homepage_section__isnull"] = True
        scope = "global assets"

    # Find and delete asset
    assets = SiteAsset.objects.filter(**filter_kwargs)
    deleted = False

    for asset in assets:
        if asset.file and filename in asset.file.name:
            asset.delete()
            deleted = True
            break

    if deleted:
        return f"Asset '{filename}' deleted successfully from {scope}"
    else:
        return f"Error: Asset '{filename}' not found in {scope}"
