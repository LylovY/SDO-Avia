from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Case, Count, Exists, F, Func, IntegerField, OuterRef, Q, Subquery, When
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from tasks.forms import AnswerForm, ReviewForm, TaskFormTaskcase, TaskFormTaskcaseUser
from tasks.models import Answer, Review, Task, TaskCase, UserTaskCaseRelation, UserTaskRelation
from tasks.utils import SubqueryCount
from users.models import User


class TaskCaseList(ListView):
    paginate_by = 3
    model = TaskCase
    template_name = 'tasks/index.html'
    context_object_name = 'task_case'

    def get_queryset(self):
        task_count_new = Task.objects.filter(Q(task_relation__status=UserTaskRelation.NEW) | Q(task_relation__status=UserTaskRelation.FOR_REVISION),
                                         task_case=OuterRef('id'),
                                         task_relation__user=self.request.user).annotate(
            count=Func(F('id'), function='Count')
        ).values('count')
        task_count_oncheck = Task.objects.filter(task_case=OuterRef('id'),
                                             task_relation__user=self.request.user,
                                             task_relation__status=UserTaskRelation.ON_CHECK).annotate(
            count=Func(F('id'), function='Count')
        ).values('count')
        task_count_accept = Task.objects.filter(task_case=OuterRef('id'),
                                             task_relation__user=self.request.user,
                                             task_relation__status=UserTaskRelation.ACCEPT).annotate(
            count=Func(F('id'), function='Count')
        ).values('count')
        return TaskCase.objects.filter(task_case_relation__user=self.request.user).annotate(
            WAITING_ANSWER=Subquery(task_count_new),
            ON_CHECK=Subquery(task_count_oncheck),
            ACCEPT=Subquery(task_count_accept),
    )


    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['WAITING_ANSWER'] = user.tasks.filter(Q(task_relation__status=UserTaskRelation.NEW) | Q(task_relation__status=UserTaskRelation.FOR_REVISION)).count()
        context['ON_CHECK'] = user.tasks.filter(task_relation__status=UserTaskRelation.ON_CHECK).count()
        context['ACCEPT'] = user.tasks.filter(task_relation__status=UserTaskRelation.ACCEPT).count()
        return context


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
    success_url = reverse_lazy('tasks:taskcase_list_admin')
    template_name = 'tasks/confirm_delete_taskcase.html'
    context_object_name = 'taskcase'


class TaskListUser(ListView):
    paginate_by = 10
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'task_list'

    def get_queryset(self):
        return Task.objects.filter(task_case=self.kwargs['pk']).annotate(
            status=Subquery(UserTaskRelation.objects.filter(
                user=self.request.user,
                task=OuterRef('pk'),
            ).order_by('-created').values('status')[:1]),
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taskcase'] = self.kwargs['pk']
        return context


class TaskListAdmin(ListView):
    paginate_by = 10
    model = Task
    template_name = 'tasks/task_list_admin.html'
    context_object_name = 'task_list'


class TaskDetailAdmin(DetailView):
    model = Task
    template_name = 'tasks/task_detail_admin.html'
    context_object_name = 'task'
    pk_url_kwarg = 'pk'


class TaskListAdminCheck(ListView):
    paginate_by = 10
    model = Task
    template_name = 'tasks/task_list_check.html'
    context_object_name = 'task_list'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.kwargs['username']
        return context

    def get_queryset(self):
        return Task.objects.filter(users__username=self.kwargs.get('username'),
                                   task_relation__status=UserTaskRelation.ON_CHECK)



class TaskDetail(DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'
    pk_url_kwarg = 'id'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        taskcase = self.kwargs['pk']
        task = self.kwargs['id']
        user = self.request.user
        relation, _ = UserTaskRelation.objects.get_or_create(
            user=user,
            task_id=task,
        )
        context['form'] = AnswerForm
        context['taskcase'] = taskcase
        context['relation'] = relation
        return context


class CreateTask(CreateView):
    model = Task
    fields = ('title', 'description', 'answer', 'task_case')
    template_name = 'tasks/create_task.html'
    success_url = reverse_lazy('tasks:task_list_admin')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Вопрос добавлен")
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())


class UpdateTask(UpdateView):
    model = Task
    fields = ('title', 'description', 'answer', 'task_case')
    template_name = 'tasks/create_task.html'
    # success_url = HttpResponseRedirect(self.request.path_info)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = self.request.GET.get('page', 1)
        context['is_edit'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, "Вопрос изменен")
        # super().form_valid(form)
        # return HttpResponseRedirect(self.get_success_url())
        return super().form_valid(form)

    def get_success_url(self):
        res = self.request.META.get('HTTP_REFERER')
        # res = reverse('tasks:task_list_admin')
        # print(self.request.GET)
        # if 'page' in self.request.GET:
        #     res += f"?page={self.request.GET['page']}"
        #     # print(res)
        return res

    # def get_success_url(self):
    #     return self.request.path




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
        relation, created = UserTaskRelation.objects.get_or_create(
            user=user,
            task=task,
        )
        relation.status = UserTaskRelation.ON_CHECK
        relation.save()
        answer.relation = relation
        answer.save()
    return redirect('tasks:task_list', pk)


@login_required
def accept_answer(request, username, pk):
    relation = get_object_or_404(UserTaskRelation, id=pk)
    relation.status = UserTaskRelation.ACCEPT
    relation.save()
    user = get_object_or_404(User, username=username)
    if user.tasks.filter(task_relation__status=UserTaskRelation.ON_CHECK).count() > 0:
        return redirect('tasks:check_task', username)
    return redirect('tasks:users_list')


class AnswerDetail(DetailView):
    model = Answer
    template_name = 'tasks/answer_detail.html'
    context_object_name = 'answer'
    pk_url_kwarg = 'id'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ReviewForm
        context['relation'] = self.kwargs['pk']
        context['username'] = self.kwargs['username']
        return context


@login_required
def add_review(request, username, pk, id):
    answer = get_object_or_404(Answer, id=id)
    form = ReviewForm(request.POST or None)
    if form.is_valid():
        review = form.save(commit=False)
        review.answer = answer
        review.save()

        relation = get_object_or_404(UserTaskRelation, id=pk)
        relation.status = UserTaskRelation.FOR_REVISION
        relation.save()
    user = get_object_or_404(User, username=username)
    if user.tasks.filter(task_relation__status=UserTaskRelation.ON_CHECK).count() > 0:
        return redirect('tasks:check_task', username)
    return redirect('tasks:users_list')


class UsersList(ListView):
    model = User
    template_name = 'tasks/users.html'
    context_object_name = 'users'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['NEW'] = 'NEW'
        # context['users'] = User.objects.annotate(
        #     NEW=Count('tasks'),
        #     new2=Count('task_case')
        # )
        # context['NEW'] = User.objects.filter(task_relation__status=UserTaskRelation.NEW, username=OuterRef('username')).count()
        # context['ON_CHECK'] = UserTaskRelation.objects.filter(status=UserTaskRelation.ON_CHECK).count()
        # context['ACCEPT'] = UserTaskRelation.objects.filter(status=UserTaskRelation.ACCEPT).count()
        return context

    def get_queryset(self):
        note_count = User.objects.annotate(count=Count('notes')).values('count').order_by('-date_joined').filter(pk=OuterRef('pk'))
        NEW = Count('tasks', filter=Q(task_relation__status=UserTaskRelation.NEW))
        ON_CHECK = Count('tasks', filter=Q(task_relation__status=UserTaskRelation.ON_CHECK))
        ACCEPT = Count('tasks', filter=Q(task_relation__status=UserTaskRelation.ACCEPT))
        return User.objects.annotate(
            note_count=Subquery(note_count),
            NEW=NEW,
            ON_CHECK=ON_CHECK,
            ACCEPT=ACCEPT
        ).order_by('-ON_CHECK')
        # ).annonate(
        #     # NEW=Count('tasks', filter=Q(task_relation__status=UserTaskRelation.NEW)),
        #     ON_CHECK=Count('tasks', filter=Q(task_relation__status=UserTaskRelation.ON_CHECK)),
        #     # ACCEPT=Count('tasks', filter=Q(task_relation__status=UserTaskRelation.ACCEPT)),
        # ).prefetch_related('tasks')


class AddTaskTaskCase(UpdateView):
    model = TaskCase
    form_class = TaskFormTaskcase
    context_object_name = 'taskcase'
    template_name = 'tasks/add_task_taskcase.html'
    success_url = reverse_lazy('tasks:taskcase_list_admin')


class AddTaskCaseUsers(UpdateView):
    model = TaskCase
    form_class = TaskFormTaskcaseUser
    context_object_name = 'taskcase'
    template_name = 'tasks/add_user_taskcase.html'
    success_url = reverse_lazy('tasks:taskcase_list_admin')

    def form_valid(self, form):
        # self.object.tasks.clear()
        users = [user for user in form.cleaned_data['users']]
        for user in users:
            for task in self.object.tasks.all():
                relation = UserTaskRelation.objects.create(
                    user=user,
                    task=task
                )
                relation.status = UserTaskRelation.NEW
                relation.save()
            # taskcase.tasks.filter(task_relation__user=self.object).status = UserTaskRelation.NEW
            # self.object.tasks.set(taskcase.tasks.all())
            # for task in taskcase.tasks.all():
            #     self.object.tasks.set(taskcase.tasks.all())
        # self.object.tasks.add(form.cleaned_data['task_case'])
        return super(AddTaskCaseUsers, self).form_valid(form)


def complete_taskcase(request, pk):
    taskcase = get_object_or_404(TaskCase, id=pk)
    user = request.user
    for task in taskcase.tasks.all():
        user.tasks.remove(task)
    user.task_case.remove(taskcase)
    return redirect('tasks:taskcase_list')

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
