from django import forms
from django.forms import models
from django.shortcuts import get_object_or_404
from django.utils.html import format_html
from django import urls
from django_summernote.widgets import SummernoteWidget

from tasks.models import Answer, Review, Task, TaskCase, UserTaskRelation, Variant
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

        # Если Блок-тест, то выбираем только вопросы-тесты, иначе наоборот
        is_test = self.instance.is_test
        if is_test:
            self.fields['tasks'].queryset = Task.objects.filter(is_test=True)
        else:
            self.fields['tasks'].queryset = Task.objects.filter(is_test=False)

        # Добавляет в форму уже выбранные вопросы
        self.fields['tasks'].initial = self.instance.tasks.all()
        # self.fields['tasks'].initial = self.instance.tasks.all()


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

    # def save(self, *args, **kwargs):
    #     instance = super().save(*args, **kwargs)
    #     instance.users.set(self.cleaned_data['users'])
    #     return instance
    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        selected_users = self.cleaned_data['users']
        current_users = instance.users.all()

        # Remove UserTaskRelation for users not selected in the form
        for user in current_users:
            if user not in selected_users:
                relations = UserTaskRelation.objects.filter(user=user, task__in=instance.tasks.all())
                relations.delete()

        instance.users.set(selected_users)
        return instance


class VariantForm(forms.ModelForm):
    """Форма для ответа на вопрос"""
    class Meta:
        model = Variant
        fields = ('text', 'correct')
        widgets = {
            'text': forms.Textarea(attrs={'cols': 50, 'rows': 5}),
            'correct': forms.CheckboxInput()
        }


class TestForm(forms.ModelForm):
    """Форма для ответа на вопрос"""
    def __init__(self, *args, **kwargs):
        task_id = kwargs.pop("task", None)
        # user = kwargs.pop("user", None)
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields['variants'].queryset = Variant.objects.filter(
            task=task_id
        )

    variants = forms.ModelMultipleChoiceField(
        queryset=Variant.objects.none(),
        label='Варианты',
        help_text='Выберите правильные',
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = User
        fields = ('variants',)


class CreateTaskForm(forms.ModelForm):
    """Форма для создания и редактирования вопроса"""

    def __init__(self, *args, **kwargs):
        super(CreateTaskForm, self).__init__(*args, **kwargs)

        # task_case фильтруем только по is_test=false
        self.fields['task_case'].queryset = TaskCase.objects.filter(is_test=False)

    description = forms.CharField(widget=SummernoteWidget, label='Вопрос')

    class Meta:
        model = Task
        fields = ('title', 'description', 'answer', 'task_case')
        widgets = {
            'answer': forms.Textarea(attrs={'cols': 50, 'rows': 3})
        }


class CreateTaskTestForm(forms.ModelForm):
    """Форма для создания и редактирования теста"""

    description = forms.CharField(widget=SummernoteWidget, label='Описание теста')

    def __init__(self, *args, **kwargs):
        super(CreateTaskTestForm, self).__init__(*args, **kwargs)
        self.fields['is_test'].disabled = True
        self.fields['is_test'].initial = True

        # task_case фильтруем только по is_test=true
        self.fields['task_case'].queryset = TaskCase.objects.filter(is_test=True)

    class Meta:
        model = Task
        fields = ('title', 'description', 'task_case', 'is_test')
        # widgets = {
        #     'description': forms.Textarea(attrs={'cols': 50, 'rows': 3})
        # }

    # def save(self, *args, **kwargs):
    #     instance = super().save(*args, **kwargs)
    #     user = get_object_or_404(User, username__id=self.cleaned_data['user'])
    #     user.variants.set(self.cleaned_data['variants'])
    #     return instance

    # def __init__(self, *args, **kwargs):
    #     author_id = kwargs.pop("user", None)
    #     forms.ModelForm.__init__(self, *args, **kwargs)
    #     self.fields['directories'].queryset = Directory.objects.filter(
    #         owner=author_id
    #     )
    #
    # directories = forms.ModelMultipleChoiceField(
    #     queryset=Directory.objects.none(),
    #     label='Папки',
    #     help_text='Please select the article to recover',
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False,
    # )

    # class Meta:
    #     model = Track
    #     fields = ('directories',)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['users'].initial = self.instance.users.all()
    #
    # def save(self, *args, **kwargs):
    #     instance = super().save(*args, **kwargs)
    #     instance.users.set(self.cleaned_data['users'])
    #     return instance