from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Group, Follow
from .forms import PostForm, CommentForm
from django.core.paginator import Paginator
from django.views.generic.base import TemplateView
from django.contrib.auth import get_user_model

User = get_user_model()


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'posts/index.html',
        {'page': page, }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)

    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)

    return render(request, 'group.html',
                  {'group': group, 'page': page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'posts/new_post.html', {'form': form})


class JustStaticPage(TemplateView):
    # В переменной template_name обязательно указывается имя шаблона,
    # на основе которого будет создана возвращаемая страница
    template_name = 'posts/just_page.html'


def profile(request, username):
    user = get_object_or_404(User, username=username)
    following = Follow.objects.filter(
        user__id=request.user.id, author=user).exists()
    posts = user.posts.all()
    posts_count = len(posts)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)

    return render(
        request, 'posts/profile.html',
        {'user_prof': user, 'page': page,
         'posts_count': posts_count, 'following': following}
    )


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    posts_count = Post.objects.filter(author=user).count()
    comment_form = CommentForm()
    comments = post.comment.all()
    return render(request, 'posts/post.html',
                  {'user_prof': user, 'post': post,
                   'posts_count': posts_count, 'form': comment_form,
                   'comments': comments}
                  )


@login_required
def post_edit(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)
    if request.user != profile:
        return redirect('post', username=username, post_id=post_id)
    # добавим в form свойство files
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(
                "post",
                username=request.user.username, post_id=post_id)

    return render(
        request, 'posts/new_post.html', {'form': form, 'post': post},
    )


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, pk=post_id)
        comment.save()
        return redirect('post',
                        username=request.user.username, post_id=post_id)
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    posts_count = Post.objects.filter(author=user).count()
    return render(request, 'posts/post.html',
                  {'user_prof': user, 'post': post,
                   'posts_count': posts_count, 'form': form, }
                  )


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def follow_index(request):
    user = request.user
    authors = Follow.objects.filter(user=user).values('author')
    posts = Post.objects.filter(author__in=authors).order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    follow = Follow()
    follow.user = request.user
    follow.author = User.objects.get(username=username)
    follow.save()

    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    user = get_object_or_404(User, username=username)
    follow = Follow.objects.get(user=request.user, author=user)
    follow.delete()
    return redirect('profile', username=username)
