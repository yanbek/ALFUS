from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404
from .models import Choice, Question, hasAnswered, hasChapter, Chapter
from collections import defaultdict
import math


def index(request):
    question_list = Question.objects.all()

    populate_questions_dict(question_list, request)

    return render(request, 'questions/index.html', {'question_list': question_list})


def populate_questions_dict(question_list, request):
    question_dict = defaultdict(list)
    for question in question_list:
        question_dict[question.chapter_id].append((question.id, question.difficulty))
    request.session['question_dict'] = question_dict


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
        new_answer = hasAnswered(wasCorrect=isCorrect, submitted_by=request.user, submitted_answer=question)
        new_answer.save()

        # Update chapter skill rating (just using correct answer / total answers now)
        prior_user_answers_to_current_chapter = hasAnswered.objects.filter(submitted_by=request.user,
                                                                           submitted_answer__chapter=question.chapter_id)
        answer_list = []

        for prior_answer in prior_user_answers_to_current_chapter:
            answer_list.append(prior_answer.wasCorrect)
        total_answers = len(answer_list)
        correct_answers = sum(answer_list)
        updated_skill_rating = float(total_answers - correct_answers) / float(total_answers)
        if not hasChapter.objects.filter(user=request.user, chapter=question.chapter_id).exists():
            user_hasChapter_current = hasChapter(user=request.user, chapter=Chapter.objects.get(pk=question.chapter_id))
        else:
            user_hasChapter_current = hasChapter.objects.get(user=request.user, chapter=question.chapter_id)
        user_hasChapter_current.skill_rating_chapter = updated_skill_rating
        user_hasChapter_current.save()

        # Get next question by selecting an unanswered question that match the current skill rating.
        # This is most likely not the most optimal solution..

        next_question_id = None
        delta = 1
        for chapter in question_dict:

            if not hasChapter.objects.filter(user=request.user, chapter=chapter).exists():
                user_hasChapter = hasChapter(user=request.user, chapter=Chapter.objects.get(pk=chapter))
                user_hasChapter.save()
            skill_rating_chapter = hasChapter.objects.values_list('skill_rating_chapter', flat=True).get(
                user=request.user, chapter=chapter)
            if question_dict[chapter]:
                for question_to_be_checked in question_dict[chapter]:
                    if hasAnswered.objects.filter(submitted_by=request.user,
                                                  submitted_answer=question_to_be_checked[0]).exists():
                        question_dict[chapter].remove(question_to_be_checked)
                    else:
                        if math.fabs(question_to_be_checked[1] - skill_rating_chapter) < delta:
                            delta = math.fabs(question_to_be_checked[1] - skill_rating_chapter)
                            next_question_id = question_to_be_checked[0]
            request.session['question_dict'] = question_dict

        if next_question_id is None:
            return redirect('index')

    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'questions/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice."
        })
    else:
        return render(request, 'questions/results.html',
                      {'question': question, 'is_correct': selected_choice.is_correct,
                       'next_question': next_question_id})
