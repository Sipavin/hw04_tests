from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

FIRST_PAGE = 10
SECOND_PAGE = 5


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
        posts = [Post(
            author=cls.user, group=cls.group, text=str(i)) for i in range(15)]
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.guest_client = Client()

    def test_paginator(self):
        context = {
            reverse('posts:index'): FIRST_PAGE,
            reverse('posts:index') + '?page=2': SECOND_PAGE,
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ): FIRST_PAGE,
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ) + '?page=2': SECOND_PAGE,
            reverse(
                'posts:profile', kwargs={'username': 'test_user'}
            ): FIRST_PAGE,
            reverse(
                'posts:profile', kwargs={'username': 'test_user'}
            ) + '?page=2': SECOND_PAGE,
        }
        for reverse_page, len_posts in context.items():
            with self.subTest(reverse=reverse):
                self.assertEqual(len(self.client.get(
                    reverse_page).context.get('page_obj')), len_posts)
