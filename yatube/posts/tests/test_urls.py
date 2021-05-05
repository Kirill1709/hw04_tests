from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username="name")
        cls.user_2 = User.objects.create_user(username="name2")
        cls.post_1 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user_1,
            group=Group.objects.create(title="testgroup", slug='test-slug',
                                       description='Описание')
        )
        cls.post_2 = Post.objects.create(
            text='Тестовый текст2',
            author=cls.user_2,
            group=Group.objects.create(title="testgroup2", slug='test-slug2',
                                       description='Описание2')
        )
        cls.url_guest_user = (
            '/',
            '/group/test-slug/',
            '/name/',
            '/name/1/',
        )
        cls.url_authorized_user = (
            '/new/',
            '/name/1/edit/',
        )
        cls.url_redirect_anonymous = {
            '/new/': '/auth/login/?next=/new/',
            '/name/1/edit/': '/auth/login/?next=/name/1/edit/',
        }
        cls.templates_url_authorized_client = {
            '/new/': 'new_post.html',
            '/name/1/edit/': 'new_post.html',
        }
        cls.templates_url_guest_client = {
            '/': 'index.html',
            '/group/test-slug/': 'group.html',
            '/name/': 'profile.html',
            '/name/1/': 'post.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user_1)

    def test_url_guest_user_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        for url in self.url_guest_user:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_task_list_url_exists_at_desired_location(self):
        """Страница /new/ доступна авторизованному пользователю."""
        for url in self.url_authorized_user:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anonimus_post_edit_url_exists_at_desired_location(self):
        """Страницы не доступны анонимному пользователю(редирект)."""
        for url, url_redirect in self.url_redirect_anonymous.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, url_redirect)

    def test_anonimus_redirect_post_edit_url_exists_at_desired_location(self):
        """Страница /<username>/<post_id>/edit/ не доступна
        не автору поста."""
        response = self.authorized_client.get('/name2/2/edit/')
        self.assertRedirects(
            response, ('/name2/2/'))

    def test_urls_authorized_client_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон
        авторизованного пользователя."""
        for adress, template in self.templates_url_authorized_client.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_guest_client_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон
        анонимного пользователя."""
        for adress, template in self.templates_url_guest_client.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
