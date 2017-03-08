import datetime

from django.test import TestCase
from django.utils import timezone

from .models import *
from django.contrib.auth.models import User

class QuestionModelsTest(TestCase):


    def setUp(self):
        self.do_print = True

        # Make questions
        self.q1 = Question(question_text="This is a test text.", pub_date=timezone.now())
        self.q1.save()
        self.q2 = Question(question_text="This is another test text.", pub_date=timezone.now(), difficulty=0.5)
        self.q2.save()

        # Make choices
        self.q1Choices = [Choice(question=self.q1, choice_text=str(i), correct=i==0) for i in range(0, 3)]
        self.q2Choices = [Choice(question=self.q2, choice_text=str(i), correct=i==0) for i in range(0, 5)]
        for i in self.q1Choices:
            i.save()
        for i in self.q2Choices:
            i.save()

        # Make subject
        self.subject = Subject(name="Matte 1")

        # Make chapters
        self.cha1 = Chapter(name="1",
            description="A very fun chapter about calculus. Great stuff, must read.", part_of=self.subject)
        self.cha2 = Chapter(name="2", part_of=self.subject)

        # Make users
        #TODO: Fix the user code
        #self.u1 = User.objects.create_user("user1", "user1@mail.com", "password")
        #self.u2 = User.objects.create_user("user2", "user2@mail.com", "password")

        #TODO: Add the rest of the tables and write test for them



    def test_question_added(self):
        # Test that the questions are in the database
        self.assertTrue(self.q1 in Question.objects.all())
        self.assertTrue(self.q2 in Question.objects.all())

    def test_adding_illegal_questions(self):

        # Test that setting illegal values raises an exception
        with self.assertRaises(Exception):
            q = Question(question_text="Test", pub_date=timezone.now(), difficulty=3)
            q.save()
        with self.assertRaises(Exception):
            q = Question(question_text="Test", pub_date=timezone.now(), difficulty=-1)
            q.save()

    def test_choice_added(self):
        # Test that the choices are in the database
        self.assertTrue(len(Choice.objects.all()) > 0)

        # Test the question/choice relationship
        for i in Choice.objects.filter(question_id=self.q1.pk):
            self.assertEqual(self.q1, i.question)
        for i in Choice.objects.filter(question_id=self.q2.pk):
            self.assertEqual(self.q2, i.question)


    def test_choice_cascade(self):
        # Test that the choices are deleted
        # when its question is deleted
        pk = self.q1.pk
        self.q1.delete()
        query_result = Choice.objects.filter(question_id=pk)
        self.assertEqual(len(query_result), 0)
        if self.do_print: print("Query 1: " + str(query_result))

        # Test that q2 is unaffected
        query_result = Choice.objects.filter(question_id=self.q2.pk)
        self.assertTrue(len(query_result) == 5)
        if self.do_print: print("Query 2: " + str(query_result))

        # Restore the setUp state
        self.setUp()
        if self.do_print: print("Questions", Question.objects.all())
        if self.do_print: print("Choices to question1", Choice.objects.filter(question_id=self.q1.pk))
        if self.do_print: print("Choices to question2", Choice.objects.filter(question_id=self.q2.pk))

    def test_adding_illegal_choice(self):
        # Creating a choice without a question
        with self.assertRaises(Exception):
            Choice.objects.create(choice_text="Test name")




