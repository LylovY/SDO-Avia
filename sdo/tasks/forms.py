from django import forms

from tasks.models import Answer


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'cols': 50, 'rows': 5})
        }