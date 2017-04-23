from collections import defaultdict

from django.test import TestCase
from django.urls import reverse
from django.contrib.sessions.models import Session

from .models import *

class ViewTest(TestCase):

    def setUp(self):
        self.do_print = False



        # Make subject
        self.subject = Subject(name="Matte 1")
        self.subject.save()

        # Make chapters
        self.cha1 = Chapter(name="1",
                            description="A very fun chapter about calculus. Great stuff, must read.",
                            part_of=self.subject)
        self.cha1.save()

        # Make questions
        self.q1 = Question(question_text="This is a test text.", pub_date=timezone.now(), chapter=self.cha1, difficulty=0.1)
        self.q1.save()
        self.q2 = Question(question_text="This is another test text.", pub_date=timezone.now(),chapter=self.cha1, difficulty=0.9)
        self.q2.save()

        # Make choices
        self.q1Choices = [Choice(question=self.q1, choice_text=str(i), correct=i==0) for i in range(0, 3)]
        self.q2Choices = [Choice(question=self.q2, choice_text=str(i), correct=i==0) for i in range(0, 5)]
        for i in self.q1Choices:
            i.save()
        for i in self.q2Choices:
            i.save()

        # Make users
        self.users = [User.objects.create_user("user" + str(i), "user" + str(i) + "@mail.com", "password") for i in range(0, 30)]

        hasCha = hasChapter(user=self.users[1], chapter=self.cha1)
        hasCha.save()

        # Make relationship between user and questions
        pass

    def test_login(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse("questions:index"))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_login_denied(self):
        response = self.client.get(reverse("questions:index"))
        self.assertRedirects(response, "/login/?next=/questions/")

    def test_selecting_course(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse("questions:index_questions", args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_view_question(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse("questions:detail", args=[1, 1]))
        self.assertEqual(response.status_code, 200)

    def test_view_invalid_question_gives_404(self):
        self.client.login(username='user1', password='password')

        response = self.client.get(reverse("questions:detail", args=[1, 598]))
        self.assertEqual(response.status_code, 404)

    def test_search(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse("questions:search"))
        self.assertEqual(response.status_code, 200)

    def test_answer(self):
        self.client.login(username='user1', password='password')
        question_list = Question.objects.filter(chapter__part_of_id=1)
        question_dict = defaultdict(list)
        for question in question_list:
            question_dict[question.chapter_id].append((question.id, question.difficulty))
        s = self.client.session
        s['question_dict'] = question_dict
        s.save()
        self.client.post(reverse("questions:answer", args=[1, 1]), {"choice" : 1})
        response = self.client.get(reverse("questions:answer", args=[1, 1]))
        self.assertEqual(response.status_code, 200)
