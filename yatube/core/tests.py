from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class CoreURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_404_uses_custom_template(self):
        settings.DEBUG = False
        response = self.authorized_client.get('page_404/')
        self.assertTemplateUsed(response, 'core/404.html')
