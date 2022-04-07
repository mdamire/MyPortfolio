from datetime import datetime
from django.test import TestCase
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

from .models import BlogsPosts, BlogsTags
# Create your tests here.
class BlogTests(TestCase):

    def setUp(self) -> None:
        self.bt1 = BlogsTags(name="General") 
        self.bt2 = BlogsTags(name="django")
        self.bt1.save()
        self.bt2.save()

        self.bp1 = BlogsPosts (  
                title='blog 1', 
                sub_title="this is blog 1", 
                url_param="blog_1",
                body="This is blog 1 body",
                update_date=timezone.datetime.now(),
                publish_date=timezone.datetime.now()
            )
        self.bp2 = BlogsPosts (  
                title='blog 2', 
                sub_title="this is blog 2", 
                url_param="blog_2",
                body="This is blog 2 body",
                update_date=timezone.datetime.now(),
                publish_date=timezone.datetime.now()
            )

        self.bp3 = BlogsPosts (  
                title='blog 3', 
                sub_title="this is blog 3", 
                url_param="blog_3",
                body="This is blog 3 body",
                update_date=timezone.datetime.now(),
                publish_date=timezone.datetime.now(),
                is_published=False
            )
        self.bp1.save()
        self.bp2.save()
        self.bp3.save()
        self.bp1.tags.add(self.bt1)
        self.bp2.tags.add(self.bt2)
        self.bp2.tags.add(self.bt1, self.bt2)
        self.bp1.save()
        self.bp2.save()
        self.bp3.save()

    def test_blogpost(self):
        bp = BlogsPosts.objects.all()
        self.assertEqual(len(bp), 3)
        self.assertEqual(bp[0].is_published, True)

        bp1 = BlogsPosts.objects.get(url_param="blog_3")
        self.assertEqual(bp1.is_published, False)

    def test_list_page_response(self):
        res = self.client.get(reverse('blogs:blogs'))
        self.assertEqual(res.status_code, 200)

    def test_list_page_content(self):
        res = self.client.get(reverse('blogs:blogs'))
        self.assertQuerysetEqual(res.context['post_list'], [self.bp1, self.bp2  ])

        self.assertContains(res, self.bp1.title)
        self.assertContains(res, self.bp1.sub_title)
        self.assertContains(res, self.bp2.title)
        self.assertContains(res, self.bp2.sub_title)

    def test_detail_page_response(self):
        with self.assertRaises(NoReverseMatch):
            res = self.client.get(reverse('blogs:details'))

        res = self.client.get(reverse('blogs:details', args={self.bp2.url_param}))
        self.assertEqual(res.context['post'].id, self.bp2.id)

        self.assertContains(res, self.bp2.title)
        self.assertContains(res, self.bp2.body)

        res = self.client.get(reverse('blogs:details', args={'random_one'}))
        self.assertEqual(res.status_code, 404)

        res = self.client.get(reverse('blogs:details', args={self.bp3.url_param}))
        self.assertEqual(res.status_code, 404)