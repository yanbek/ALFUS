import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    topic_text = models.CharField(max_length=200,default="x")


    def __str__(self):
        return self.question_text

    def topic(self):
        return self.topic_text

    topic.short_description = 'Sort topic'
    topic.admin_order_field = 'topic_text'


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    correct = models.BooleanField(default=False)

    def is_correct(self):
        return self.correct

    def __str__(self):
        return self.choice_text


class Answer(models.Model):
    submitted_by = models.ForeignKey(User)
    submitted_answer = models.ForeignKey(Choice)
