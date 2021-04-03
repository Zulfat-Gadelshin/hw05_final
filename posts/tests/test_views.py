from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post, Follow
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil
import tempfile
from django.core.cache import cache


User = get_user_model()


class PaginatorViewsTest(TestCase):
    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        for index in range(13):
            Post.objects.create(
                text=f'Эта запись № {index} создана для проверки теста',
                author=self.user,
            )

    def test_first_page_containse_ten_records(self):
        response = self.client.get(reverse('index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД:
        # она понадобится для тестирования страницы deals:task_detail
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.group_2 = Group.objects.create(
            title='Тестовое название группы 2',
            description='Тестовый текст',
            slug='test-slug-2'
        )
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    @classmethod
    def tearDownClass(cls):
        # Модуль shutil - библиотека Python с прекрасными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок|файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # состоящей из двух пикселей: белого и чёрного
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        self.post = Post.objects.create(
            text='Эта запись создана для проверки теста',
            author=self.user,
            group=PostPagesTests.group,
            image=uploaded,
        )

    def test_image_on_index_page(self):
        """Проверка наличия картинки в посте"""
        response = self.authorized_client.get(reverse('index'))
        self.assertIsNotNone(response.context['page'][0].image)

    def test_index_page_cache(self):
        """Testing correct caching the index template"""
        response = self.authorized_client.get(reverse('index'))
        last_post = response.content
        post = Post.objects.create(
            text='Новый пост',
            author=self.user,
        )
        response = self.authorized_client.get(reverse('index'))
        current_post = response.content
        self.assertEqual(last_post, current_post, 'Caching is not working.')

        cache.delete('index_page')

        response = self.authorized_client.get(reverse('index'))
        current_post = response.content
        self.assertNotEqual(current_post, post, 'Caching is not working.')

    def test_added_page_uses_correct_template(self):
        response = self.authorized_client.get(reverse('index'))
        self.assertTemplateUsed(response, 'posts/index.html')

    def test_home_page_uses_correct_template(self):
        response = self.authorized_client.get(reverse('new_post'))
        self.assertTemplateUsed(response, 'posts/new_post.html')

    def test_task_detail_pages_authorized_use_correct_template(self):
        response = self.authorized_client.get(
            reverse('group_detail', kwargs={'slug': 'test-slug'})
        )
        self.assertTemplateUsed(response, 'group.html')

    # Проверяем, что словарь context страницы со списком задач
    # в первом элементе списка object_list содержит ожидаемые значения
    def test_posts_list_page_shows_correct_context(self):
        """Шаблон task_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page'][0]

        post_author_0 = first_object.author
        post_text_0 = first_object.text

        self.assertEqual(
            post_text_0, 'Эта запись создана для проверки теста')
        self.assertEqual(post_author_0, self.user)

    def test_posts_group_page_shows_correct_context(self):
        """Шаблон task_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'group_detail',
            kwargs={'slug': 'test-slug'})
        )
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page'][0]

        post_author_0 = first_object.author
        post_text_0 = first_object.text

        self.assertEqual(
            post_text_0, 'Эта запись создана для проверки теста')
        self.assertEqual(post_author_0, self.user)

    def test_new_post_page_shows_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'group': forms.fields.ChoiceField,
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'text': forms.fields.CharField, }

        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_post_in_correct_group(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'group_detail',
            kwargs={'slug': 'test-slug'}))
        objects = response.context['page']
        self.assertIn(self.post, objects)

    def test_post_in_correct_group_index(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        objects = response.context['page']
        self.assertIn(self.post, objects)

    def test_post_not_in_uncorrect_group(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'group_detail',
            kwargs={'slug': 'test-slug-2'}))
        objects = response.context['page']
        self.assertNotIn(self.post, objects)

    def test_post_edit_page_shows_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post_edit',
                    kwargs={'username': self.user.username,
                            'post_id': self.post.id}))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'group': forms.fields.ChoiceField,
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField, }

        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_user_page_shows_correct_context(self):
        """Шаблон task_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'profile',
            kwargs={'username': self.user.username}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        object2 = response.context['posts_count']
        self.assertEqual(post_text_0,
                         'Эта запись создана для проверки теста')
        self.assertEqual(post_author_0, self.user)

        self.assertEqual(object2, 1, 'Ошибка ')

    def test_post_page_shows_correct_context(self):
        """Шаблон task_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'post',
            kwargs={'username': self.user.username,
                    'post_id': 1}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['post']
        post_author_0 = first_object.author
        post_text_0 = first_object.text

        self.assertEqual(post_text_0,
                         'Эта запись создана для проверки теста')
        self.assertEqual(post_author_0, self.user)


class ErrorPageTest(TestCase):
    def SetUp(self):
        self.client = Client()

    def test_404error_code(self):
        response = self.client.get('sgWVGETN')
        self.assertEqual(response.status_code, 404)


class FollowTest(TestCase):
    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author = User.objects.create_user(username='Tolstoy')

    def test_follow(self):
        response = self.authorized_client.get(
            reverse('profile_follow',
                    kwargs={'username': self.author.username}))
        self.assertTrue(
            Follow.objects.get(user=self.user, author=self.author))

    def test_unfollow(self):
        response = self.authorized_client.get(
            reverse('profile_follow',
                    kwargs={'username': self.author.username})) # noqa
        response = self.authorized_client.get(
            reverse('profile_unfollow',
                    kwargs={'username': self.author.username})) # noqa
        self.assertFalse(Follow.objects.filter(
            user=self.user, author=self.author).exists())

    def test_post_in_follower(self):
        response = self.authorized_client.get(
            reverse('profile_follow',
                    kwargs={'username': self.author.username})) # noqa
        post = Post.objects.create(
            text='Тестовый пост',
            author=self.author
        )
        response = self.authorized_client.get(
            reverse('follow_index'))
        post1 = response.context['page'][0]
        self.assertEqual(post1, post)

    def test_post_not_in_follower(self):
        Post.objects.create(
            text='Тестовый пост',
            author=self.author
        )
        response = self.authorized_client.get(reverse('follow_index'))
        page = response.context['page']
        self.assertEqual(len(page), 0)
