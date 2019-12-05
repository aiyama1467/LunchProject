from django.test import TestCase

from .models import User


class PostSignupTests(TestCase):

    def test_get(self):
        """
        getで通常のアクセスを行う.
        """
        response = self.client.get('/accounts/signup/')
        self.assertEqual(response.status_code, 200)
