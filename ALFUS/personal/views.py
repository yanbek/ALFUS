from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import UserForm
from .forms import LoginForm


def index(request):
    return render(request, 'personal/home.html')


def contact(request):
    return render(request, 'personal/basic.html', {'content': ['Test']})


def login_view(request):
    template_name = "personal/login.html"

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            u = form.cleaned_data["username"]
            p = form.cleaned_data["password"]
            user = authenticate(username=u, password=p)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect("/")
                else:
                    print("The account has been disabled!")
            else:
                print("This user does not exist!")

    else:
        form = LoginForm()
        return render(request, "personal/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")


class UserFormView(View):
    form_class = UserForm
    template_name = "personal/registration_form.html"

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user.set_password(password)
            user.save()

            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, login())
                    return HttpResponseRedirect("/")

        return render(request, self.template_name, {"form": form})
