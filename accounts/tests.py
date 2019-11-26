from django.test import TestCase

from .models import User


class PostSignupTests(TestCase):

    def test_get(self):
        """
        getで通常のアクセスを行う.
        """
        response = self.client.get('/accounts/signup/')
        self.assertEqual(response.status_code, 200)

    def test_create_new_account(self):
        test_email = 'test@example.com'
        test_password = 'warwetsrsrd12345'
        user = User.objects.create(email=test_email, password=test_password)

        response = self.client.get('/accounts/signup/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user.username)
        # パスワードはハッシュで保存されている
