from random import randint

# from yatube.settings import POSTS_PER_PAGE
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

NUM_POSTS = randint(11, 19)
MODULO_POSTS = NUM_POSTS % settings.POSTS_PER_PAGE
ERROR_MSG = 'Количество постов не соответствует ожидаемому'


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.guest_client = Client()
        posts_list = [
            Post(text=f'Пост {i}', group=cls.group,
                 author=cls.user) for i in range(NUM_POSTS)
        ]
        posts = Post.objects.bulk_create(posts_list)
        cls.paginator = Paginator(posts, settings.POSTS_PER_PAGE)
        cls.TEMPLATES_PAGES_NAMES_CONTEXT = (
            reverse('posts:group_list', kwargs={
                'slug': cls.group.slug}),
            reverse('posts:profile', kwargs={'username': cls.user}),
            reverse('posts:home'),
        )

    def test_correct_page_context_guest_client(self):
        """Проверка количества постов на страницах для не авторизованного
        пользователя."""

        self.assertTrue(NUM_POSTS > settings.POSTS_PER_PAGE,
                        'Недостаточно постов для проверки пагинации')
        self.assertTrue(self.paginator.num_pages == 2,
                        'Для проверки пагинации предоставлено больше двух '
                        'страниц')

        for reverse_name in self.TEMPLATES_PAGES_NAMES_CONTEXT:
            response_page_1 = self.guest_client.get(reverse_name)
            response_page_2 = self.guest_client.get(reverse_name + '?page=2')
            cnt1 = len(response_page_1.context['page_obj'])
            cnt2 = len(response_page_2.context['page_obj'])

            self.assertEqual(cnt1, settings.POSTS_PER_PAGE, ERROR_MSG)
            self.assertEqual(cnt2, MODULO_POSTS, ERROR_MSG)
