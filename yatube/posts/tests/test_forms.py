import datetime as dt

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm

from ..models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create_user(username="name",
                                            email="email@mail.com",
                                            password="Pass12345"),
            group=Group.objects.create(title="testgroup", slug='test-slug',
                                       description='Описание')
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='name')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.get(title="testgroup")

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст2',
            'pub_date': dt.datetime.today(),
            'author': self.user,
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст2',
                group=self.group.id
            ).exists()
        )

    def test_change_post(self):
        """Валидная форма редактирует запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст3',
            'pub_date': dt.datetime.today(),
            'author': self.user,
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'username': 'name',
                                               'post_id': '1'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/name/1/')
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст3',
                group=self.group.id
            ).exists()
        )
