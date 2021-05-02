import datetime as dt

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД
        User.objects.create_user(username="name")
        Group.objects.create(title="testgroup2", slug='test-slug2',
                             description='Описание2')
        Group.objects.create(title="testgroup", slug='test-slug',
                             description='Описание')
        for i in range(1, 6):
            Post.objects.create(
                text=f'Тестовый текст{i}',
                pub_date=dt.datetime.today(),
                author=User.objects.get(username="name"),
                group=Group.objects.get(title="testgroup2")
            )
        for i in range(6, 12):
            Post.objects.create(
                text=f'Тестовый текст{i}',
                pub_date=dt.datetime.today(),
                author=User.objects.get(username="name"),
                group=Group.objects.get(title="testgroup")
            )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='name')
        self.group = Group.objects.get(title="testgroup")
        self.group_2 = Group.objects.get(title="testgroup2")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: name"
        templates_pages_names = {
            'index.html': reverse('posts:index'),
            'group.html': reverse('posts:group_posts',
                                  kwargs={'slug': 'test-slug'}),
            'new_post.html': reverse('posts:new_post'),
        }
        # Проверяем, что при обращении к name вызывается
        # соответствующий HTML-шаблон
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_post_shows_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:new_post'))
        response_edit = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'username': 'name', 'post_id': '1'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                form_field_edit = response_edit.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
                self.assertIsInstance(form_field_edit, expected)

    def test_index_list_page_shows_correct_context(self):
        """Шаблон index и group сформирован с правильным контекстом,
        а также проверка отображения созданного поста на главной
         странице и в группе"""
        response_name = {
            'index': reverse('posts:index'),
            'group': reverse('posts:group_posts',
                             kwargs={'slug': 'test-slug'}),
            'profile': reverse('posts:profile',
                               kwargs={'username': 'name'}),
        }
        for template, reverse_name in response_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context['page'][0]
                task_text_0 = first_object.text
                task_pub_date_0 = (first_object.pub_date).replace(
                    microsecond=0)
                task_author_0 = first_object.author
                task_group_0 = first_object.group
                self.assertEqual(task_text_0, 'Тестовый текст11')
                self.assertEqual(task_pub_date_0,
                                 dt.datetime.today().replace(
                                     microsecond=0))
                self.assertEqual(task_author_0, self.user)
                self.assertEqual(task_group_0, self.group)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'username': 'name',
                                               'post_id': '1'})
        )
        self.assertEqual(response.context['post'].text, 'Тестовый текст1')
        self.assertEqual(response.context['post'].pub_date.replace(
            microsecond=0), dt.datetime.today().replace(microsecond=0))
        self.assertEqual(response.context['post'].author, self.user)
        self.assertEqual(response.context['post'].group, self.group_2)

    def test_post_not_equal_show_correct_context(self):
        """Проверка поста, не принадлежащего данной группе."""
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'test-slug2'}))
        first_object = response.context['page'][0]
        task_text_0 = first_object.text
        task_group_0 = first_object.group
        self.assertNotEqual(task_text_0, 'Тестовый текст11')
        self.assertNotEqual(task_group_0, self.group)

    def test_first_page_contains_ten_records(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_contains_one_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 1)
