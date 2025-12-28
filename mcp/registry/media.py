import base64
from typing import Optional
from django.core.files.base import ContentFile

from mcp_serializer.features.tool.result import ToolsResult

from posts.models import PostDetail, PostAsset
from pages.models import StaticPage, PageAsset
from .registry import registry


@registry.tool()
def create_media_file(
    content_type: str,
    permalink: str,
    filename: str,
    file_content: str,
    description: Optional[str] = None,
) -> str:
    """Create a media asset (image or audio) for a post or page.

    Creates an image or audio file asset associated with a specific post or page.
    The file content should be base64 encoded for binary files.

    Args:
        content_type: Type of content - either "post" or "page".
        permalink: The permalink of the post or page this media belongs to.
        filename: Name of the file (e.g., "banner.jpg", "audio.mp3").
        file_content: Base64 encoded content for images/audio, or text content.
        description: Optional description of the media file.
    """


    # Validate content_type
    if content_type not in ["post", "page"]:
        tool_result = ToolsResult(is_error=True)
        tool_result.add_text_content(f"Error: content_type must be either 'post' or 'page', got '{content_type}'")
        return tool_result

    # Get the content object (post or page)
    if content_type == "post":
        try:
            content_obj = PostDetail.objects.get(permalink=permalink)
        except PostDetail.DoesNotExist:
            tool_result = ToolsResult(is_error=True)
            tool_result.add_text_content(f"Error: Post with permalink '{permalink}' does not exist")
            return tool_result
        AssetModel = PostAsset
        content_field = "post"
    else:  # page
        try:
            content_obj = StaticPage.objects.get(permalink=permalink)
        except StaticPage.DoesNotExist:
            tool_result = ToolsResult(is_error=True)
            tool_result.add_text_content(f"Error: Page with permalink '{permalink}' does not exist")
            return tool_result
        AssetModel = PageAsset
        content_field = "page"

    # Decode base64 content
    try:
        decoded_content = base64.b64decode(file_content)
        content_file = ContentFile(decoded_content, name=filename)
    except Exception:
        # If not base64, treat as text
        content_file = ContentFile(file_content.encode("utf-8"), name=filename)

    # Create the asset
    asset_kwargs = {
        content_field: content_obj,
        "key": filename.rsplit(".", 1)[0],  # Use filename without extension as key
        "file": content_file,
        "description": description or f"Media file: {filename}",
        "is_static": False,
        "is_active": True,
    }
    asset = AssetModel.objects.create(**asset_kwargs)

    return f"Media file '{filename}' created successfully for {content_type} '{permalink}'. Access via: {{{{ {asset.key}.url }}}} in the content."


@registry.tool()
def delete_media_file(
    content_type: str,
    permalink: str,
    filename: str,
) -> str:
    """Delete a media file from a post or page.

    Removes a media asset by filename from the specified post or page.

    Args:
        content_type: Type of content - either "post" or "page".
        permalink: The permalink of the post or page.
        filename: Name of the file to delete.
    """
    # Validate content_type
    if content_type not in ["post", "page"]:
        return f"Error: content_type must be either 'post' or 'page', got '{content_type}'"

    # Get the content object (post or page)
    if content_type == "post":
        try:
            content_obj = PostDetail.objects.get(permalink=permalink)
        except PostDetail.DoesNotExist:
            return f"Error: Post with permalink '{permalink}' does not exist"
        assets = PostAsset.objects.filter(post=content_obj)
    else:  # page
        try:
            content_obj = StaticPage.objects.get(permalink=permalink)
        except StaticPage.DoesNotExist:
            return f"Error: Page with permalink '{permalink}' does not exist"
        assets = PageAsset.objects.filter(page=content_obj)

    # Find asset by filename pattern in the file field
    deleted = False

    for asset in assets:
        if asset.file and filename in asset.file.name:
            asset.delete()
            deleted = True
            break

    if deleted:
        return f"Media file '{filename}' deleted successfully from {content_type} '{permalink}'"
    else:
        return f"Error: Media file '{filename}' not found in {content_type} '{permalink}'"
