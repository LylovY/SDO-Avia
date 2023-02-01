from django import forms

from tasks.models import Answer, TaskCase, UserTaskRelation
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


