from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView

from core.views import AdminRequiredMixin
from tasks.models import UserTaskRelation
from users.forms import CreationForm, TaskCaseForm, TaskFormUser
from users.models import User


class CreateUser(CreateView, SuccessMessageMixin, AdminRequiredMixin, ):
    """Создание юзера"""
    model = User
    form_class = CreationForm
    template_name = 'users/create_user.html'
    success_url = reverse_lazy('users:users_list')
    success_message = 'Аккаунт добавлен'
    extra_context = {'title': 'Создать аккаунт'}

    def form_valid(self, form):
        messages.success(self.request, "Пользователь создан")
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())


class UpdateUser(UpdateView, AdminRequiredMixin):
    """Изменение юзера"""
    model = User
    form_class = CreationForm
    template_name = 'users/create_user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    success_url = reverse_lazy('users:users_list')
    extra_context = {'title': 'Изменить аккаунт'}

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, "Аккаунт изменен")
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())


class DeleteUser(DeleteView, SuccessMessageMixin, AdminRequiredMixin):
    """Удаление юзера"""
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    success_url = reverse_lazy('users:users_list')
    template_name = 'users/confirm_delete_user.html'
    context_object_name = 'user'
    success_message = 'Аккаунт удален'
    extra_context = {'title': 'Удалить аккаунт'}

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteUser, self).delete(request, *args, **kwargs)


class TaskCaseUser(UpdateView, AdminRequiredMixin, ):
    """Назначение пользователю группы вопросов"""
    model = User
    form_class = TaskCaseForm
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'user'
    template_name = 'users/add_taskcase_user.html'
    success_url = reverse_lazy('users:users_list')
    extra_context = {'title': 'Добавить блок вопросов пользователю'}

    def form_valid(self, form):
        # self.object.tasks.clear()
        # self.object.task_relation.all().delete()
        # self.object.variants.clear()
        taskcases = [taskcase for taskcase in form.cleaned_data['task_case']]

        for taskcase in taskcases:
            for task in taskcase.tasks.all():
                # self.object.tasks.add(task)
                relation, create = UserTaskRelation.objects.get_or_create(
                    user=self.object,
                    task=task
                )
                if create:
                    relation.status = UserTaskRelation.NEW
                    relation.save()
        # taskcase.tasks.filter(task_relation__user=self.object).status = UserTaskRelation.NEW
        # self.object.tasks.set(taskcase.tasks.all())
        # for task in taskcase.tasks.all():
        #     self.object.tasks.set(taskcase.tasks.all())
        # self.object.tasks.add(form.cleaned_data['task_case'])
        return super(TaskCaseUser, self).form_valid(form)


class AddTaskUser(UpdateView, AdminRequiredMixin, ):
    """Назначение пользователю  вопросов"""
    model = User
    form_class = TaskFormUser
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'user'
    template_name = 'users/add_task_user.html'
    success_url = reverse_lazy('users:users_list')
    extra_context = {'title': 'Добавить вопросы пользователю'}
