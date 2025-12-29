from django.conf import settings

from mcp_serializer.features.prompt.result import PromptsResult
from common.models import SiteAsset
from .registry import registry


## Prompts
@registry.prompt()
def global_assets_prompt():
    """Manage global site assets (color schema, navbar design, global styling, etc.)"""
    base_dir = settings.BASE_DIR.parent

    result = PromptsResult()

    # Add built-in common CSS and JS files
    result.add_file_resource(
        file=f"{base_dir}/common/static/common/common.css",
        title="Base CSS for the entire website",
        description=(
            "Core styling for all pages across the website, ensuring consistency in appearance and "
            "user experience. This includes navbar design, color schema, and base styles. "
            "This is automatically loaded on every page."
        ),
    )

    result.add_file_resource(
        file=f"{base_dir}/common/static/common/common.js",
        title="Base JavaScript for the entire website",
        description=(
            "Core JavaScript functionality for all pages across the website, ensuring consistency in "
            "behavior and user experience. This is automatically loaded on every page."
        ),
    )

    # Add existing global assets (assets not linked to any specific post, page, or section)
    global_assets = SiteAsset.objects.filter(
        post__isnull=True,
        page__isnull=True,
        homepage_section__isnull=True,
        is_active=True,
    )

    for asset in global_assets:
        result.add_file_resource(
            file=asset.file,
            title=asset.description or f"Global asset: {asset.key}",
            description=f"Global asset '{asset.key}' available across the entire site.",
        )

    result.add_text(
        role=PromptsResult.Roles.USER,
        text="""Manage global assets that are shared across the entire website.

**Use this prompt when you need to:**
- Update global color schema or theme
- Modify navbar design or styling
- Change site-wide fonts, spacing, or layout
- Add/update global JavaScript functionality
- Manage shared images, logos, or icons
- Update global configuration files

**Global Assets Overview:**
Global assets are CSS, JS, images, JSON, or other files that are available across ALL pages, posts, and homepage sections.
Unlike page/post/section-specific assets, global assets are not linked to any particular content.

**When to Use Global Assets:**
- Site-wide styling or themes (color schema, typography, spacing)
- Navbar design and styling
- Global JavaScript functionality (analytics, common utilities)
- Shared images (logos, icons, backgrounds)
- Configuration files (JSON data used across multiple pages)
- Fonts or other resources used throughout the site

**Creating Global Assets:**
Use `create_site_asset` WITHOUT specifying any reference (no post_permalink, page_permalink, or homepage_section_name):

**For CSS/JS Files (automatically linked on all pages):**
- `create_site_asset(filename="global-theme.css", file_content=css_text)`
- `create_site_asset(filename="analytics.js", file_content=js_text)`
- These will be loaded on EVERY page automatically

**For Images, JSON, and other files (available as template variables):**
- `create_site_asset(filename="logo.png", file_content=base64_encoded_image)`
- `create_site_asset(filename="site-config.json", file_content=json_text)`
- Access in ANY template using: {{ filename_without_extension.url }}
- Example: {{ logo.url }} for "logo.png"

**File Content:**
- Binary files (images, fonts, audio): Provide base64-encoded content
- Text files (CSS, JS, JSON, TXT): Provide plain text content

**Built-in Global Assets:**
The following files are already available globally (referenced above as resources):
- `common.css` - Base styling for all pages (includes navbar design, color schema)
- `common.js` - Base JavaScript functionality for all pages
- Bootstrap 5 CSS and JavaScript are also loaded on all pages
- Any existing global assets are listed above as file resources

**Managing Global Assets:**

**To add a new global asset:**
```python
create_site_asset(
    filename="custom-global.css",
    file_content=css_text,
    description="Custom global styles"
)
```

**To update a global asset (e.g., change color schema or navbar design):**
1. Delete: `delete_site_asset(filename="custom-global.css")`
2. Create: `create_site_asset(filename="custom-global.css", file_content=new_css_text)`

**To delete a global asset:**
```python
delete_site_asset(filename="custom-global.css")
```

**Important Notes:**
- Global CSS/JS files are loaded BEFORE page/post/section-specific files
- This allows page-specific styles to override global styles
- Be careful with global assets as they affect the entire site
- Use specific assets (post, page, or section) when content is only needed in one place
- To update navbar design or color schema, create a new global CSS file or update existing ones
""",
    )
    return result
