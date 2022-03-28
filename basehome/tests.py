from django.test import TestCase
from django.urls import reverse

# Create your tests here.

class HomeTest(TestCase):

    def test_home_return(self):
        """To test if home page is working correctly
        """

        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Amir Ebrahim')