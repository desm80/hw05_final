from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UserURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.USER_URLS = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        self.USER_REDIRECT_URLS = {
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
        }

    def test_user_urls_exists_at_desired_location(self):
        """Проверяем урлы приложения User на доступность и соответствие
        шаблонам"""
        for url, template in self.USER_URLS.items():
            response = self.guest_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
        for url, template in self.USER_REDIRECT_URLS.items():
            response = self.authorized_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
