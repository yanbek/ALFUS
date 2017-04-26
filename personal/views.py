from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from .forms import UserLoginForm


#Get home page
def index(request):
    return render(request, 'personal/home.html')


#Login page, loges the user in if the form is valid
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

    return render(request, "personal/loginForm.html", {"form": form, "title": title})


#Logout
def logout_view(request):
    logout(request)
    return render(request, "personal/home.html")


#Login link for forgot password
def go_login_view(request):
    return redirect("login")


#Registration page. Make new user if the form is valid
def register_view(request):
    title = "Register"
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get("password1")
        user.set_password(password)
        user.save()
        new_user = authenticate(username=user.username, password=password)
        login(request, new_user)
        return render(request, "registration_complete/registration_complete.html")

    context = {"form": form, "title": title}
    return render(request, "personal/form.html", context)
