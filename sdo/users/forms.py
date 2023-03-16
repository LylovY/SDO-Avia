from django import forms
from django.contrib.auth.forms import UserCreationForm

from tasks.models import Task, TaskCase, UserTaskRelation
from users.models import User


class TaskCaseForm(forms.ModelForm):
    """Форма добавления юзеру группы вопросов"""
    task_case = forms.ModelMultipleChoiceField(
        queryset=TaskCase.objects.all(),
        label='Группы вопросов',
        help_text='Назначьте группы вопросов',
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = User
        fields = ['task_case']

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        taskcases = self.cleaned_data['task_case']
        print(taskcases)

        # Get all tasks for selected taskcases
        tasks = Task.objects.filter(task_case__in=taskcases)
        print((tasks))

        # Get all relations for selected tasks and user
        relations = UserTaskRelation.objects.filter(user=instance, task__in=tasks)

        relations.exclude(task__in=tasks).delete()

        instance.tasks.set(tasks)

        return instance


class TaskFormUser(forms.ModelForm):
    """Форма добавления юзеру вопросов"""
    tasks = forms.ModelMultipleChoiceField(
        queryset=Task.objects.all(),
        label='Вопросы',
        help_text='Назначьте вопросы',
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = User
        fields = ['tasks']


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'parol')
