from django.views.generic import ListView

from tasks.models import Task, TaskCase


class TaskCaseList(ListView):
    paginate_by = 5
    model = TaskCase
    template_name = 'tasks/index.html'
    context_object_name = 'task_case'


class TaskList(ListView):
    paginate_by = 10
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'task_list'

    def get_queryset(self):
        return Task.objects.filter(task_case=self.kwargs['pk'])