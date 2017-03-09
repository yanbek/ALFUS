from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
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
        return redirect("../questions")
    elif request.user.is_authenticated():
        return redirect("../questions")

    return render(request, "personal/form.html", {"form": form, "title": title})


def logout_view(request):
    logout(request)
    return render(request, "personal/home.html")


def reqister_view(request):
    title = "Register"
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get("password")
        user.set_password(password)
        user.save()
        new_user = authenticate(username=user.username, password=password)
        login(request, new_user)
        return redirect("/")


    context = {"form": form, "title": title}
    return render(request, "personal/form.html", context)
