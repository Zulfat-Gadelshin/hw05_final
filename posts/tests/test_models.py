from django.test import TestCase
from ..models import Post, Group
from django.contrib.auth import get_user_model


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.user = User.objects.create_user(username='john',
                                            email='jlennon@beatles.com',
                                            password='glass onion')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Эта запись создана для проверки теста'
        )

    def test_verbose_name(self):

        task = PostModelTest.post
        field_verboses = {
            'text': 'текст поста',
            'group': 'название группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    task._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        task = PostModelTest.post
        field_help_texts = {
            'text': 'Хелп текст - напигите здесь текст поста',
            'group': 'Хелп текст - Укажите название группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    task._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_field_Post(self):
        """__str__  task - это строчка с содержимым task.title."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEquals(expected_object_name, str(post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём тестовую запись в БД
        # и сохраняем ее в качестве переменной класса
        cls.group = Group.objects.create(
            title='Заголовок тестовой задачи',
            slug='test-task'
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        task = GroupModelTest.group
        field_verboses = {
            'title': 'Заголовок',
            'slug': 'Слаг',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    task._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        task = GroupModelTest.group
        field_help_texts = {
            'title': 'Дайте короткое название задаче',
            'slug': ('Укажите адрес для страницы задачи. Используйте '
                     'только латиницу, цифры, дефисы и знаки '
                     'подчёркивания'),
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    task._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_field_Group(self):
        """__str__  task - это строчка с содержимым task.title."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))
