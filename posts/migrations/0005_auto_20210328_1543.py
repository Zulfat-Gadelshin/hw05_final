# Generated by Django 2.2.6 on 2021-03-28 12:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20210228_2143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(help_text='Укажите адрес для страницы задачи. Используйте только латиницу, цифры, дефисы и знаки подчёркивания', unique=True, verbose_name='Слаг'),
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(help_text='Дайте короткое название задаче', max_length=200, verbose_name='Заголовок'),
        ),
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Хелп текст - Укажите название группы', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='posts.Group', verbose_name='название группы'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='Хелп текст - напигите здесь текст поста', verbose_name='текст поста'),
        ),
    ]