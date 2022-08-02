from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.urls import reverse

from ..models import Comment, Follow, Post
from .fixtures.fixture_data import Settings

User = get_user_model()


class PostViewsTests(Settings):

    def setUp(self):
        self.TEMPLATES_PAGES_NAMES = {
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:home'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
        }
        self.TEMPLATES_PAGES_NAMES_CONTEXT = (
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
            reverse('posts:home'),
        )
        self.FORM_FIELDS = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        self.PAGE_GROUP1 = reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}
        )
        self.PAGE_GROUP2 = reverse(
            'posts:group_list',
            kwargs={'slug': self.group2.slug})

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_pages_names = self.TEMPLATES_PAGES_NAMES
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_group_list_profile_show_correct_context(self):
        """Шаблон home, group_list, profile сформирован с правильным
        контекстом."""
        cache.clear()
        for reverse_name in self.TEMPLATES_PAGES_NAMES_CONTEXT:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context['page_obj'][0]
                post_text = first_object.text
                post_group = first_object.group.title
                post_author = first_object.author.username
                post_image = first_object.image
                self.assertEqual(post_text, self.post.text)
                self.assertEqual(post_group, self.post.group.title)
                self.assertEqual(post_author, self.user.username)
                self.assertEqual(post_image, 'posts/small.gif')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context['post'].text, self.post.text)
        self.assertEqual(
            response.context['post'].group.title, self.post.group.title)
        self.assertEqual(
            response.context['post'].author.username, self.user.username)
        self.assertEqual(
            response.context['post'].image, 'posts/small.gif')

    def test_edit_post_get_correct_contex(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        post = self.post
        page = reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        response = self.authorized_client.get(page)
        self.assertEqual(response.context['form'].instance, post)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        for value, expected in self.FORM_FIELDS.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_added_with_group_exists_on_pages(self):
        """Если при создании поста указать группу, то этот пост появляется
        на главной странице сайта, на странице выбранной группы, в профайле
        пользователя."""
        cache.clear()
        post2 = Post.objects.create(
            text='Пост из формы',
            author=self.user,
            group=self.group)
        for page in self.TEMPLATES_PAGES_NAMES_CONTEXT:
            response = self.authorized_client.get(page).context['page_obj']
            self.assertIn(
                post2, response, f'поста {post2} нет на странице {page}'
            )

    def test_comment_exists_on_page_detail(self):
        """Проверка, что после успешной отправки комментарий появляется на
        странице поста."""
        post = get_object_or_404(Post, pk=1)
        comment = Comment.objects.create(
            text='Тестовый коммент',
            post=post,
            author=self.user
        )
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        ).context['comments']
        self.assertIn(
            comment, response, 'Коммента нет'
        )

    def test_post_added_with_group_not_in_wrong_group(self):
        """Проверка, что созданный пост не попал в группу, для которой не был
        предназначен."""
        post2 = Post.objects.create(
            text='Пост из формы',
            author=self.user,
            group=self.group2)

        response = (
            self.authorized_client.get(self.PAGE_GROUP1).context['page_obj']
        )
        response2 = (
            self.authorized_client.get(self.PAGE_GROUP2).context['page_obj']
        )
        self.assertNotIn(
            post2, response, f'пост {post2} на странице "Тестовая группа"'
        )
        self.assertIn(
            post2, response2,
            f'поста {post2} нет на странице "Тестоваягруппа 2"'
        )

    def test_cache_index(self):
        """Проверка хранения и очищения кэша для index."""
        posts = self.authorized_client.get('/').content
        Post.objects.all().delete()
        posts2 = self.authorized_client.get('/').content
        self.assertEqual(posts2, posts)

    def test_authorized_user_follow_unfollow(self):
        """Авторизованный пользователь может подписываться на других
        пользователей и удалять их из подписок."""
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.user2})
        )

        self.assertTrue(Follow.objects.filter(
            user=self.user, author=self.user2).exists())
        self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.user2})
        )
        self.assertFalse(Follow.objects.filter(
            user=self.user, author=self.user2).exists())

    def test_follow_new_post_appears_for_followers(self):
        """Новая запись пользователя появляется в ленте тех, кто на него
        подписан и не появляется в ленте тех, кто не подписан."""
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.user2})
        )
        new_post = Post.objects.create(
            text='Пост из формы',
            author=self.user2,
            group=self.group)
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        response2 = self.authorized_client2.get(
            reverse('posts:follow_index')
        )
        self.assertIn(new_post, response.context['page_obj'])
        self.assertNotIn(new_post, response2.context['page_obj'])
