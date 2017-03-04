import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    # 0 is the easiest and 1 is the hardest
    difficulty = models.FloatField()

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    correct = models.BooleanField(default=False)

    def is_correct(self):
        return self.correct

    def __str__(self):
        return self.choice_text
class Subject(models.Model):
    name = models.CharField(max_length=200)

class Chapter(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    part_of = models.ForeignKey(Subject)

# A table for the relationship between user and question
class hasAnswered(models.Model):
    wasCorrect = models.BooleanField()
    submitted_by = models.ForeignKey(User, blank=True)
    submitted_answer = models.ForeignKey(Question, blank=True)


class hasSubject(models.Model):
    skill_rating = models.FloatField(default=0)
    user = models.ForeignKey(User, blank=True)
    subject = models.ForeignKey(Subject, blank=True)

#Old code, now redundant
#class Answer(models.Model):
#    submitted_by = models.ForeignKey(User)
#    submitted_answer = models.ForeignKey(Choice)




























