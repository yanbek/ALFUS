import datetime

from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

from .cron import Difficulty_adjustment as DA
from .models import *
from django.contrib.auth.models import User

class DynamicDifficultyTest(TestCase):

    def setUp(self):
        self.do_print = False

        self.da = DA()

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



        # Make relationship between user and questions
        pass

    def test_difficulty_adjustment_q1(self):
        # Make all the users answer wrong
        q1pk = self.q1.pk
        old_difficulty = Question.objects.get(pk=q1pk).difficulty
        for user in self.users:
            has_answered = hasAnswered(wasCorrect=False, submitted_by=user, submitted_answer=Question.objects.get(pk=q1pk))
            has_answered.save()

        # Make a instance of the difficulty_adjustment class

        self.da.do()

        # Check if the difficulty has increased
        new_difficulty = Question.objects.get(pk=q1pk).difficulty
        self.assertTrue(old_difficulty < new_difficulty)

    def test_difficulty_adjustment_q2(self):
        # Make all the users answer right
        q2pk = self.q2.pk
        old_difficulty = Question.objects.get(pk=q2pk).difficulty
        for user in self.users:
            has_answered = hasAnswered(wasCorrect=True, submitted_by=user, submitted_answer=Question.objects.get(pk=q2pk))
            has_answered.save()

        # Make a instance of the difficulty_adjustment class

        self.da.do()

        # Check if the difficulty has decreased
        new_difficulty = Question.objects.get(pk=q2pk).difficulty
        self.assertTrue(old_difficulty > new_difficulty)