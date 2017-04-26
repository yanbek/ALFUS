from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from django.db.models import signals


# Extends the user model.
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


# Subject model
class Subject(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

# Chapter model
class Chapter(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, blank=True, default='')
    part_of = models.ForeignKey(Subject)

    def __str__(self):
        return self.name

# Question model
# Difficulty 0 is the easiest and 1 is the hardest
class Question(models.Model):
    question_text = models.CharField(max_length=700)
    pub_date = models.DateTimeField('date published')
    difficulty = models.FloatField(default=0.5)
    topic_text = models.CharField(max_length=200,default="x")
    chapter = models.ForeignKey(Chapter)
    question_image = models.ImageField(upload_to = "static/images/questions",  blank=True, null=True)

    def __str__(self):
        return self.question_text

    def topic(self):
        return self.topic_text

    topic.short_description = 'Sort topic'
    topic.admin_order_field = 'topic_text'

# Model for the different answer choices for the questions
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    correct = models.BooleanField(default=False)

    def is_correct(self):
        return self.correct

    def __str__(self):
        return self.choice_text

# Model for related information links (for the questions=
class Urls(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    help_links = models.URLField(max_length=400)
    description = models.CharField(max_length=200, default="x")

    def __str__(self):
        return self.help_links

    def desc(self):
        return self.description


# Model for the relationship between user and question
# Each user has a hasAnswer object for every question the user has answered
# firstWasCorrect attribute is used for updating difficulties
class hasAnswered(models.Model):
    wasCorrect = models.BooleanField()
    firstWasCorrect = models.BooleanField()
    answer_attempt = models.IntegerField(default=1)
    submitted_by = models.ForeignKey(User)
    submitted_answer = models.ForeignKey(Question)


# Model for the relationship between user and chapter
# Each user has a hasChapter object for every chapter
class hasChapter(models.Model):
    skill_rating_chapter = models.FloatField(default=0.5)
    chapter_attempt = models.IntegerField(default=1)
    user = models.ForeignKey(User)
    chapter = models.ForeignKey(Chapter)

    def __str__(self):
        return str(self.skill_rating_chapter)
















