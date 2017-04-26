from django.db.utils import IntegrityError
from django.test import TestCase
from .models import *
from django.contrib.auth.models import User

class QuestionModelsTest(TestCase):


    def setUp(self):
        self.do_print = False

        # Make subject
        self.subject = Subject(name="Matte 1")
        self.subject.save()

        # Make chapters
        self.cha1 = Chapter(name="1",
                            description="A very fun chapter about calculus. Great stuff, must read.",
                            part_of=self.subject)
        self.cha2 = Chapter(name="2", part_of=self.subject)
        self.cha1.save()
        self.cha2.save()

        # Make questions
        self.q1 = Question(question_text="This is a test text.", pub_date=timezone.now(), chapter=self.cha1)
        self.q1.save()
        self.q2 = Question(question_text="This is another test text.", pub_date=timezone.now(), difficulty=0.5, chapter=self.cha1)
        self.q2.save()

        # Make choices
        self.q1Choices = [Choice(question=self.q1, choice_text=str(i), correct=i==0) for i in range(0, 3)]
        self.q2Choices = [Choice(question=self.q2, choice_text=str(i), correct=i==0) for i in range(0, 5)]
        for i in self.q1Choices:
            i.save()
        for i in self.q2Choices:
            i.save()

        # Make users
        try:
            self.u1 = User.objects.create_user("user1", "user1@mail.com", "password")
            self.u2 = User.objects.create_user("user2", "user2@mail.com", "password")
        except IntegrityError:
            #The users are already created
            pass

        # Make the relationship between user and chapter
        temp = hasChapter(user_id=self.u1.pk, chapter_id=self.cha1.pk)
        temp.save()

        # Make relationship between user and questions
        pass





    def test_question_added(self):
        # Test that the questions are in the database
        self.assertTrue(self.q1 in Question.objects.all())
        self.assertTrue(self.q2 in Question.objects.all())

    def test_choice_added(self):
        # Test that the choices are in the database
        self.assertTrue(len(Choice.objects.all()) > 0)

        # Test the question/choice relationship
        for i in Choice.objects.filter(question_id=self.q1.pk):
            self.assertEqual(self.q1, i.question)
        for i in Choice.objects.filter(question_id=self.q2.pk):
            self.assertEqual(self.q2, i.question)


    def test_choice_cascade(self):
        # Creating question and choices
        q = Question(question_text="This is a test text.", pub_date=timezone.now(), chapter=self.cha1)
        q.save()
        pk = q.pk
        choices = [Choice(question=q, choice_text="Choice number " + str(i), correct=i == 0) for i in range(0, 3)]
        for i in choices:
            i.save()
        q.delete()
        # Test that the choices are deleted
        # when its question is deleted
        query_result = Choice.objects.filter(question_id=pk)
        self.assertEqual(len(query_result), 0)
        if self.do_print: print("Query 1: " + str(query_result))

        # Test that q2 is unaffected
        query_result = Choice.objects.filter(question_id=self.q2.pk)
        self.assertTrue(len(query_result) == 5)
        if self.do_print: print("Query 2: " + str(query_result))


        if self.do_print: print("Questions", Question.objects.all())
        if self.do_print: print("Choices to question1", Choice.objects.filter(question_id=self.q1.pk))
        if self.do_print: print("Choices to question2", Choice.objects.filter(question_id=self.q2.pk))

    def test_adding_illegal_choice(self):
        # Creating a choice without a question
        with self.assertRaises(Exception):
            Choice.objects.create(choice_text="Test name")

    def test_subject_added(self):
        self.assertTrue(len(Subject.objects.all()) == 1)

    def test_chapter_user_relationship(self):
        # Test that the relationship is correctly created with the default skill rating
        self.assertEqual(hasChapter.objects.all()[0].skill_rating_chapter, 0.5)

        # Change the skill_rating to a legal value
        u2cha2 = hasChapter(user=self.u2, chapter=self.cha2, skill_rating_chapter=0.2)
        u2cha2.save()
        temp_relationship = hasChapter.objects.get(id=u2cha2.pk)
        temp_relationship.skill_rating_chapter = 0.8
        temp_relationship.save()

        hasChapter.objects.get(id=u2cha2.pk).delete()

    def test_hasAnswered(self):
        # Create user and question
        user = User.objects.create_user("User", "mail@mail.com", "password")
        q = Question(question_text="This is a test text.", pub_date=timezone.now(), chapter=self.cha1)
        q.save()
        choices = [Choice(question=q, choice_text="Choice number " + str(i), correct=i == 0) for i in range(0, 3)]
        for i in choices:
            i.save()

        # Create a hasAnswered relationship
        user_has_answered_q = hasAnswered(submitted_by=user, submitted_answer=q, wasCorrect=False, firstWasCorrect=False)
        user_has_answered_q.save()
        self.assertEqual(len(hasAnswered.objects.all()), 1)

        # Test cascade on delete
        user.delete()
        self.assertEqual(len(hasAnswered.objects.all()), 0)

        # Cleanup
        q.delete()