from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, get_user_model


class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=64, widget=forms.TextInput(
        attrs={'class': 'form-control', 'style': 'text-align:center'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'style': 'text-align:center'}))


class UserRegisterForm(forms.ModelForm):
    username = forms.CharField(label="Choose your username", max_length=64, widget=forms.TextInput(
        attrs={'class': 'form-control', 'style': 'text-align:center'}))
    email = forms.EmailField(label="Email address", widget=forms.TextInput(
        attrs={'class': 'form-control', 'style': 'text-align:center'}))
    password1 = forms.CharField(min_length=6, widget=forms.PasswordInput(attrs={'class': 'form-control', 'style': 'text-align:center'}), label="Create a password")
    password2 = forms.CharField(min_length=6, widget=forms.PasswordInput(attrs={'class': 'form-control', 'style': 'text-align:center'}), label="Confirm your password")
    first_name = forms.CharField(label="First name", max_length=64, widget=forms.TextInput(
        attrs={'class': 'form-control', 'style': 'text-align:center'}))
    last_name = forms.CharField(label="Last name", max_length=64, widget=forms.TextInput(
        attrs={'class': 'form-control', 'style': 'text-align:center'}))

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")

        if User.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError("The username is already taken.")

        return self.cleaned_data

User = get_user_model()


class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'style': 'text-align:center'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'style': 'text-align:center'}))

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        if username and password:
            if not user:
                raise forms.ValidationError("This user does not exist.")
            if not user.check_password(password):
                raise forms.ValidationError("Incorrect password.")
            if not user.is_active:
                raise forms.ValidationError("This user is not longer active.")
        return super(UserLoginForm, self).clean(*args, **kwargs)
