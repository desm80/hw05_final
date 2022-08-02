from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Group, Post, User


def get_page_obj(request, *args):
    """Получение объекта page_obj для пагинатора"""
    paginator = Paginator(*args, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(20, key_prefix='index_page')
def index(request):
    """Стартовая страница проекта, выводятся все посты без фильтрации,
    посты представлены в краткой версии"""
    template = 'posts/index.html'
    page_obj = get_page_obj(request, Post.objects.all().select_related(
        'author', 'group'))
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context=context)


def group_posts(request, slug):
    """Вывод постов по группам, применена пагинация по 10"""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    page_obj = get_page_obj(request, group.posts.all().select_related('author')
                            )
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, template, context)


def profile(request, username):
    """Профайл автора со всеми его постами"""
    author = get_object_or_404(User, username=username)
    page_obj = get_page_obj(request, author.posts.all().select_related(
        'group'))
    if request.user.is_authenticated:
        return render(
            request, 'posts/profile.html',
            {'page_obj': page_obj,
             'author': author,
             'following': author.following.filter(user=request.user).exists(),
             }
        )
    else:
        return render(
            request, 'posts/profile.html', {'page_obj': page_obj,
                                            'author': author
                                            }
        )


@login_required
def post_create(request):
    """Функция обработки формы для создания нового поста"""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(f'/profile/{post.author.username}/')
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Функция обработки формы для редактирования поста автора"""
    post = get_object_or_404(Post, pk=post_id)
    if request.user.id == post.author.id:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            form.save()
            return redirect(f'/posts/{post_id}')
        return render(request, 'posts/create_post.html',
                      {'form': form,
                       'is_edit': True
                       })
    else:
        return redirect('posts:post_detail', post_id=post_id)


def post_detail(request, post_id):
    """Вывод полной версии поста"""
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all().select_related('author')
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def add_comment(request, post_id):
    """Функция комментирования постов авторов"""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts/add_comment.html', {'form': form})


@login_required
def follow_index(request):
    """Вывод постов авторов по подписке."""
    page_obj = get_page_obj(
        request, Post.objects.filter(
            author__following__user=request.user).select_related('group')
    )
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора."""
    author = get_object_or_404(User, username=username)
    if (request.user.username != username and author.following.filter(
            user=request.user).exists() is False):
        author.following.create(user=request.user)
        return redirect('posts:profile', username)
    else:
        return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    """Отписаться от автора."""
    author = get_object_or_404(User, username=username)
    follow = author.following.filter(user=request.user)
    follow.delete()
    return redirect('posts:profile', username)
