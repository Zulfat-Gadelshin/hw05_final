from .models import Post, Comment
from django.forms import ModelForm


class PostForm(ModelForm):
    class Meta:
        # укажем модель, с которой связана создаваемая форма
        model = Post
        # укажем, какие поля должны быть видны в форме и в каком порядке
        fields = ('group', 'text', 'image')


class CommentForm(ModelForm):
    class Meta:
        # укажем модель, с которой связана создаваемая форма
        model = Comment
        # укажем, какие поля должны быть видны в форме и в каком порядке
        fields = ('text',)

