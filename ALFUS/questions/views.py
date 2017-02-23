from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.http import Http404
from .models import Choice, Question
import random

def index(request):
    all_question_id = Question.objects.values_list('id', flat=True)
    request.session['question_ids'] = list(all_question_id)
    question_list = Question.objects.all
    return render(request, 'questions/index.html', {'question_list': question_list})


def detail(request, question_id):
    try:
        question = get_object_or_404(Question, pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question doesn't exist")
    return render(request, 'questions/detail.html', {'question': question})


def answer(request, question_id):
    questions_not_answered = request.session['question_ids']
    questions_not_answered.remove(int(question_id))
    request.session['question_ids'] = questions_not_answered
    next_question_id = random.choice(questions_not_answered)
    question = get_object_or_404(Question, pk=question_id)

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'questions/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice."
        })
    else:
        return render(request, 'questions/results.html', {'question': question, 'is_correct': selected_choice.is_correct, 'random_q': next_question_id})

