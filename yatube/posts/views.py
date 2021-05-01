from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post

User = get_user_model()


def index(request):
    latest = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(latest, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
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
    return render(request, "new_post.html", {"form": form})


def profile(request, username):
    post = get_object_or_404(User, username=username)
    user_posts = post.posts.all()
    user_posts_count = post.posts.all().count()
    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {'page': page,
                  'user_posts_count': user_posts_count, 'post': post})


def post_view(request, username, post_id):
    user = User.objects.get(username=username)
    post = Post.objects.get(id=post_id)
    posts_count = user.posts.all().count()
    author = post.author
    return render(request, 'post.html', {'post': post, 'author': author,
                  'posts_count': posts_count})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = PostForm(request.POST or None, instance=post)
    if request.user != post.author:
        return redirect('posts:post', username, post_id)
    if form.is_valid():
        form.save()
        return redirect('posts:post', username, post_id)
    return render(request, 'new_post.html', {"form": form, "post": post})
