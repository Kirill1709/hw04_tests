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
        cls.post_2 = Post.objects.create(
            text='Тестовый текст2',
            author=User.objects.get(username="name"),
            group=cls.group_2
        )
        cls.post_1 = Post.objects.create(
            text='Тестовый текст1',
            author=User.objects.get(username="name"),
            group=cls.group
        )
        cls.response_name = {
            reverse('posts:index'): 'index',
            reverse('posts:group_posts',
                    kwargs={'slug': cls.group.slug}): 'group',
            reverse('posts:profile',
                    kwargs={'username': cls.user.username}): 'profile',
        }
        cls.templates_pages = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug': cls.group.slug}): 'group.html',
            reverse('posts:new_post'): 'posts/new_post.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)

    def checks_the_fields_of_the_post(self, post, expected_post):
        """Проверка ожидаемых и действительных значений."""
        post_text_0 = expected_post.text
        post_pub_date_0 = (expected_post.pub_date).replace(
            microsecond=0)
        post_author_0 = expected_post.author
        post_group_0 = expected_post.group
        self.assertEqual(post_text_0, post.text),
        self.assertEqual(
            post_pub_date_0,
            dt.datetime.today().replace(
                microsecond=0)),
        self.assertEqual(post_author_0, self.user),
        self.assertEqual(post_group_0, post.group)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in PostPagesTests.templates_pages.items():
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
        for reverse_name, _ in PostPagesTests.response_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                post = response.context['page'][0]
                expected_post = self.post_1
                self.checks_the_fields_of_the_post(post, expected_post)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'username': 'name',
                                               'post_id': '1'})
        )
        post = response.context['post']
        expected_post = self.post_2
        self.checks_the_fields_of_the_post(post, expected_post)

    def test_post_not_equal_show_correct_context(self):
        """Проверка поста, не принадлежащего данной группе."""
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'test-slug2'}))
        post = response.context['page'][0]
        expected_post = self.post_2
        self.checks_the_fields_of_the_post(post, expected_post)


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
        posts = [Post(
            text=f'Тестовый текст{i}',
            author=cls.user,
            group=cls.group_2) for i in range(1, 12)]
        # for i in range(1, 12):
        #     post = Post(text=f'Тестовый текст{i}',
        #                 author=cls.user,
        #                 group=cls.group_2)
        #     posts.append(post)
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_contains_one_records(self):
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 1)
