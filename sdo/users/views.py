from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView

from users.models import User


class CreateUser(CreateView, SuccessMessageMixin):
    model = User
    fields = ('username', 'first_name', 'password')
    template_name = 'users/create_user.html'
    success_url = reverse_lazy('tasks:users_list')
    success_message = 'Аккаунт добавлен'


class UpdateUser(UpdateView, SuccessMessageMixin):
    model = User
    fields = ('username', 'first_name', 'password')
    template_name = 'users/create_user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    success_url = reverse_lazy('tasks:users_list')
    success_message = 'Аккаунт изменен'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    # def get_object(self):
    #     return User.objects.get(username=self.kwargs.get("username"))


class DeleteUser(DeleteView, SuccessMessageMixin):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    success_url = reverse_lazy('tasks:users_list')
    template_name = 'users/confirm_delete_user.html'
    context_object_name = 'user'
    success_message = 'Аккаунт удален'