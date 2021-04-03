from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'Заголовок',
        help_text='Дайте короткое название задаче',
        max_length=200
    )
    slug = models.SlugField(
        'Слаг',
        help_text='Укажите адрес для страницы задачи. Используйте '
                  'только латиницу, цифры, дефисы и знаки '
                  'подчёркивания', unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        'текст поста',
        help_text='Хелп текст - напигите здесь текст поста'
    )
    pub_date = models.DateTimeField('date published',
                                    auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts')
    group = models.ForeignKey(
        Group,
        models.SET_NULL, blank=True, null=True,
        related_name='posts',
        verbose_name='название группы',
        help_text='Хелп текст - Укажите название группы')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comment')
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comment')
    text = models.TextField(
        'текст комментария',
        help_text='Напиши комментарии'
    )
    created = models.DateTimeField('created',
                                   auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following')
