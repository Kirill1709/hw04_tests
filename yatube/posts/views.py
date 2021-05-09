from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post

COUNT_POSTS = 10
User = get_user_model()


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, COUNT_POSTS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, COUNT_POSTS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.save()
        return redirect("posts:index")
    return render(
        request, "posts/new_post.html",
        {"form": form, "is_new": True})


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    paginator = Paginator(user_profile.posts.all(), COUNT_POSTS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'posts/profile.html',
        {'page': page, 'user_profile': user_profile})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    user_profile = post.author
    return render(
        request, 'posts/post.html',
        {'post': post, 'user_profile': user_profile})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.user != post.author:
        return redirect('posts:post_view', username, post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_view', username, post_id)
    return render(
        request, 'posts/new_post.html',
        {"form": form, "post": post, "is_new": False})
