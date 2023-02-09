from django import forms
from django.contrib.auth.forms import UserCreationForm

from tasks.models import Task, TaskCase
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
        fields = ('username', 'first_name')
