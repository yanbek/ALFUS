
from django.urls import reverse
from django.test import TestCase
import personal.forms as forms

from django.contrib.auth.models import User

class PersonalTest(TestCase):

    def setUp(self):
        self.u1 = User.objects.create_user("user1", "user1@mail.com", "password")
        self.u2 = User.objects.create_user("user2", "user2@mail.com", "password")

    def test_index_view(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_login_view_redirect(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 302)

    def test_login_view(self):
        User.objects.create_user("test1234", "user1@mail.com", "averystrongpassword")
        form_data = {"username": "test1234", "password": "averystrongpassword"}
        response = self.client.post(reverse("login"), form_data)
        self.assertEqual(response.status_code, 302)

    def test_logout_view(self):
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 200)

    def test_register_view(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_login_form_valid(self):
        User.objects.create_user("test1234", "user1@mail.com", "averystrongpassword")
        form_data = {"username": "test1234", "password": "averystrongpassword"}

        form = forms.UserLoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_valid(self):
        #"username", "first_name", "last_name", "email", "password1", "password2"
        form_data = {"username": "Auser", "first_name": "ghj", "last_name": "cv", "email": "ads@asd.no",
                     "password1": "averystrongpassword", "password2": "averystrongpassword"}
        form = forms.UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_invalid(self):
        form_data = {"username": "Auser", "first_name": "ghj", "last_name": "cv", "email": "ads@asd.no",
                     "password1": "averystrongpassword", "password2": "av"}
        form = forms.UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
