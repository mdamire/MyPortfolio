# MyPortfolio

**Build your portfolio or any static site with AI.**

MyPortfolio is a Django-based portfolio website that comes as an empty slate, containing only a navbar and post list page. Everything else is created dynamically through AI integration. Create content in HTML, JavaScript, and CSS with AI assistance. Build posts, pages, homepage sections, and global assets like color schemes—all with AI. Features built-in Model Context Protocol (MCP) integration with OAuth for powerful and easy content creation. Includes an admin page for manual content management.

---

## 🚀 Quick Start

### Development Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mdamire/MyPortfolio.git
   cd MyPortfolio
   ```

2. **Start with Docker Compose:**
   ```bash
   docker compose up
   ```

   Or specify a custom port:
   ```bash
   PORT=8001 docker compose up
   ```

3. **Access the application:**
   - Navigate to [http://localhost:8000](http://localhost:8000) (or your custom port)
   - Admin panel: [http://localhost:8000/admin](http://localhost:8000/admin)

---

### Production Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mdamire/MyPortfolio.git
   cd MyPortfolio
   ```

2. **Create environment file:**
   ```bash
   touch .env
   ```

   Add the following environment variables to `.env`:
   ```env
   DB_NAME=myportfolio
   DB_USER=myportfolio-user
   DB_PASSWORD=portfolio-pass-42
   ALLOWED_HOST=your-domain.com,www.your-domain.com,127.0.0.1
   CSRF_TRUSTED_ORIGINS=http://your-domain.com,https://your-domain.com,http://www.your-domain.com,https://www.your-domain.com
   SECRET_KEY='your-secret-key-here'
   ```

   > **Note:** Replace `your-domain.com` with your actual domain and generate a secure `SECRET_KEY`.

3. **Create static and media directories:**
   ```bash
   sudo mkdir -p /app/staticfiles
   sudo chown www-data:www-data /app/staticfiles
   sudo chmod 755 /app/staticfiles

   sudo mkdir -p /app/mediafiles
   sudo chown www-data:www-data /app/mediafiles
   sudo chmod 755 /app/mediafiles
   ```

4. **Build and start the application:**
   ```bash
   docker compose -f docker-compose.prod.yml up --build
   ```

---

## 👤 Create Admin User

After installation, create an admin user to access the Django admin panel:

**Development:**
```bash
docker compose run web python manage.py createsuperuser
```

**Production:**
```bash
docker compose -f docker-compose.prod.yml run web python manage.py createsuperuser
```

Access the admin panel at `/admin` and login with your credentials.

---

## 🤖 MCP Integration (AI-Powered Content Creation)

### Connect with MCP

- **MCP Endpoint:** `/mcp`
- Use as an HTTP MCP server for any AI client
- OAuth authentication required (use your admin credentials)

### Available MCP Tools

#### **Posts**
- `create_post` - Create new blog posts with HTML content, tags, and assets
- `get_post` - Retrieve post details and associated assets
- `list_posts` - List posts with filtering by publication status and tags
- `update_post` - Update existing posts

#### **Pages**
- `create_page` - Create static pages with custom content
- `get_page` - Retrieve page details and assets
- `list_pages` - List all static pages
- `update_page` - Update existing pages

#### **Homepage Sections**
- `create_homepage_section` - Create homepage sections
- `get_homepage_section` - Retrieve section details and shared assets
- `list_homepage_sections` - List all active homepage sections
- `update_homepage_section` - Update existing sections

#### **Assets**
- `create_site_asset` - Create CSS, JavaScript, images, or any file assets
  - CSS/JS files are automatically linked as static resources
  - Other files (images, JSON, etc.) are available as Django template context variables
  - Can be scoped to posts, pages, homepage sections, or globally
- `delete_site_asset` - Remove assets

### Creating Content with AI

#### **Posts**
Ask AI to create a post. It should generate:
- HTML content
- JavaScript and CSS as assets
- Appropriate tags

Posts are created as drafts. Review them in the admin panel and publish manually by selecting the post and running the "publish post" action.

#### **Pages**
Ask AI to create a page with:
- HTML, JavaScript, and CSS content
- Optional navbar integration

#### **Homepage**
The homepage is composed of sections. Ask AI to create sections with:
- HTML content
- JavaScript and CSS (shared across all homepage sections)

#### **Assets**
Assets can be:
- **Scoped:** Linked to specific posts, pages, or homepage sections
- **Global:** Available across the entire site (useful for color schemes, global CSS/JS)

CSS and JavaScript files are automatically linked to their pages. Images, audio, and video files are accessible as Django template context variables (e.g., `{{ asset_key }}` provides a file object).

---

## 📋 Manual Content Management

### Admin Interface

Login at `/admin` to manually manage:
- Homepage sections
- Static pages
- Blog posts
- Site assets
- Tags

### Site Assets

Upload files (images, PDFs, CSS, JS, etc.) to be incorporated into your content. Assets are stored with unique keys and can be:
- Automatically linked (CSS/JS files)
- Used as Django template variables (images, media files)

**Example:** An asset with key `mycv` can be accessed as `{{ mycv }}` in templates, providing a file object with all file properties.

---

## 🏗️ Content Structure

### Homepage

The homepage is structured with multiple sections, each with:
- **Content:** HTML content (supports Django templates)
- **Navbar Title:** Optional title for navbar link
- **Serial:** Determines order of appearance

### Posts

Blog posts include:
- **Permalink:** URL-friendly identifier
- **Heading:** Post title
- **Tags:** Color-coded labels for categorization
- **Introduction:** Brief summary for post list page
- **Content:** Full HTML content
- **Include Sublinks:** Auto-generated table of contents from headers
- **Is Published:** Control visibility
- **Metadata:** Publication date, view count, related posts

**Sublinks** are automatically generated from heading tags (H1-H6) in sequential order, creating nested sections for easy navigation.

### Static Pages

Create custom pages with:
- **Permalink:** Custom URL
- **Heading:** Page title
- **Content:** HTML content (supports Django templates)
- **Navbar Integration:** Optional navbar title and position

---

## 🛠️ Technical Details

- **Framework:** Django
- **Database:** MySQL 8.0
- **Web Server:** Gunicorn (production)
- **Containerization:** Docker & Docker Compose
- **Content Editing:** Dynamic HTML, CSS, JS
- **Template Engine:** Django Templates
- **MCP Server:** Built-in HTTP MCP with OAuth

---

## 📖 License

This project is open source and available under the MIT License.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
