from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Func, OuterRef, Q, Subquery
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from core.views import AdminRequiredMixin, MyLoginRequiredMixin
from tasks.forms import AnswerForm, ReviewForm, TaskFormTaskcase, TaskFormTaskcaseUser
from tasks.models import Answer, Task, TaskCase, UserTaskRelation
from users.models import User


class TaskCaseList(MyLoginRequiredMixin, ListView):
    """GenericView листа группы вопросов от юзера"""
    paginate_by = 3
    model = TaskCase
    template_name = 'tasks/index.html'
    context_object_name = 'task_case'

    def get_queryset(self):
        task_count_new = Task.objects.filter(
            Q(task_relation__status=UserTaskRelation.NEW) | Q(task_relation__status=UserTaskRelation.FOR_REVISION),
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
        context['WAITING_ANSWER'] = user.tasks.filter(Q(task_relation__status=UserTaskRelation.NEW) | Q(
            task_relation__status=UserTaskRelation.FOR_REVISION)).count()
        context['ON_CHECK'] = user.tasks.filter(task_relation__status=UserTaskRelation.ON_CHECK).count()
        context['ACCEPT'] = user.tasks.filter(task_relation__status=UserTaskRelation.ACCEPT).count()
        return context


class TaskCaseListAdmin(AdminRequiredMixin, ListView):
    """GenericView листа группы вопросов от админа"""
    paginate_by = 5
    model = TaskCase
    template_name = 'tasks/taskcase_list_admin.html'
    context_object_name = 'task_cases'


class CreateTaskCase(AdminRequiredMixin, CreateView):
    """GenericView создания группы вопросов"""
    model = TaskCase
    fields = ('title', 'description')
    template_name = 'tasks/create_taskcase.html'
    success_url = reverse_lazy('tasks:taskcase_list_admin')

    def form_valid(self, form):
        messages.success(self.request, "Группа вопросов создана")
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())


class UpdateTaskCase(AdminRequiredMixin, UpdateView):
    """GenericView изменения  группы вопросов"""
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


class DeleteTaskCase(AdminRequiredMixin, DeleteView):
    """GenericView удаления группы вопросов"""
    model = TaskCase
    success_url = reverse_lazy('tasks:taskcase_list_admin')
    template_name = 'tasks/confirm_delete_taskcase.html'
    context_object_name = 'taskcase'
    success_message = "Группа вопросов удалена"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteTaskCase, self).delete(request, *args, **kwargs)


class TaskListUser(MyLoginRequiredMixin, ListView):
    """GenericView листа вопросов, назначенных юзеру"""
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


class TaskListAdmin(AdminRequiredMixin, ListView):
    """GenericView листа вопросов от админа"""
    paginate_by = 10
    model = Task
    template_name = 'tasks/task_list_admin.html'
    context_object_name = 'task_list'


class TaskDetailAdmin(AdminRequiredMixin, DetailView):
    """GenericView одного  вопроса от админа"""
    model = Task
    template_name = 'tasks/task_detail_admin.html'
    context_object_name = 'task'
    pk_url_kwarg = 'pk'


class TaskListAdminCheck(AdminRequiredMixin, ListView):
    """Проверка ответов со статусом ON_CHECK"""
    paginate_by = 10
    model = Task
    template_name = 'tasks/task_list_check.html'
    context_object_name = 'task_list'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.kwargs['username']
        return context

    def get_queryset(self):
        return Task.objects.filter(users__username=self.kwargs.get('username'),
                                   task_relation__status=UserTaskRelation.ON_CHECK)


class TaskDetail(MyLoginRequiredMixin, DetailView):
    """GenericView одного вопроса от пользователя"""
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'
    pk_url_kwarg = 'id'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        taskcase = self.kwargs['pk']
        task = self.kwargs['id']
        user = self.request.user
        relation = UserTaskRelation.objects.get(
            user=user,
            task=task,
        )
        context['form'] = AnswerForm
        context['taskcase'] = taskcase
        context['relation'] = relation
        return context


class CreateTask(AdminRequiredMixin, CreateView):
    """GenericView создания вопроса"""
    model = Task
    fields = ('title', 'description', 'answer', 'task_case')
    template_name = 'tasks/create_task.html'
    success_url = reverse_lazy('tasks:task_list_admin')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Вопрос добавлен")
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())


class UpdateTask(AdminRequiredMixin, UpdateView):
    """GenericView изменения вопроса"""
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
        form.save()
        # super().form_valid(form)
        return HttpResponse('<script>history.go(-2)</script>')
        # return super().form_valid(form)
    # window.location.reload(history.back())
    # window.history.go(-2);
    # def get_success_url(self):
    #     # res = self.request.META.get('HTTP_REFERER')
    #     res = self.request.build_absolute_uri()
    #     print(res)
    #     # res1 = HttpResponse('<script>history.go(-2);</script>')
    #     # print(res1)
    #     # res = reverse('tasks:task_list_admin')
    #     # print(self.request.GET)
    #     # if 'page' in self.request.GET:
    #     #     res += f"?page={self.request.GET['page']}"
    #     #     # print(res)
    #     return res

    # def get_success_url(self):
    #     return self.request.path


class DeleteTask(AdminRequiredMixin, DeleteView):
    """GenericView удаления вопроса"""
    model = Task
    success_url = reverse_lazy('tasks:task_list_admin')
    template_name = 'tasks/confirm_delete_task.html'
    context_object_name = 'task'
    success_message = "Вопрос удален"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteTask, self).delete(request, *args, **kwargs)


@login_required
def add_answer(request, pk, id):
    """Юзер добавляет ответ на вопрос"""
    task = get_object_or_404(Task, id=id)
    form = AnswerForm(request.POST or None)
    user = request.user
    if form.is_valid():
        answer = form.save(commit=False)
        relation = UserTaskRelation.objects.get(
            user=user,
            task=task,
        )
        relation.status = UserTaskRelation.ON_CHECK
        relation.save()
        answer.relation = relation
        answer.author = request.user
        answer.save()
    return redirect('tasks:task_list', pk)


@login_required
def accept_answer(request, username, pk):
    """Принять ответ юзера со стороны админа"""
    relation = get_object_or_404(UserTaskRelation, id=pk)
    relation.status = UserTaskRelation.ACCEPT
    relation.save()
    user = get_object_or_404(User, username=username)
    if user.tasks.filter(task_relation__status=UserTaskRelation.ON_CHECK).count() > 0:
        return redirect('tasks:check_task', username)
    return redirect('tasks:users_list')


class AnswerDetail(MyLoginRequiredMixin, DetailView):
    """GenericView одного ответа"""
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
    """Добавление ревью админом на ответ юзера"""
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


class UsersList(AdminRequiredMixin, ListView):
    """GenericView листа юзеров"""
    model = User
    template_name = 'tasks/users.html'
    context_object_name = 'users'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        note_count = User.objects.annotate(count=Count('notes')).values('count').order_by('-date_joined').filter(
            pk=OuterRef('pk'))
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


class AddTaskTaskCase(MyLoginRequiredMixin, UpdateView):
    """Добавление вопросов в группу вопросов"""
    model = TaskCase
    form_class = TaskFormTaskcase
    context_object_name = 'taskcase'
    template_name = 'tasks/add_task_taskcase.html'
    success_url = reverse_lazy('tasks:taskcase_list_admin')


class AddTaskCaseUsers(MyLoginRequiredMixin, UpdateView):
    """Добавление юзеров в группу вопросов"""
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


@login_required()
def complete_taskcase(request, pk):
    """Завершить выполнение группы вопросов пользователем"""
    taskcase = get_object_or_404(TaskCase, id=pk)
    user = request.user
    for task in taskcase.tasks.all():
        user.tasks.remove(task)
    user.task_case.remove(taskcase)
    return redirect('tasks:taskcase_list')

