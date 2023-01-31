from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tasks.urls', namespace='tasks')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
]
