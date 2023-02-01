from django import forms

from tasks.models import TaskCase
from users.models import User


class TaskCaseForm(forms.ModelForm):
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