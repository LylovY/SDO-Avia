from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView

from tasks.forms import AnswerForm
from tasks.models import Task, TaskCase, UserTaskRelation
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