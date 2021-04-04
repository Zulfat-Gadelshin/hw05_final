from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Group, Post
from django.urls import reverse

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            description='Тестовый текст',
            slug='test-slug'
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='AndreyG')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        # Не автор поста
        self.user1 = User.objects.create_user(username='User1')
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)

        self.post = Post.objects.create(
            text='Эта запись создана для проверки теста',
            author=self.user,
            group=PostURLTests.group)

    def test_home_url_exists_at_desired_location(self):
        response = self.guest_client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_post_added_url_exists_at_desired_location(self):
        response = self.guest_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 302)

    def test_new_post_url_redirect_anonymous_on_admin_login(self):
        response = self.guest_client.get(reverse('new_post'), follow=True)
        self.assertRedirects(response, reverse('login')+'?next=/new/')

    def test_post_added_url_exists_at_desired_location_authorized(self):
        response = self.authorized_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 200)

    def test_group_url_exists_at_desired_location(self):
        response = self.guest_client.get(
            reverse('group_detail', kwargs={'slug': 'test-slug'}))
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_redirect_anonymous(self):
        response = self.guest_client.get(
            reverse('post_edit',
                    kwargs={'username': self.user.username,
                            'post_id': self.post.id}), follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/AndreyG/1/edit/')

    def test_post_edit_url_redirect_non_author(self):
        response = self.authorized_client1.get(
            reverse('post_edit',
                    kwargs={'username': self.user.username,
                            'post_id': self.post.id}), follow=True)
        self.assertRedirects(
            response, ('/AndreyG/1/'))

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            reverse('index'): 'posts/index.html',
            reverse('new_post'): 'posts/new_post.html',
            reverse('group_detail',
                    kwargs={'slug': 'test-slug'}): 'group.html',
            reverse(
                'profile',
                kwargs={'username': 'AndreyG'}): 'posts/profile.html',
            reverse('post',
                    kwargs={'username': 'AndreyG',
                            'post_id': 1}): 'posts/post.html',
            reverse(
                'post_edit',
                kwargs={'username': 'AndreyG',
                        'post_id': 1}): 'posts/new_post.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_return_correct_code(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = [
            [200, reverse('profile',
                          kwargs={'username': 'AndreyG'}),
             self.authorized_client],
            [200, reverse(
                'post',
                kwargs={'username': 'AndreyG',
                        'post_id': 1}), self.authorized_client],
            [302, reverse(
                'post_edit',
                kwargs={'username': 'AndreyG', 'post_id': 1}),
             self.guest_client],
            [200, reverse(
                'post_edit',
                kwargs={'username': 'AndreyG', 'post_id': 1}),
             self.authorized_client],
            [302, reverse(
                'post_edit',
                kwargs={'username': 'AndreyG', 'post_id': 1}),
             self.authorized_client1],
        ]
        for subtest in templates_url_names:
            with self.subTest():
                response = subtest[2].get(subtest[1])
                self.assertEqual(response.status_code, subtest[0])

    def test_comment_added_url_not_available_for_guest(self):
        response = self.guest_client.get(
            reverse('add_comment',
                    kwargs={'username': 'AndreyG', 'post_id': 1}))
        self.assertEqual(response.status_code, 302)

    def test_new_comment_url_redirect_anonymous_on_admin_login(self):
        response = self.guest_client.get(
            reverse('add_comment',
                    kwargs={'username': 'AndreyG', 'post_id': 1}),
            follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/AndreyG/1/comment')
