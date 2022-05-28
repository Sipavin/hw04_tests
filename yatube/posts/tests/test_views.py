from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms
from django.core.cache import cache

from posts.models import Group, Post, Comment
from posts.forms import PostForm

User = get_user_model()


class PostsPagesTests(TestCase):
    """ Тест страниц сайта."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.upload = SimpleUploadedFile(name='small_image.gif',
                                        content=cls.small_image,
                                        content_type='image/gif')
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
            image=cls.upload,
        )

    def setUp(self):
        # self.user2 = User.objects.create_user(username='test_comment_user')
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
        Comment.objects.create(
            post=PostsPagesTests.post,
            author=self.user,
            text='Тестовый комент',
        )
        response = self.guest_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post.id},
            )
        )
        comment = response.context.get('comments')[0]
        self.assertIsInstance(comment, Comment)
        self.assertEqual(comment.post, PostsPagesTests.post)
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.text, 'Тестовый комент')
        self.assertEqual(response.context.get('post'), post)
        field = response.context['form'].fields['text']
        self.assertIsInstance(field, forms.fields.CharField)
        self.assertEqual(
            response.context.get('posts_count'),
            Post.objects.filter(author=post.author).count()
        )

    def test_create_post_page_show_correct_context(self):
        """Шаблон create post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context.get('form'), PostForm)

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
        group2 = response.context.get('group')
        self.assertEqual(group2, PostsPagesTests.group2)

    def test_index_cache(self):
        new_post = Post.objects.create(
            text='Тестовый текст2',
            author=PostsPagesTests.user,
            group=PostsPagesTests.group,
        )
        content1 = self.authorized_client.get(reverse('posts:index')).content
        new_post.delete()
        content2 = self.authorized_client.get(reverse('posts:index')).content
        self.assertEqual(content1, content2)
        cache.clear()
        content3 = self.authorized_client.get(reverse('posts:index')).content
        self.assertNotEqual(content1, content3)
