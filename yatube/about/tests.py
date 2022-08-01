from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.TEMPLATE_NAMES = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }

    def test_about_url_exists_at_desired_location_uses_correct_template(self):
        """Проверка доступности адресов и шаблонов приложения About."""
        for url, template in self.TEMPLATE_NAMES.items():
            response = self.guest_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(response.status_code, HTTPStatus.OK.value)
                self.assertTemplateUsed(response, template)
