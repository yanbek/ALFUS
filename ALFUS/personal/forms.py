from django.contrib.auth.models import User
from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label="User Name", max_length=64, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]