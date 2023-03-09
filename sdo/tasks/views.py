from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Exists, F, Func, OuterRef, Q, Subquery
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from core.views import AdminRequiredMixin, MyLoginRequiredMixin
from tasks.forms import AnswerForm, CreateTaskForm, CreateTaskTestForm, ReviewForm, TaskFormTaskcase, \
    TaskFormTaskcaseUser, TestForm, \
    VariantForm
from tasks.models import Answer, Task, TaskCase, UserTaskRelation, Variant
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
        task_count_wrong = Task.objects.filter(task_case=OuterRef('id'),
                                                task_relation__user=self.request.user,
                                                task_relation__status=UserTaskRelation.WRONG).annotate(
            count=Func(F('id'), function='Count')
        ).values('count')
        return TaskCase.objects.filter(task_case_relation__user=self.request.user).annotate(
            WAITING_ANSWER=Subquery(task_count_new),
            ON_CHECK=Subquery(task_count_oncheck),
            ACCEPT=Subquery(task_count_accept),
            WRONG=Subquery(task_count_wrong),
        ).prefetch_related('tasks', 'users')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['WAITING_ANSWER'] = user.tasks.filter(Q(task_relation__status=UserTaskRelation.NEW) | Q(
            task_relation__status=UserTaskRelation.FOR_REVISION)).count()
        context['ON_CHECK'] = user.tasks.filter(task_relation__status=UserTaskRelation.ON_CHECK).prefetch_related(
            'tasks', 'task_case').count()
        context['ACCEPT'] = user.tasks.filter(task_relation__status=UserTaskRelation.ACCEPT).prefetch_related('tasks',
                                                                                                              'task_case').count()
        context['title'] = 'СДО авиа'
        return context


class TaskCaseListAdmin(AdminRequiredMixin, ListView):
    """GenericView листа группы вопросов от админа"""
    paginate_by = 5
    model = TaskCase
    template_name = 'tasks/taskcase_list_admin.html'
    context_object_name = 'task_cases'
    extra_context = {'title': 'Блоки вопросов'}

    def get_queryset(self):
        return TaskCase.objects.prefetch_related('tasks', 'users')


class CreateTaskCase(AdminRequiredMixin, CreateView):
    """GenericView создания группы вопросов"""
    model = TaskCase
    fields = ('title', 'description', 'is_test')
    template_name = 'tasks/create_taskcase.html'
    success_url = reverse_lazy('tasks:taskcase_list_admin')
    extra_context = {'title': 'Создать блок вопросов'}

    def form_valid(self, form):
        messages.success(self.request, "Группа вопросов создана")
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())


class UpdateTaskCase(AdminRequiredMixin, UpdateView):
    """GenericView изменения  группы вопросов"""
    model = TaskCase
    fields = ('title', 'description', 'is_test')
    template_name = 'tasks/create_taskcase.html'
    success_url = reverse_lazy('tasks:taskcase_list_admin')
    context_object_name = 'taskcase'
    extra_context = {'title': 'Изменить блок вопросов'}

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
    extra_context = {'title': 'Удаление блока вопросов'}

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteTaskCase, self).delete(request, *args, **kwargs)


class TaskListUser(MyLoginRequiredMixin, ListView):
    """GenericView листа вопросов, назначенных юзеру"""
    paginate_by = 10
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'task_list'
    extra_context = {'title': 'Список вопросов'}

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
    extra_context = {'title': 'Список вопросов'}

    def get_queryset(self):
        search_term = self.request.GET.get('q')
        if search_term:
            return Task.objects.prefetch_related('task_case', 'users').filter(is_test=False,
                                                                              title__icontains=search_term)
        return Task.objects.prefetch_related('task_case', 'users').filter(is_test=False)


class TaskListTestAdmin(AdminRequiredMixin, ListView):
    """GenericView листа вопросов от админа"""
    paginate_by = 10
    model = Task
    template_name = 'tasks/tests/task_list_admin_test.html'
    context_object_name = 'task_list'
    extra_context = {'title': 'Список тестов'}

    def get_queryset(self):
        search_term = self.request.GET.get('q')
        if search_term:
            return Task.objects.prefetch_related('task_case', 'users').filter(is_test=True,
                                                                              title__icontains=search_term)
        return Task.objects.prefetch_related('task_case', 'users').filter(is_test=True)


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
    extra_context = {'title': 'Проверка'}

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.kwargs['username']
        return context

    def get_queryset(self):
        return Task.objects.filter(
            Q(task_relation__status=UserTaskRelation.ON_CHECK) | Q(task_relation__status=UserTaskRelation.FOR_REVISION),
            users__username=self.kwargs.get('username'),
        )


class TaskListAdminCheckTest(AdminRequiredMixin, ListView):
    paginate_by = 10
    model = Task
    template_name = 'tasks/tests/task_list_check_test.html'
    context_object_name = 'task_list'
    extra_context = {'title': 'Проверка теста'}

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.kwargs['username']
        return context

    def get_queryset(self):
        # user_variants = Subquery(Variant.objects.filter(task=OuterRef('pk'), users__username=self.kwargs.get('username')).values('text')[:1])
        return Task.objects.filter(users__username=self.kwargs.get('username'), is_test=True, task_case=self.kwargs.get('pk')).annotate(
            status=Subquery(UserTaskRelation.objects.filter(
                user__username=self.kwargs.get('username'),
                task=OuterRef('pk'),
            ).order_by('-created').values('status')[:1]),
        )


class TaskDetail(MyLoginRequiredMixin, DetailView, UpdateView):
    """GenericView одного вопроса от пользователя"""
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'
    pk_url_kwarg = 'id'
    extra_context = {'title': 'Вопросы'}
    form_class = TestForm
    # form_class = AnswerForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        taskcase = self.kwargs['pk']
        task = self.kwargs['id']
        user = self.request.user
        relation = UserTaskRelation.objects.get(
            user=user,
            task=task,
        )
        context['answerform'] = AnswerForm
        # context['testform'] = TestForm
        context['taskcase'] = taskcase
        context['relation'] = relation
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['task'] = self.object.id
        # kwargs['user'] = self.request.user.id
        return kwargs


class CreateTask(AdminRequiredMixin, CreateView):
    """GenericView создания вопроса"""
    model = Task
    # fields = ('title', 'description', 'answer', 'task_case')
    template_name = 'tasks/create_task.html'
    success_url = reverse_lazy('tasks:task_list_admin')
    extra_context = {'title': 'Создать вопрос'}
    form_class = CreateTaskForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Вопрос добавлен")
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())


class UpdateTask(AdminRequiredMixin, UpdateView):
    """GenericView изменения вопроса"""
    model = Task
    fields = ('title', 'description', 'answer', 'task_case', 'is_test')
    template_name = 'tasks/create_task.html'
    extra_context = {'title': 'Изменить вопрос'}
    success_url = reverse_lazy('tasks:task_list_admin')

    # success_url = HttpResponseRedirect(self.request.path_info)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = self.request.GET.get('page') or 1
        context['is_edit'] = True
        return context

    # def form_valid(self, form):
    #     messages.success(self.request, "Вопрос изменен")
    #     form.save()
    # # #     # super().form_valid(form)
    #     return HttpResponse('<script>history.go(-2)</script>')
        # return super().form_valid(form)
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
    def get_success_url(self):
        # get the current page from the query parameters
        # current_page = self.request.GET.get('page')
        current_page = self.request.POST.get('page') or self.kwargs.get('page')
        if current_page:
            # redirect to the current page in pagination
            return f"{reverse_lazy('tasks:task_list_admin')}?page={current_page}"
        else:
            # redirect to the default success URL
            return super().get_success_url()


class DeleteTask(AdminRequiredMixin, DeleteView):
    """GenericView удаления вопроса"""
    model = Task
    success_url = reverse_lazy('tasks:task_list_admin')
    template_name = 'tasks/confirm_delete_task.html'
    context_object_name = 'task'
    success_message = "Вопрос удален"
    extra_context = {'title': 'Удалить вопрос'}

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
    extra_context = {'title': 'Сотрудники'}

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        note_count = User.objects.annotate(count=Count('notes')).values('count').order_by('-date_joined').filter(
            pk=OuterRef('pk'))
        NEW = Count('tasks', filter=Q(task_relation__status=UserTaskRelation.NEW))
        FOR_REVISION = Count('tasks', filter=Q(task_relation__status=UserTaskRelation.FOR_REVISION))
        ON_CHECK = Count('tasks', filter=Q(task_relation__status=UserTaskRelation.ON_CHECK))
        ACCEPT = Count('tasks', filter=Q(task_relation__status=UserTaskRelation.ACCEPT))
        return User.objects.annotate(
            note_count=Subquery(note_count),
            NEW=NEW,
            FOR_REVISION=FOR_REVISION,
            ON_CHECK=ON_CHECK,
            ACCEPT=ACCEPT,
            tests=Exists(Task.objects.filter(users=OuterRef('pk'), is_test=True))
        ).order_by('-ON_CHECK', '-NEW').prefetch_related('tasks', 'task_case')
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
    extra_context = {'title': 'Добавить вопросы в блок '}


class AddTaskCaseUsers(MyLoginRequiredMixin, UpdateView):
    """Добавление юзеров в группу вопросов"""
    model = TaskCase
    form_class = TaskFormTaskcaseUser
    context_object_name = 'taskcase'
    template_name = 'tasks/add_user_taskcase.html'
    success_url = reverse_lazy('tasks:taskcase_list_admin')
    extra_context = {'title': 'Добавить сотрудников в блок '}

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


class CreateTest(AdminRequiredMixin, CreateView):
    """GenericView создания теста"""
    model = Task
    # fields = ('title', 'description', 'task_case')
    form_class = CreateTaskTestForm
    template_name = 'tasks/tests/create_test.html'
    # success_url = reverse_lazy('tasks:test_detail_admin')
    extra_context = {'title': 'Создать вопрос'}

    def form_valid(self, form):
        # form.instance.author = self.request.user
        messages.success(self.request, "Тест создан")
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self, **kwargs):
        # if kwargs != None:
        return reverse('tasks:test_detail_admin', kwargs={'pk': self.object.id})
        # else:
        #     return reverse_lazy('detail', args=(self.object.id,))

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(CreateTest, self).get_form_kwargs(
            *args, **kwargs)
        return kwargs


class TestDetailAdmin(AdminRequiredMixin, DetailView):
    """GenericView одного вопроса от пользователя"""
    model = Task
    template_name = 'tasks/tests/test_detail_admin.html'
    context_object_name = 'test'
    pk_url_kwarg = 'pk'
    extra_context = {'title': 'Тесты'}

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = VariantForm
        return context


@login_required
def add_variant(request, pk):
    """Юзер добавляет ответ на вопрос"""
    task = get_object_or_404(Task, id=pk)
    form = VariantForm(request.POST or None)
    # user = request.user
    if form.is_valid():
        variant = form.save(commit=False)
        variant.task = task
        # answer.author = request.user
        variant.save()
    return redirect('tasks:test_detail_admin', pk)

@login_required
def update_variant(request, pk, id_variant):
    variant = get_object_or_404(Variant, id=id_variant)
    form = VariantForm(instance=variant)
    if request.method == 'POST':
        form = VariantForm(
            request.POST,
            instance=variant)
        if form.is_valid():
            form.save()
        return redirect('tasks:test_detail_admin', pk)
    template = 'tasks/tests/test_detail_admin.html'
    context = {
        'form': form,
        'is_edit': True,
        'test': pk,
        'variant': id_variant
    }
    return render(request, template, context)


@login_required
def delete_variant(request, pk, id_variant):
    variant = get_object_or_404(Variant, id=id_variant)
    variant.delete()
    return redirect('tasks:test_detail_admin', pk)


def add_variants_to_user(request, pk, id):
    '''Ответы юзера на тест'''
    task = get_object_or_404(Task, id=id)
    taskcase = get_object_or_404(TaskCase, pk=pk)
    user = request.user
    form = TestForm(request.POST, task=task, instance=user)
    relation = UserTaskRelation.objects.get(
        user=user,
        task=task,
    )
    correct_variants = Variant.objects.filter(task=task, correct=True)
    user_variants = user.variants.filter(task=task)
    # for field in form:
    #     print("Field Error:", field.name, field.errors)
    # print('test')
    if request.POST and form.is_valid():
        form = TestForm(request.POST, task=task, instance=user)
        form.save(commit=False)
        # form.save_m2m()

        # user.variants.all().delete()
        for variant in form.cleaned_data['variants']:
            user.variants.add(variant)
        user_variants = user.variants.filter(task=task)
        if list(correct_variants) == list(user_variants):
            relation.status = UserTaskRelation.ACCEPT
        else:
            relation.status = UserTaskRelation.WRONG
        relation.save()
        context = {
            'task': task,
            'taskcase': taskcase.id,
            'relation': relation,
            'correct_variants': correct_variants,
            'user_variants': user_variants
        }
        # return redirect('tasks:task_detail', pk, id)
        return render(request, 'tasks/tests/task_detail_test_complete.html', context)
    context = {'form': form,
               'task': task,
               'taskcase': taskcase.id,
               'relation': relation,
               'correct_variants': correct_variants,
               'user_variants': user_variants
               }
    return render(request, 'tasks/tests/task_detail_test.html', context)


class TaskCaseListAdminTest(AdminRequiredMixin, ListView):
    """GenericView листа группы вопросов от юзера"""
    paginate_by = 3
    model = TaskCase
    template_name = 'tasks/tests/test_case_list_admin.html'
    context_object_name = 'task_case'

    def get_queryset(self):
        task_count_new = Task.objects.filter(
            Q(task_relation__status=UserTaskRelation.NEW) | Q(task_relation__status=UserTaskRelation.FOR_REVISION),
            task_case=OuterRef('id'),
            task_relation__user__username=self.kwargs.get('username')).annotate(
            count=Func(F('id'), function='Count')
        ).values('count')
        task_count_oncheck = Task.objects.filter(task_case=OuterRef('id'),
                                                 task_relation__user__username=self.kwargs.get('username'),
                                                 task_relation__status=UserTaskRelation.ON_CHECK).annotate(
            count=Func(F('id'), function='Count')
        ).values('count')
        task_count_accept = Task.objects.filter(task_case=OuterRef('id'),
                                                task_relation__user__username=self.kwargs.get('username'),
                                                task_relation__status=UserTaskRelation.ACCEPT).annotate(
            count=Func(F('id'), function='Count')
        ).values('count')
        task_count_wrong = Task.objects.filter(task_case=OuterRef('id'),
                                                task_relation__user__username=self.kwargs.get('username'),
                                                task_relation__status=UserTaskRelation.WRONG).annotate(
            count=Func(F('id'), function='Count')
        ).values('count')
        return TaskCase.objects.filter(task_case_relation__user__username=self.kwargs.get('username'), is_test=True).annotate(
            WAITING_ANSWER=Subquery(task_count_new),
            ON_CHECK=Subquery(task_count_oncheck),
            ACCEPT=Subquery(task_count_accept),
            WRONG=Subquery(task_count_wrong),
        ).prefetch_related('tasks', 'users')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        context['WAITING_ANSWER'] = user.tasks.filter(Q(task_relation__status=UserTaskRelation.NEW) | Q(
            task_relation__status=UserTaskRelation.FOR_REVISION)).count()
        context['ON_CHECK'] = user.tasks.filter(task_relation__status=UserTaskRelation.ON_CHECK).prefetch_related(
            'tasks', 'task_case').count()
        context['ACCEPT'] = user.tasks.filter(task_relation__status=UserTaskRelation.ACCEPT).prefetch_related('tasks',
                                                                                                              'task_case').count()
        context['title'] = 'СДО авиа'
        context['user'] = user
        return context
# class TestDetail(MyLoginRequiredMixin, UpdateView):
#     """GenericView одного вопроса от пользователя"""
#     model = Task
#     template_name = 'tasks/task_detail.html'
#     context_object_name = 'task'
#     pk_url_kwarg = 'id'
#     extra_context = {'title': 'Вопросы'}
#     form_class = TestForm
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         taskcase = self.kwargs['pk']
#         task = self.kwargs['id']
#         user = self.request.user
#         relation = UserTaskRelation.objects.get(
#             user=user,
#             task=task,
#         )
        # context['answerform'] = AnswerForm
        # context['testform'] = TestForm
    #     context['taskcase'] = taskcase
    #     # context['relation'] = relation
    #     return context
    #
    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['task'] = self.object.id
    #     # kwargs['user'] = self.request.user.id
    #     return kwargs
