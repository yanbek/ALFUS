from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(label="User name", max_length=64, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserForm(forms.ModelForm):
    username = forms.CharField(label="User name", max_length=64, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.CharField(label="Email address", max_length=64, widget=forms.TextInput(
        attrs={'class': 'form-control', 'for': 'exampleInputEmail1'}))
    first_name = forms.CharField(label="First name", max_length=64, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Last name", max_length=64, widget=forms.TextInput(
        attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]
