from django import forms

from tasks.models import Answer, Review, Task, TaskCase, UserTaskRelation
from users.models import User


# class AnswerForm(forms.ModelForm):
#     class Meta:
#         model = UserTaskRelation
#         fields = ('answer',)
#         widgets = {
#             'text': forms.Textarea(attrs={'cols': 50, 'rows': 5})
#         }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'cols': 50, 'rows': 5})
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'cols': 50, 'rows': 5})
        }


class TaskFormTaskcase(forms.ModelForm):
    tasks = forms.ModelMultipleChoiceField(
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
        super().__init__(*args, **kwargs)
        self.fields['tasks'].initial = self.instance.tasks.all()

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        instance.tasks.set(self.cleaned_data['tasks'])
        return instance


class TaskFormTaskcaseUser(forms.ModelForm):
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

