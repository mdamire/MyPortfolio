from django.test import TestCase
from datetime import date
import os
from django.conf import settings
from mcp.registry import (
    create_post,
    get_post,
    publish_post,
    list_posts,
    update_post,
    delete_post,
    create_post_asset,
    list_post_assets,
    delete_post_asset,
)
from posts.models import PostDetail, PostTag
from common.models import SiteAsset


class TestPostFunctions(TestCase):
    def setUp(self):
        """Set up test data."""
        self.tag1 = PostTag.objects.create(
            label="Python", color="white", bg_color="blue"
        )
        self.tag2 = PostTag.objects.create(
            label="Django", color="white", bg_color="green"
        )

    def test_create_and_get_post(self):
        """Test creating a post and retrieving it."""
        # Create a post using existing tag labels
        response = create_post(
            permalink="test-post",
            heading="Test Post",
            content="<p>This is test content</p>",
            introduction="This is a test introduction",
            tags=["Python", "Django"],
        )

        self.assertEqual(response.permalink, "test-post")
        self.assertEqual(response.heading, "Test Post")
        self.assertEqual(response.is_published, False)
        self.assertEqual(response.feature, 0)
        self.assertIn("Python", response.tags)
        self.assertIn("Django", response.tags)

        # Get the post
        result = get_post("test-post")
        self.assertIsNotNone(result)

    def test_update_post(self):
        """Test updating a post."""
        # Create a post
        create_post(
            permalink="update-test",
            heading="Original Heading",
            content="<p>Original content</p>",
        )

        # Update the post
        response = update_post(
            permalink="update-test",
            heading="Updated Heading",
            content="<p>Updated content</p>",
            feature=10,
        )

        self.assertEqual(response.heading, "Updated Heading")
        self.assertEqual(response.content, "<p>Updated content</p>")
        self.assertEqual(response.feature, 10)

    def test_publish_post(self):
        """Test publishing a post."""
        # Create a draft post
        create_post(
            permalink="publish-test",
            heading="Publish Test",
            content="<p>Content to publish</p>",
        )

        # Publish the post
        response = publish_post("publish-test")

        self.assertTrue(response.is_published)
        self.assertEqual(response.publish_date, str(date.today()))

    def test_list_posts(self):
        """Test listing posts with filters."""
        # Create multiple posts
        create_post(permalink="post1", heading="Post 1", content="<p>Content 1</p>")
        create_post(
            permalink="post2",
            heading="Post 2",
            content="<p>Content 2</p>",
            tags=["Python"],
        )
        publish_post("post2")

        # List all posts
        all_posts = list_posts()
        self.assertEqual(len(all_posts.post_list), 2)

        # List only published posts
        published_posts = list_posts(is_published=True)
        self.assertEqual(len(published_posts.post_list), 1)

        # List posts by tag
        tagged_posts = list_posts(tag_id=self.tag1.id)
        self.assertEqual(len(tagged_posts.post_list), 1)

    def test_create_post_with_mixed_tag_formats(self):
        """Test creating a post with both existing tags (labels) and new tags (tuples)."""
        # Create a post with both existing tag labels and new tag tuples
        response = create_post(
            permalink="mixed-tags-post",
            heading="Mixed Tags Post",
            content="<p>Post with mixed tag formats</p>",
            tags=[
                "Python",  # Existing tag by label
                ("React", "white", "cyan"),  # New tag as tuple
                "Django",  # Existing tag by label
                ("Testing", "black", "yellow"),  # New tag as tuple
            ],
        )

        self.assertEqual(response.permalink, "mixed-tags-post")
        self.assertEqual(len(response.tags), 4)
        self.assertIn("Python", response.tags)
        self.assertIn("React", response.tags)
        self.assertIn("Django", response.tags)
        self.assertIn("Testing", response.tags)

        # Verify the new tags were created in the database
        self.assertTrue(PostTag.objects.filter(label="React").exists())
        self.assertTrue(PostTag.objects.filter(label="Testing").exists())

        # Verify the new tags have correct colors
        react_tag = PostTag.objects.get(label="React")
        self.assertEqual(react_tag.color, "white")
        self.assertEqual(react_tag.bg_color, "cyan")

    def test_delete_post(self):
        """Test deleting a post."""
        # Create a post
        create_post(
            permalink="delete-test",
            heading="Delete Test",
            content="<p>Content to delete</p>",
        )

        # Delete the post
        result = delete_post("delete-test")
        self.assertIn("deleted successfully", result)

        # Verify post is deleted
        self.assertFalse(PostDetail.objects.filter(permalink="delete-test").exists())


class TestAssetFunctions(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create a post for assets
        self.post = create_post(
            permalink="asset-test-post",
            heading="Asset Test Post",
            content="<p>Post with assets</p>",
        )
        self.created_files = []

    def tearDown(self):
        """Clean up created files."""
        # Clean up all assets and their files
        for asset in SiteAsset.objects.all():
            if asset.file:
                file_path = asset.file.path
                if os.path.exists(file_path):
                    os.remove(file_path)
                # Also remove the directory if empty
                dir_path = os.path.dirname(file_path)
                if os.path.exists(dir_path) and not os.listdir(dir_path):
                    os.rmdir(dir_path)

    def test_create_and_list_assets(self):
        """Test creating assets and listing them."""
        # Create CSS asset
        css_asset = create_post_asset(
            post_permalink="asset-test-post",
            key="custom_style",
            filename="custom.css",
            file_content="body { background: red; }",
            description="Custom CSS for the post",
        )

        self.assertEqual(css_asset.key, "custom_style")
        self.assertIn("custom.css", css_asset.file)

        # Create JS asset
        js_asset = create_post_asset(
            post_permalink="asset-test-post",
            key="custom_script",
            filename="custom.js",
            file_content="console.log('Hello');",
            description="Custom JS for the post",
        )

        self.assertEqual(js_asset.key, "custom_script")

        # List assets for the post
        assets = list_post_assets(post_permalink="asset-test-post")
        self.assertEqual(len(assets.post_asset_list), 2)

    def test_delete_asset(self):
        """Test deleting an asset."""
        # Create an asset
        asset = create_post_asset(
            post_permalink="asset-test-post",
            key="temp_asset",
            filename="temp.txt",
            file_content="Temporary content",
        )

        # Delete the asset
        result = delete_post_asset(asset.id)
        self.assertIn("deleted successfully", result)

        # Verify asset is deleted
        self.assertFalse(SiteAsset.objects.filter(id=asset.id).exists())
