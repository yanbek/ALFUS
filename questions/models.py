import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import signals

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')

    def __str__(self):
          return "%s's profile" % self.user

    def create_profile(sender, instance, created, *args, **kwargs):
        # ignore if this is an existing User
        if not created:
            return
        UserProfile.objects.create(user=instance)
    signals.post_save.connect(create_profile, sender=User)

class Subject(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Chapter(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, blank=True, default='')
    part_of = models.ForeignKey(Subject)

    def __str__(self):
        return self.name

class Question(models.Model):
    question_text = models.CharField(max_length=700)
    pub_date = models.DateTimeField('date published')
    # 0 is the easiest and 1 is the hardest
    difficulty = models.FloatField(default=0.5)
    topic_text = models.CharField(max_length=200,default="x")
    chapter = models.ForeignKey(Chapter)

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
    
class Urls(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    help_links = models.URLField(max_length=400)
    description = models.CharField(max_length=200, default="x")

    def __str__(self):
        return self.help_links

    def desc(self):
        return self.description


# A table for the relationship between user and question
class hasAnswered(models.Model):
    wasCorrect = models.BooleanField()
    firstWasCorrect = models.BooleanField()
    answer_attempt = models.IntegerField(default=1)
    submitted_by = models.ForeignKey(User)
    submitted_answer = models.ForeignKey(Question)

# A table for the relationship between user and chapter
class hasChapter(models.Model):
    skill_rating_chapter = models.FloatField(default=0.5)
    chapter_attempt = models.IntegerField(default=1)
    user = models.ForeignKey(User)
    chapter = models.ForeignKey(Chapter)

    def __str__(self):
        return str(self.skill_rating_chapter)
















