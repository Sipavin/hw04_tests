from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PaginatorViewsTest(TestCase):
    """Тест паджинатора"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание',
        )
        for i in range(1, 15):
            cls.post = Post.objects.create(
                text=f'Тестовый текст{i}',
                author=cls.user,
                group=cls.group,
            )

    def setUp(self):
        self.guest_client = Client()

    def test_first_index_page_contains_10_posts(self):
        """На первой странице index выводится 10 постов"""
        response = self.guest_client.get(
            reverse('posts:index')
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_index_page_contains_4_posts(self):
        """На второй странице index выводится 4 поста"""
        response = self.guest_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_first_group_list_page_contains_10_posts(self):
        """На первой странице group list выводится 10 постов"""
        response = self.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_group_list_page_contains_4_posts(self):
        """На второй странице group list выводится 4 поста"""
        response = self.guest_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_first_profile_page_contains_10_posts(self):
        """На первой странице profile выводится 10 постов"""
        response = self.guest_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author}
            )
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_profile_page_contains_4_posts(self):
        """На второй странице profile выводится 4 поста"""
        response = self.guest_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 4)
