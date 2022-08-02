import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from posts.models import Comment, Post
from posts.tests.fixtures.fixture_data import Settings

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostFormTests(Settings):
    def setUp(self) -> None:
        self.PAGE_CREATE = reverse('posts:post_create')
        self.PAGE_CREATE_REDIRECT = reverse(
            'posts:profile', kwargs={'username': self.user})
        self.PAGE_EDIT = reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}
        )
        self.PAGE_EDIT_REDIRECT = reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}
        )
        self.PAGE_GROUP1 = reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}
        )
        self.form_data = {
            'text': 'Тестовый пост из формы',
            'group': self.group2.id,
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_create(self):
        """Валидная форма создает запись в Post."""
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        form_data = {'text': 'Тестовый пост из формы', 'group': self.group.id}
        response = self.authorized_client.post(
            self.PAGE_CREATE, data=form_data, follow=True
        )
        self.assertEqual(Post.objects.count(), 1)
        self.assertRedirects(response, self.PAGE_CREATE_REDIRECT)
        self.assertTrue(Post.objects.filter(**form_data).exists())

    def test_form_fields_labels(self):
        """Проверка переопределенных  labels и help_texts в форме"""
        text_label = self.form.fields['text'].label
        group_label = self.form.fields['group'].label
        group_help_text = self.form.fields['group'].help_text
        self.assertEquals(text_label, 'Текст поста')
        self.assertEquals(group_label, 'Группа')
        self.assertEquals(
            group_help_text, 'Группа, к которой будет относиться пост')

    def test_post_edit(self):
        """Валидная форма со страницы редактирования поста сохраняет
        изменения"""
        form_data = self.form_data
        response = self.authorized_client.post(
            self.PAGE_EDIT, data=form_data, follow=True
        )
        self.assertRedirects(response, self.PAGE_EDIT_REDIRECT)
        self.assertTrue(Post.objects.filter(**form_data).exists())
        post = get_object_or_404(Post, pk=1)
        self.assertEquals(post.author, self.user)
        response2 = self.authorized_client2.get(
            self.PAGE_EDIT, data=form_data, follow=True
        )
        self.assertRedirects(response2, self.PAGE_EDIT_REDIRECT)
        response3 = (
            self.authorized_client.get(self.PAGE_GROUP1).context['page_obj']
        )
        self.assertNotIn(
            post, response3, f'пост {post} на странице {self.group.title}'
        )

    def test_guest_client_cant_edit_post(self):
        """Не авторизированный клиент не может редактировать записи"""
        form_data = self.form_data
        response = self.guest_client.post(
            self.PAGE_EDIT, data=form_data, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, (reverse('users:login') + '?next=' + self.PAGE_EDIT))
        self.assertFalse(Post.objects.filter(**form_data).exists())

    def test_guest_client_cant_comment_post(self):
        """Не авторизированный клиент не может комментировать записи"""
        post = get_object_or_404(Post, pk=1)
        form_data = {
            'text': 'Тестовый коммент',
            'post': post,
            'author': self.user
        }
        response = self.guest_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': post.id}
            ), data=form_data, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            (reverse('users:login') + '?next=' + reverse(
                'posts:add_comment', kwargs={'post_id': post.id})))
        self.assertFalse(Comment.objects.filter(**form_data).exists())

    def test_comment_create(self):
        """Валидная форма создает комментарий для выбранного Post."""
        Comment.objects.all().delete()
        self.assertEqual(Comment.objects.count(), 0)
        post = get_object_or_404(Post, pk=1)
        form_data = {
            'text': 'Тестовый коммент',
            'post': post,
            'author': self.user
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': post.id}
            ), data=form_data, follow=True
        )
        self.assertEqual(Comment.objects.count(), 1)
        self.assertRedirects(response, self.PAGE_EDIT_REDIRECT)
        self.assertTrue(Comment.objects.filter(**form_data).exists())
