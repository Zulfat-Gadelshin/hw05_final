from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..forms import PostForm
from ..models import Post
import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем временную папку для медиа-файлов;
        # на момент теста медиа папка будет перопределена
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        # Модуль shutil - библиотека Python с прекрасными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок|файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        # Создаем неавторизованный клиент
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        # Создаем запись в базе данных для проверки сушествующего slug
        Post.objects.create(
            text='Тестовый текст',
            author=self.user
        )

    def test_only_img_in_image_field(self):
        # Для тестирования загрузки изображений
        # берём байт-последовательность картинки,
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
            name='small.txt',
            content=small_gif,
            content_type='text/plain'
        )
        form_data = {
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        error_text = "Формат файлов 'txt' не поддерживается." \
                     " Поддерживаемые форматы файлов: 'bmp, dib," \
                     " gif, tif, tiff, jfif, jpe, jpg, jpeg, pbm," \
                     " pgm, ppm, pnm, png, apng, blp, bufr, cur, pcx," \
                     " dcx, dds, ps, eps, fit, fits, fli, flc, ftc," \
                     " ftu, gbr, grib, h5, hdf, jp2, j2k, jpc, jpf," \
                     " jpx, j2c, icns, ico, im, iim, mpg, mpeg, mpo," \
                     " msp, palm, pcd, pdf, pxr, psd, bw, rgb, rgba," \
                     " sgi, ras, tga, icb, vda, vst," \
                     " webp, wmf, emf, xbm, xpm'."
        self.assertFormError(response, 'form', 'image', error_text)
        self.assertFalse(PostForm(response.get('form')).is_valid())

    def test_create_post_with_img(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        tasks_count = Post.objects.count()
        # Для тестирования загрузки изображений
        # берём байт-последовательность картинки,
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
        form_data = {
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('index'))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        # Проверяем, что создалась запись с нашим слагом
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Тестовый текст',
                image='posts/small.gif').exists()
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(Post.objects.first().image)


class PostEditFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()

    def setUp(self):
        # Создаем неавторизованный клиент
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        Post.objects.create(
            text='Тестовый текст',
            author=self.user, )

    def test_create_post(self):
        """Валидная форма создает запись в Task."""
        tasks_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый измененный текст', }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse(
                'post_edit',
                kwargs={'username': 'StasBasov',
                        'post_id': 1}),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'post', kwargs={'username': 'StasBasov', 'post_id': 1}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), tasks_count)
        # Проверяем, что создалась запись с нашим слагом
        self.assertTrue(Post.objects.filter(
            author=self.user,
            text='Тестовый измененный текст').exists()
        )
