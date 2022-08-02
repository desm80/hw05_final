from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from users.views import SignUp

User = get_user_model()


class UserURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.form = SignUp().form_class
        self.USER_CREATE_PAGE = reverse('users:signup')

        self.TEMPLATES = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse(
                'users:password_reset_form'
            ): 'users/password_reset_form.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            reverse('users:password_reset_confirm',
                    kwargs={
                        'uidb64': '123',
                        'token': 'skhjdskhd'
                    }
                    ): 'users/password_reset_confirm.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
            reverse(
                'users:password_change_form'
            ): 'users/password_change_form.html',
            reverse(
                'users:password_change_done'
            ): 'users/password_change_done.html',
            # тест логаут всегда в конце
            reverse('users:logout'): 'users/logged_out.html',
        }

    def test_users_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.TEMPLATES.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response, template, f'Шаблон {reverse_name} глючный')

    def test_users_signup_get_correct_context(self):
        response = self.guest_client.get(self.USER_CREATE_PAGE)
        self.assertEqual(response.context['form'].__class__, self.form)
        # self.assertIsInstance(response.context['form'].__class__, self.form)

    # def test_new_user_create(self):
    #     user_cnt = User.objects.all().count()
    #     print(user_cnt)
    #     response = self.guest_client.post(self.USER_CREATE_PAGE, kwargs={
    #         'first_name': 'Den',
    #         'last_name': 'Sm',
    #         'username': 'desm',
    #         'password1': 'pft,fk1234',
    #         'password2': 'pft,fk1234',
    #     })
    #
    #     print(response.context['form'].fields.__getitem__(
    #         'first_name').__doc__()
    #           )
    #     user_cnt2 = User.objects.all().count()
    #     print(user_cnt2)
    #     print(User.objects.all())
