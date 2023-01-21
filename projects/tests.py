from django.test import TestCase
from django.urls import reverse, NoReverseMatch
from django.utils import timezone

from .models import ProjectPosts
# Create your tests here.

class TestProject(TestCase):

    def setUp(self) -> None:
        self.p1 = ProjectPosts.objects.create(
            title = 'post 1',
            sub_title = 'this is post 1',
            url_param = 'post_1',
            body = 'This is post 1 body',
            update_date = timezone.datetime.now(),
            publish_date = timezone.datetime.now(), 
        )
        self.p2 = ProjectPosts.objects.create(
            title = 'post 2',
            sub_title = 'this is post 2',
            url_param = 'post_2',
            body = 'This is post 2 body',
            update_date = timezone.datetime.now(),
            publish_date = timezone.datetime.now(),
            is_published = False,
        )
        self.p3 = ProjectPosts.objects.create(
            title = 'post 3',
            sub_title = 'this is post 1',
            url_param = 'post_3',
            update_date = timezone.datetime.now(),
            publish_date = timezone.datetime.now(),
        )
        self.p4 = ProjectPosts.objects.create(
            title = 'post 4',
            sub_title = 'this is post 4',
            url_param = 'post_4',
            body = 'This is post 4 body',
            update_date = timezone.datetime.now(),
            publish_date = timezone.datetime.now(), 
            parent = self.p3,
            serial = 2,
        )
        self.p5 = ProjectPosts.objects.create(
            title = 'post 5',
            sub_title = 'this is post 1',
            url_param = 'post_5',
            body = 'This is post 1 body',
            update_date = timezone.datetime.now(),
            publish_date = timezone.datetime.now(), 
            parent = self.p3,
            serial = 1,
        )

    def test_response(self):
        res = self.client.get(reverse('projects:projects'))
        self.assertEqual(res.status_code, 200)

        res = self.client.get(reverse('projects:details', args=[self.p1.url_param]))
        self.assertEqual(res.status_code, 200) 

    def test_defaults(self):
        self.assertEqual(self.p1.is_parent, True)
        self.assertEqual(self.p1.url_name, 'projects:details')
        self.assertEqual(self.p1.is_published, True)

    def test_project_list(self):
        res = self.client.get(reverse('projects:projects'))
        
        self.assertQuerysetEqual(res.context['post_list'], [self.p1, self.p3])

        self.assertContains(res, self.p1.title)
        self.assertContains(res, self.p1.sub_title)
        self.assertContains(res, self.p3.title)
        self.assertContains(res, self.p3.sub_title)

    def test_details(self):
        with self.assertRaises(NoReverseMatch):
            res = self.client.get(reverse('projects:details'))

        res = self.client.get(reverse('projects:details', args=[self.p1.url_param]))
        self.assertContains(res, self.p1.body)
        self.assertContains(res, self.p1.title)

        res = self.client.get(reverse('projects:details', args=[self.p3.url_param]))
        self.assertEqual(res.status_code, 200)

        res = self.client.get(reverse('projects:details', args=[self.p4.url_param]))
        self.assertIsNotNone(res.context['sidebar'])

        #available even though not published
        res = self.client.get(reverse('projects:details', args=[self.p2.url_param]))
        self.assertEqual(res.status_code, 200)
