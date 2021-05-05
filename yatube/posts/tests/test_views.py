import datetime as dt

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="name")
        cls.group_2 = Group.objects.create(
            title="testgroup2",
            slug='test-slug2',
            description='Описание2')
        cls.group = Group.objects.create(
            title="testgroup",
            slug='test-slug',
            description='Описание')
        Post.objects.create(
            text='Тестовый текст2',
            author=User.objects.get(username="name"),
            group=cls.group_2
        )
        Post.objects.create(
            text='Тестовый текст1',
            author=User.objects.get(username="name"),
            group=cls.group
        )
        cls.response_name = {
            reverse('posts:index'): 'index',
            reverse('posts:group_posts',
                    kwargs={'slug': 'test-slug'}): 'group',
            reverse('posts:profile',
                    kwargs={'username': 'name'}): 'profile',
        }
        cls.templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug': 'test-slug'}): 'posts/group.html',
            reverse('posts:new_post'): 'posts/new_post.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)

    def equal_fields(self, first_object, expected_text, expected_group):
        """Проверка ожидаемых и действительных значений."""
        post_text_0 = first_object.text
        post_pub_date_0 = (first_object.pub_date).replace(
            microsecond=0)
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        self.assertEqual(post_text_0, expected_text),
        self.assertEqual(
            post_pub_date_0,
            dt.datetime.today().replace(
                microsecond=0)),
        self.assertEqual(post_author_0, self.user),
        self.assertEqual(post_group_0, expected_group)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names.items():
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
        for reverse_name, template in self.response_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context['page'][0]
                expected_text = 'Тестовый текст1'
                expected_group = self.group
                self.equal_fields(first_object, expected_text, expected_group)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'username': 'name',
                                               'post_id': '1'})
        )
        first_object = response.context['post']
        expected_text = 'Тестовый текст2'
        expected_group = self.group_2
        self.equal_fields(first_object, expected_text, expected_group)

    def test_post_not_equal_show_correct_context(self):
        """Проверка поста, не принадлежащего данной группе."""
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'test-slug2'}))
        first_object = response.context['page'][0]
        expected_text = 'Тестовый текст2'
        expected_group = self.group_2
        self.equal_fields(first_object, expected_text, expected_group)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="name")
        cls.group_2 = Group.objects.create(
            title="testgroup2",
            slug='test-slug2',
            description='Описание2')
        cls.group = Group.objects.create(
            title="testgroup",
            slug='test-slug',
            description='Описание')
        Post.objects.bulk_create([
            Post(
                text='Тестовый текст1',
                author=cls.user,
                group=cls.group_2),
            Post(
                text='Тестовый текст2',
                author=cls.user,
                group=cls.group_2),
            Post(
                text='Тестовый текст3',
                author=cls.user,
                group=cls.group_2),
            Post(
                text='Тестовый текст4',
                author=cls.user,
                group=cls.group_2),
            Post(
                text='Тестовый текст5',
                author=cls.user,
                group=cls.group_2),
            Post(
                text='Тестовый текст6',
                author=cls.user,
                group=cls.group_2),
            Post(
                text='Тестовый текст7',
                author=cls.user,
                group=cls.group_2),
            Post(
                text='Тестовый текст8',
                author=cls.user,
                group=cls.group_2),
            Post(
                text='Тестовый текст9',
                author=cls.user,
                group=cls.group_2),
            Post(
                text='Тестовый текст10',
                author=cls.user,
                group=cls.group_2),
            Post(
                text='Тестовый текст11',
                author=cls.user,
                group=cls.group_2),
        ])

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_contains_one_records(self):
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 1)
