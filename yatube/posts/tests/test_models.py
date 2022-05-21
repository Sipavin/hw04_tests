from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый_текст_для_поста',
            author=cls.user,
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        field_object_names = {
            group.title: 'Тестовая группа',
            post.text[:15]: 'Тестовый_текст_'
        }
        for field, expected_value in field_object_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    str(field),
                    expected_value
                )
