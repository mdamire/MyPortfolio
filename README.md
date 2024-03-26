# MyPortfolio

### Overview

The portfolio website is built on Django, offering a highly dynamic approach to content creation and management. It doesn't have any hardcoded content.
The website allows users to dynamically create homepage layouts, static pages, and posts using the TinyMCE editor within the Django admin interface. 
Additionally, the website enables to dynamically add CSS file for any fine customization without deploying the code. The code is easy to understand and modify.


### Installation:

#### Development:

1. Clone the repository from git:

   ```bash
   $ git clone https://github.com/mdamire/MyPortfolio.git
   ```

2. Create a virtual environment to isolate the installation:

   ```bash
   $ python -m venv <path>/mysite
   ```

3. Activate the virtual environment:

   ```bash
   $ source <path>/mysite/bin/activate
   ```

4. Navigate to the project directory and install dependencies:

   ```bash
   $ pip install -r requirements.txt
   ```

5. Migrate the database structure:

   ```bash
   $ python manage.py migrate
   ```

6. Run the development server and navigate to [http://localhost:8000/](http://localhost:8000/):

   ```bash
   $ python manage.py runserver
   ```

#### Production:

- Yet to come.


## Documentation:

### Site Assets

Users can upload various files such as images and PDFs to be incorporated into the website's content. These assets are stored with unique keys, making them easily accessible within the content. Additionally, with a key `style` , users can add CSS files that are immediately applied to the content.

If the django template rendering in on, these assets are passed as context where key is the context variable. So, an asset with key `mycv` can be accessed as `{{mycv}}` which is a file object and has file properties.

#### "Site assests" in "COMMON" section of admin:
- **Key:** Identifies uploaded files for integration into content.
- **File:** File to be uploaded, including images, PDFs, etc.

### Home Page

The homepage can be structured as a single-page design with multiple sections or as a traditional one-page layout. Sections are populated from the "Home Page Sections" model in the admin interface, allowing for seamless customization.

#### Properties of "Home Page Sections" in Pages:

- **Content:** Users can create content using the TinyMCE editor, allowing for rich text formatting and media embedding.
- **Requires Rendering:** Toggle to enable processing of Django template syntax within the content.
- **Navbar Title:** Title used for the navigation bar link associated with the section.
- **Serial:** Determines the order of appearance on the homepage and in the navigation bar.

### Post List Page

This page displays a list of posts with sorting and filtering functionality based on tags and other properties. Pagination is implemented to manage large numbers of posts efficiently.

### Post Detail Page

Posts are structured for readability and navigation ease. Users can create posts using the "Post Details" model in the admin interface.

#### Sections:

- **Meta:** Displays metadata such as publication date, view count, and associated tags.
- **Tags:** Allows for categorization and organization of posts.
- **Heading:** Title of the post.
- **Sublink:** Automatically generated links within the post, facilitating navigation. 
Sublinks are generated from the heading tags used in the post's content. By keeping headings in a sequential manner, users can create nested sections within their posts. For instance, if an H3 heading is used for a section, any lower heading (in HTML, actually a higher number) like H4 or H6 will be considered an inner section and will appear after the top section. This hierarchical organization enables users to present content in a structured and easily navigable format.
- **Body:** Main content of the post.
- **Related Posts:** Shows the five most related posts based on tags.

#### "Post Details" in "POSTS" section in admin:

- **Permalink:** Defines the URL structure for the post.
- **Heading:** Title of the post.
- **Tags:** Enables the assignment of descriptive labels to categorize the post.
- **Feature:** Integer value used for sorting posts.
- **Introduction:** A brief overview of the post displayed on the post list page.
- **Content:** Detailed content of the post.
- **Include Sublinks:** Toggle to display or hide sublinks within the post.
- **Is Published:** Toggle to control whether the post is displayed in the post list.
- **Publish Date:** Date when the post was published.

### Static Pages

Users can create multiple static pages, which can be linked in the navigation bar or accessed via their URL.

#### "Static Pages" in "PAGES" section of admin:

- **Content:** Content of the static page, editable using the TinyMCE editor.
- **Requires Rendering:** Toggle to enable processing of Django template syntax within the content.
- **Permalink:** Defines the URL structure for the static page.
- **Heading:** Title of the static page.
- **Navbar Title:** Title used for the navigation bar link associated with the static page.
- **Navbar Serial:** Determines the order of appearance in the navigation bar.
