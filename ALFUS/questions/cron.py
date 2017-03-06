from django_cron import CronJobBase, Schedule
from .models import hasAnswered, Question
from collections import defaultdict
from django.conf import settings

class Difficulty_adjustment(CronJobBase):
    RUN_EVERY_MINS = 0 if settings.DEBUG else 360

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'cron.Difficulty_adjustment'

    def do(self):

        # Difficulty weight of each question is adjusted according to prior scoring.
        question_dict = defaultdict(list)

        try:
            prior_answers = hasAnswered.objects.all()
            for prior_answer in prior_answers:
                question_dict[prior_answer.submitted_answer_id].append(prior_answer.wasCorrect)
            for question_id in question_dict:
                total_answers = len(question_dict[question_id])
                correct_answers = sum(question_dict[question_id])
                if total_answers == 0:
                    new_difficulty = 0
                else:
                    new_difficulty = float(total_answers - correct_answers) / float(total_answers)
                question = Question.objects.get(pk=question_id)
                question.difficulty = new_difficulty
                question.save()
            print("Difficulty weights have been successfully updated")
        except:
            print("Updating difficulty failed")
