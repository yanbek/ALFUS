from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.forms import TextInput


class AnswerForm(forms.Form):
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer
        
class ChangeEmailForm(UserChangeForm):

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = {
            'email',
            'password'
        }
        widgets = {
            'email': TextInput(attrs={'class': 'form-control'}),
        }

