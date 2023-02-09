from django import forms
from django.forms import models
from django.utils.html import format_html
from django import urls

from tasks.models import Answer, Review, Task, TaskCase
from users.models import User


class CustomModelChoiceField(models.ModelMultipleChoiceField):
    """Переобределенный лейбл формы ModelMultipleChoice с добавлением ссылки на объект"""
    def label_from_instance(self, obj):
        link = urls.reverse('tasks:task_detail_admin', args=[obj.id])
        return format_html('<a class="text-decoration-none text-reset" href="{}">{}</a>', link, obj.title)


class AnswerForm(forms.ModelForm):
    """Форма для ответа на вопрос"""
    class Meta:
        model = Answer
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'cols': 50, 'rows': 5})
        }


class ReviewForm(forms.ModelForm):
    """Форма для ревью на ответы"""
    class Meta:
        model = Review
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'cols': 50, 'rows': 5})
        }


class TaskFormTaskcase(forms.ModelForm):
    """Форма добавления вопросов в группы вопросов"""
    tasks = CustomModelChoiceField(
        queryset=Task.objects.all(),
        label='Вопросы',
        help_text='Назначьте вопросы',
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = TaskCase
        fields = ['tasks']

    def __init__(self, *args, **kwargs):
        """Добавление в данные формы related поле """
        super().__init__(*args, **kwargs)
        self.fields['tasks'].initial = self.instance.tasks.all()

    def save(self, *args, **kwargs):
        """Сохранение данные в related поле """
        instance = super().save(*args, **kwargs)
        instance.tasks.set(self.cleaned_data['tasks'])
        return instance


class TaskFormTaskcaseUser(forms.ModelForm):
    """Форма назначения группы вопросов пользователям"""
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        label='Пользователи',
        help_text='Назначьте пользователей',
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = TaskCase
        fields = ['users']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['users'].initial = self.instance.users.all()

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        instance.users.set(self.cleaned_data['users'])
        return instance

