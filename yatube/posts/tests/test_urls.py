from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адреса task/test-slug/
        cls.post_1 = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create_user(username="name"),
            group=Group.objects.create(title="testgroup", slug='test-slug',
                                       description='Описание')
        )
        cls.post_2 = Post.objects.create(
            text='Тестовый текст2',
            author=User.objects.create_user(username="name2"),
            group=Group.objects.create(title="testgroup2", slug='test-slug2',
                                       description='Описание2')
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.get(username='name')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_task_added_url_exists_at_desired_location(self):
        """Страница /group/<slug>/ доступна любому пользователю."""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    # Проверяем доступность страниц для авторизованного пользователя
    def test_task_list_url_exists_at_desired_location(self):
        """Страница /new/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    # Проверяем редиректы для неавторизованного пользователя
    def test_task_list_url_redirect_anonymous(self):
        """Страница /new/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/new/'))

    def test_username_url_exists_at_desired_location(self):
        """Страница /<username>/ доступна любому пользователю."""
        response = self.guest_client.get('/name/')
        self.assertEqual(response.status_code, 200)

    def test_username_post_id_url_exists_at_desired_location(self):
        """Страница /<username>/<post_id> доступна любому пользователю."""
        response = self.guest_client.get('/name/1/')
        self.assertEqual(response.status_code, 200)

    def test_anonimus_post_edit_url_exists_at_desired_location(self):
        """Страница /<username>/<post_id>/edit
        доступна анонимному пользователю."""
        response = self.guest_client.get('/name/1/edit/')
        self.assertEqual(response.status_code, 302)

    def test_author_post_edit_url_exists_at_desired_location(self):
        """Страница /<username>/<post_id>/edit доступна автору поста."""
        response = self.authorized_client.get('/name/1/edit/')
        self.assertEqual(response.status_code, 200)

    def test_not_author_post_edit_url_exists_at_desired_location(self):
        """Страница /<username>/<post_id>/edit доступна автору поста."""
        response = self.authorized_client.get('/name2/2/edit/')
        self.assertEqual(response.status_code, 302)

    def test_anonimus_redirect_post_edit_url_exists_at_desired_location(self):
        """Страница /<username>/<post_id>/edit/ доступна
        анонимному пользователю."""
        response = self.authorized_client.get('/name2/2/edit/')
        self.assertRedirects(
            response, ('/name2/2/'))

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'index.html',
            '/group/test-slug/': 'group.html',
            '/new/': 'new_post.html',
            '/name/1/edit/': 'new_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
