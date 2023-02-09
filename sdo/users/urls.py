from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, reverse_lazy

app_name = 'users'
urlpatterns = [
    path('logout/',
         LogoutView.as_view(template_name='users/logged_out.html'),
         name='logout'
         ),
    path('login/',
         LoginView.as_view(template_name='users/login.html', success_url=reverse_lazy('tasks:taskcase_list')),
         name='login'
         ),
]
