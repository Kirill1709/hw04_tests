from django.conf.urls import handler404, handler500
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("posts.urls", namespace='app_posts')),
    path("auth/", include("users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path('admin/', admin.site.urls),
    path('about/', include('about.urls', namespace='about')),
]
