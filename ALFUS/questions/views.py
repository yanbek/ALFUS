from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404
from .models import Choice, Question, hasAnswered, hasChapter, Chapter
from collections import defaultdict
from django.db.models import Max
import math


def index(request):
    question_list = Question.objects.all()

    question_dict = defaultdict(list)
    for question in question_list:
        question_dict[question.chapter_id].append((question.id, question.difficulty))
    request.session['question_dict'] = question_dict

    return render(request, 'questions/index.html', {'question_list': question_list})


def detail(request, question_id):
    try:
        question = get_object_or_404(Question, pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question doesn't exist")
    return render(request, 'questions/detail.html', {'question': question})


def answer(request, question_id):
    question_dict = request.session['question_dict']
    question = get_object_or_404(Question, pk=question_id)

    try:
        # Save answer
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
        isCorrect = selected_choice.correct
        # If already answered this question, create new answer with increased counter
        new_answer = hasAnswered(wasCorrect = isCorrect, submitted_by=request.user, submitted_answer=question)
        if hasAnswered.objects.filter(submitted_by=request.user, submitted_answer=question).exists():
            old_answer = hasAnswered.objects.filter(submitted_by=request.user, submitted_answer=question).latest('answer_attempt')
            new_answer.answer_attempt = old_answer.answer_attempt + 1
        new_answer.save()

        # Find new chapter skill rating. The rating is calculated by the formula  total correct answer / total answer
        prior_user_answers_to_current_chapter = hasAnswered.objects.filter(submitted_by=request.user,
                                                                           submitted_answer__chapter=question.chapter_id)
        answer_list = []

        for prior_answer in prior_user_answers_to_current_chapter:
            answer_list.append(prior_answer.wasCorrect)
        total_answers = len(answer_list)
        correct_answers = sum(answer_list)
        updated_skill_rating = float(correct_answers) / float(total_answers)

        # Check if the hasChapter relationship exists. If not exists, create one.
        if not hasChapter.objects.filter(user=request.user, chapter=question.chapter_id).exists():
            user_hasChapter_current = hasChapter(user=request.user, chapter=Chapter.objects.get(pk=question.chapter_id))
        else:
            user_hasChapter_current = hasChapter.objects.get(user=request.user, chapter=question.chapter_id)
        user_hasChapter_current.skill_rating_chapter = updated_skill_rating
        user_hasChapter_current.save()

        # Get next question by selecting an unanswered question that match the current skill rating.
        # Prioritize chapters with lower skill rating.
        # The question that gives the lowest delta is the winner.
        next_question_id = None
        chapter_priority_constant = 1
        delta = 1.0
        for chapter in question_dict:
            # Check if the hasChapter relationship exists. If not exists, create one with default skill rating 0.5
            if not hasChapter.objects.filter(user=request.user, chapter=chapter).exists():
                user_hasChapter = hasChapter(user=request.user, chapter=Chapter.objects.get(pk=chapter))
                user_hasChapter.save()
            # Get chapter skill rating
            skill_rating_chapter = hasChapter.objects.values_list('skill_rating_chapter', flat=True).get(
                user=request.user, chapter=chapter)
            # Iterate over the chapter list and see if there is any unanswered question that gives us a lower delta.
            for question_to_be_checked in question_dict[chapter]:

                new_delta = math.fabs(question_to_be_checked[1] - skill_rating_chapter) * (
                    skill_rating_chapter * chapter_priority_constant)

                if (not hasAnswered.objects.filter(submitted_by=request.user,
                                                   submitted_answer=question_to_be_checked[
                                                       0], answer_attempt=request.user.profile.test_attempt).exists()) and new_delta < delta:
                    delta = new_delta
                    next_question_id = question_to_be_checked[0]

        if next_question_id is None:
            # User has answered every question. Increment user test attempt counter (reset test).
            request.user.profile.test_attempt += 1
            request.user.profile.save()
            return redirect('index')

    except (KeyError, Choice.DoesNotExist):  # Redisplay the question voting form.

        return render(request, 'questions/detail.html', {
            'question': question,
            '   error_message': "You didn't select a choice."
        })
    else:
        return render(request, 'questions/results.html',
                      {'question': question, 'is_correct': selected_choice.is_correct,
                       'next_question': next_question_id})
