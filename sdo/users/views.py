from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView

from users.forms import TaskCaseForm, TaskFormUser
from users.models import User


class CreateUser(CreateView, SuccessMessageMixin):
    model = User
    fields = ('username', 'first_name', 'password')
    template_name = 'users/create_user.html'
    success_url = reverse_lazy('tasks:users_list')
    success_message = 'Аккаунт добавлен'


class UpdateUser(UpdateView):
    model = User
    fields = ('username', 'first_name', 'password')
    template_name = 'users/create_user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    success_url = reverse_lazy('tasks:users_list')


    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, "Аккаунт изменен")
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())

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


class TaskCaseUser(UpdateView):
    model = User
    form_class = TaskCaseForm
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'user'
    template_name = 'users/add_taskcase_user.html'
    success_url = reverse_lazy('tasks:users_list')

    def form_valid(self, form):
        # self.object.groups.clear()
        taskcases = [taskcase for taskcase in form.cleaned_data['task_case']]
        for taskcase in taskcases:
            for task in taskcase.tasks.all():
                self.object.tasks.add(task)
        # self.object.tasks.add(form.cleaned_data['task_case'])
        return super(TaskCaseUser, self).form_valid(form)


class AddTaskUser(UpdateView):
    model = User
    form_class = TaskFormUser
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'user'
    template_name = 'users/add_task_user.html'
    success_url = reverse_lazy('tasks:users_list')