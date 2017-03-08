from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View
from .forms import UserRegisterForm
from .forms import UserLoginForm

def index(request):
    return render(request, 'personal/home.html')


def contact(request):
    return render(request, 'personal/basic.html', {'content': ['Test']})


def login_view(request):
    title = "Login"
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        login(request, user)
        # redirect

    return render(request, "personal/form.html", {"form": form, "title": title})


def logout_view(request):
    logout(request)
    return render(request, "personal/home.html")


def reqister_view(request):
    title = "Register"
    form = UserRegisterForm(request.POST or None)

    context = {"form": form, "title": title}
    return render(request, "personal/form.html", context)
