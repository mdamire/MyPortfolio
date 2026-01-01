# MyPortfolio

**Build your portfolio or any static website with AI.**

MyPortfolio is a Django-based website that starts as an empty slate.
Out of the box, it includes only a navbar and a posts list page; everything else can be created with AI.

You create content as **HTML, CSS, and JavaScript**, letting AI design pages, posts, homepage sections, and even global styles like color schemes.
An admin panel is included for full manual control when needed.

AI integration is powered by **MCP (Model Context Protocol)** with OAuth, so you can connect your favorite AI client and start creating immediately.

---

## What you can build

- Blog posts with custom HTML, CSS, and JavaScript.
- Static pages (About, Projects, Contact, etc.).
- A homepage composed of reusable sections.
- Global styles and assets (themes, colors, shared JS/CSS).
- Images, audio, video, and other media assets.

AI generates the content — **you stay in control**.

---

## Quick Start (Local Development)

### Requirements
- Docker.
- Docker Compose.

### Run locally

```bash
git clone https://github.com/mdamire/MyPortfolio.git
cd MyPortfolio
docker compose up
```

Optional custom port:

```bash
PORT=8001 docker compose up
```

Then open:

- Website: [http://localhost:8000](http://localhost:8000) (or the custom port).
- Admin panel: [http://localhost:8000/admin](http://localhost:8000/admin).

---

## Production Setup (Docker)

1. **Clone the repository**.

```bash
git clone https://github.com/mdamire/MyPortfolio.git
cd MyPortfolio
```

2. **Create `.env` file**.

```bash
touch .env
```

Example `.env`:

```env
DB_NAME=myportfolio
DB_USER=myportfolio-user
DB_PASSWORD=portfolio-pass-42
ALLOWED_HOST=your-domain.com,www.your-domain.com,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
SECRET_KEY=your-secret-key
```

3. **Create static and media directories**.

```bash
sudo mkdir -p /app/staticfiles /app/mediafiles
sudo chown www-data:www-data /app/staticfiles /app/mediafiles
sudo chmod 755 /app/staticfiles /app/mediafiles
```

4. **Build and start**.

```bash
docker compose -f docker-compose.prod.yml up --build
```

---

## Create Admin User

You’ll need an admin account to manage content.

**Local**

```bash
docker compose run web python manage.py createsuperuser
```

**Production**

```bash
docker compose -f docker-compose.prod.yml run web python manage.py createsuperuser
```

Admin panel: [http://localhost:8000/admin](http://localhost:8000/admin).

---

## Using AI (MCP)

- **MCP endpoint:** [http://localhost:8000/mcp](http://localhost:8000/mcp).
- Works as an HTTP MCP server.
- OAuth authentication using your admin credentials.

---

## Creating Content with AI

### Homepage

The homepage is built from multiple sections, each with its own content, assets, and display order.

- Ask AI to create or update homepage sections.
- Sections are added to the navbar if a navbar title is provided.
- Sections can be activated or deactivated from the admin panel.
- CSS and JavaScript from active sections are shared across the entire homepage.
- Manage sections at:
  * [http://localhost:8000/admin/pages/homepagesection/](http://localhost:8000/admin/pages/homepagesection/)

### Pages

Pages are standalone static pages with a heading and content. They can be linked from anywhere on the site and optionally appear in the navbar.

- Ask AI to create a page.
- AI generates HTML content and related CSS/JS.
- You can ask AI to add the page to the navbar.
- Manage pages at:
  * [http://localhost:8000/admin/pages/staticpage/](http://localhost:8000/admin/pages/staticpage/)

### Posts

Posts are blog-style content with a heading, introduction, full HTML content, and tags. They are listed on http://localhost:8000/posts/ with pagination, filtering, sorting, and related posts based on shared tags.

- Ask AI to create a post.
- AI generates HTML content and related CSS/JS.
- Posts are created as **drafts**.
- Review and publish manually from admin:
  * Go to [http://localhost:8000/admin/posts/postdetail/](http://localhost:8000/admin/posts/postdetail/).
  * Select the post.
  * Select "Publish post" from the action dropdown and click Run.

### Assets

Assets are files used by your site, such as styles, scripts, and media. They can be created by AI or uploaded manually through the admin panel.

- You can create **images, audio, video, CSS, and JavaScript** files.
- **CSS and JavaScript** files are automatically loaded on the pages they belong to.
- **Media files** (images, audio, video, PDFs, etc.) are available in Django templates as context. The asset key is the context name and the value is a Python file object.
- Assets can be **scoped** to a post, page, or homepage section, or made **global**.
- **Global assets** are loaded on every page and are useful for things like themes, fonts, and color schemes.
- Manage all assets from:
   * [http://localhost:8000/admin/common/siteasset/](http://localhost:8000/admin/common/siteasset/)

---

## Tech Stack

- Django.
- MySQL.
- Docker & Docker Compose.
- Django Templates.
- MCP (HTTP + OAuth).

---

## License

MIT License.

---

## Contributing

Pull requests are welcome 🙂

