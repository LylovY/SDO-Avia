from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from tasks.forms import AnswerForm
from tasks.models import Task, TaskCase, UserTaskCaseRelation, UserTaskRelation
from users.models import User


class TaskCaseList(ListView):
    paginate_by = 5
    model = TaskCase
    template_name = 'tasks/index.html'
    context_object_name = 'task_case'


class TaskCaseListAdmin(ListView):
    paginate_by = 5
    model = TaskCase
    template_name = 'tasks/taskcase_list_admin.html'
    context_object_name = 'task_cases'


class CreateTaskCase(CreateView):
    model = TaskCase
    fields = ('title', 'description')
    template_name = 'tasks/create_taskcase.html'
    success_url = reverse_lazy('tasks:taskcase_list_admin')

    def form_valid(self, form):
        messages.success(self.request, "Группа вопросов создана")
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())


class UpdateTaskCase(UpdateView):
    model = TaskCase
    fields = ('title', 'description')
    template_name = 'tasks/create_taskcase.html'
    success_url = reverse_lazy('tasks:taskcase_list_admin')
    context_object_name = 'taskcase'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, "Группа вопросов изменена")
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())


class DeleteTaskCase(DeleteView):
    model = TaskCase
    success_url = reverse_lazy('tasks:task_list_admin')
    template_name = 'tasks/confirm_delete_taskcase.html'
    context_object_name = 'taskcase'


class TaskListUser(ListView):
    paginate_by = 10
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'task_list'

    def get_queryset(self):
        return Task.objects.filter(task_case=self.kwargs['pk'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taskcase'] = self.kwargs['pk']
        return context


class TaskListAdmin(ListView):
    paginate_by = 10
    model = Task
    template_name = 'tasks/task_list_admin.html'
    context_object_name = 'task_list'


class TaskDetail(DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'
    pk_url_kwarg = 'id'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AnswerForm
        context['taskcase'] = self.kwargs['pk']
        return context


class CreateTask(CreateView):
    model = Task
    fields = ('title', 'description', 'answer', 'task_case')
    template_name = 'tasks/create_task.html'
    success_url = reverse_lazy('tasks:task_list_admin')

    def form_valid(self, form):
        messages.success(self.request, "Вопрос добавлен")
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())


class UpdateTask(UpdateView):
    model = Task
    fields = ('title', 'description', 'answer', 'task_case')
    template_name = 'tasks/create_task.html'
    success_url = reverse_lazy('tasks:task_list_admin')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, "Вопрос изменен")
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())


class DeleteTask(DeleteView):
    model = Task
    success_url = reverse_lazy('tasks:task_list_admin')
    template_name = 'tasks/confirm_delete_task.html'
    context_object_name = 'task'



@login_required
def add_answer(request, pk, id):
    task = get_object_or_404(Task, id=id)
    form = AnswerForm(request.POST or None)
    user = request.user
    if form.is_valid():
        answer = form.save(commit=False)
        answer.author = user
        answer.task = task
        answer.save()
    relation, created = UserTaskRelation.objects.get_or_create(
        user=user,
        task=task,
    )
    relation.status = UserTaskRelation.ON_CHECK
    relation.save()
    return redirect('tasks:task_list', pk)


class UsersList(ListView):
    model = User
    template_name = 'tasks/users.html'
    context_object_name = 'users'

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # context['form'] = AnswerForm
    #     context['taskcases'] = TaskCase.objects.all()
    #     context['tasks'] = Task.objects.all()
    #     context['users'] = User.objects.all()
    #     return context


# @login_required
# def add_taskcase(request, pk):
#     user = get_object_or_404(User, id=pk)
#     form = TaskCaseForm(request.POST or None)
#     if form.is_valid():
#         test_case = form.save(commit=False)
#         test_case.owner = request.user
#         test_case.save()
#     return redirect('tracks:tracks')

# @login_required
# def add_task(request, pk):
#     taskcase = get_object_or_404(TaskCase, id=pk)
#     user = request.user
#     relation, created = UserTaskCaseRelation.objects.get_or_create(
#         user=user,
#         task_case=taskcase,
#     )
#     relation.save()
#     return redirect(request.META.get('HTTP_REFERER'))