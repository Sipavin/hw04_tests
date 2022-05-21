from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Group, Post
from posts.forms import PostForm

User = get_user_model()


class PostsPagesTests(TestCase):
    """ Тест страниц сайта."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовое название группы2',
            slug='test-slug2',
            description='Тестовое описание2',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.post.author.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        post = PostsPagesTests.post
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response.context.get('page_obj')[0], post)
        self.assertEqual(
            response.context.get('title'), ('Последние обновления на сайте'))

    def test_group_list_page_show_correct_context(self):
        """Шаблон group list сформирован с правильным контекстом."""
        post = PostsPagesTests.post
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': post.group.slug})
        )
        self.assertEqual(response.context.get('page_obj')[0], post)
        self.assertEqual(response.context.get('group'), post.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        post = PostsPagesTests.post
        response = self.guest_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': post.author.username}
            ),
        )
        self.assertEqual(response.context.get('page_obj')[0], post)
        self.assertEqual(response.context.get('author'), post.author)
        self.assertEqual(
            response.context.get('posts_count'),
            Post.objects.filter(author=post.author).count()
        )

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post detail сформирован с правильным контекстом."""
        post = PostsPagesTests.post
        response = self.guest_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post.id},
            )
        )
        self.assertEqual(response.context.get('post'), post)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertFalse(response.context.get('is_edit'))

    def test_edit_post_page_show_correct_context(self):
        """Шаблон edit post сформирован с правильным контекстом."""
        post = PostsPagesTests.post
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post.id})
        )
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertEqual(response.context.get('post'), post)
        self.assertTrue(response.context.get('is_edit'))

    def test_post_exists_in_index_group_profile(self):
        """Проверяем, что созданный пост появился на главной странице,
        странице группы и на странице постов автора."""
        post = PostsPagesTests.post
        reverses_filters_dict = {
            reverse('posts:index'): Post.objects.all(),
            reverse('posts:group_list', kwargs={'slug': post.group.slug}):
                Post.objects.filter(group=post.group),
            reverse(
                'posts:profile',
                kwargs={'username': post.author.username}
            ): Post.objects.filter(author=post.author),
        }
        for reverse_name, filters in reverses_filters_dict.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertTrue(filters.exists())

    def test_post_does_not_exist_in_another_group(self):
        """Проверяем, что созданный пост не появился в другой группе."""
        post = PostsPagesTests.post
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group2.slug})
        )
        self.assertNotIn(post, response.context.get('page_obj'))
