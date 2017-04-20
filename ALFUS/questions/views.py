from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect, render_to_response
from django.http import Http404
from .models import Choice, Question, hasAnswered, hasChapter, Chapter, Subject
from collections import defaultdict
from django.db.models import Max
from django.utils import timezone
import math
from random import randint
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from .forms import ChangeEmailForm
from django.db.models import Q, F
from django.db.models import Q, F
from itertools import chain

@login_required(login_url="/login/")
def change_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST,instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('/questions/profile')
    else:
        form = ChangeEmailForm(instance=request.user)
        args = {'form': form}
        return render(request, 'questions/change_email.html', args)


@login_required(login_url="/login/")
def del_user(request):
    try:
        u = request.user
        u.delete()
        return redirect('/questions/profile')

    except request.user.DoesNotExist:
        return render(request, 'questions/not_deleted.html')

    except Exception as e:
        return render(request, 'questions/not_deleted.html')



@login_required(login_url="/login/")
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return HttpResponseRedirect('/questions/profile')
    else:
        form = PasswordChangeForm(user=request.user)
        args = {'form': form}
        return render(request, 'questions/change_password.html', args)


@login_required(login_url="/login/")
def profile(request):
    return render(request, 'questions/profile.html')

@login_required(login_url="/login/")
def search(request):
    try:
        q = request.GET['q']
        topics = Question.objects.filter(topic_text__icontains=q)
        return render_to_response('questions/search.html', {'topics': topics, 'q': q})
    except KeyError:
        return render_to_response('questions/search.html')


@login_required(login_url="/login/")
def index(request):
    questions_chapter = {}
    questions_chapter_answered = {}
    questions_in_subject = {}
    questions_in_subject_answered = {}
    current_user = request.user
    questions_by_user = hasAnswered.objects.all().filter(submitted_by=current_user, wasCorrect=True)

    for i in Chapter.objects.all():
        questions_chapter_answered[i] = 0
        questions = Question.objects.filter(chapter=i)
        questions_chapter[i] = len(questions)

        for s in list(questions_by_user):
            if s.submitted_answer.chapter == i:
                questions_chapter_answered[i] += 1

    for t in Subject.objects.all():
        questions_in_subject[t] = 0
        questions_in_subject_answered[t] = 0
        for chapter in questions_chapter.keys():
            if chapter.part_of == t:
                questions_in_subject[t] += questions_chapter[chapter]

        for chapter in questions_chapter_answered.keys():
            if chapter.part_of == t:
                questions_in_subject_answered[t] += questions_chapter_answered[chapter]

    subject = []
    subject_answered = []
    count = []
    for q in questions_in_subject.keys():
        subject.append(q)
        subject_answered.append(questions_in_subject_answered[q])
        count.append(questions_in_subject[q])

    zipped = zip(subject, subject_answered, count)
    return render(request, 'questions/index.html', {'subject_list': zipped})


@login_required(login_url="/login/")
def index_questions(request, subject_id):
    questions_chapter = {}
    questions_chapter_answered = {}
    questions_in_subject = {}
    questions_in_subject_answered = {}
    current_user = request.user
    questions_by_user = hasAnswered.objects.all().filter(submitted_by=current_user, wasCorrect=True)

    for i in Chapter.objects.all():
        questions_chapter_answered[i] = 0
        questions = Question.objects.filter(chapter=i)
        questions_chapter[i] = len(questions)

        for s in list(questions_by_user):
            if s.submitted_answer.chapter == i:
                questions_chapter_answered[i] += 1

        subject = Subject.objects.get(pk=subject_id)

        for chapter in questions_chapter.keys():
            if chapter.part_of == subject:
                questions_in_subject[chapter] = questions_chapter[chapter]

        for chapter in questions_chapter_answered.keys():
            if chapter.part_of == subject:
                questions_in_subject_answered[chapter] = questions_chapter_answered[chapter]

    print(questions_in_subject)
    print(questions_in_subject_answered)
    chapter = []
    percent = []

    for q in questions_in_subject.keys():
        chapter.append(q)
        percent.append(questions_in_subject_answered[q]/questions_in_subject[q])
    zipped = zip(chapter, percent)





    question_list = Question.objects.filter(chapter__part_of_id=subject_id)
    subject_name = Subject.objects.get(pk=subject_id)

    question_dict = defaultdict(list)
    for question in question_list:
        question_dict[question.chapter_id].append((question.id, question.difficulty))
    request.session['question_dict'] = question_dict
    return render(request, 'questions/index_questions.html',
                  {'question_list': question_list, 'subject_id': subject_id, 'subject_name': subject_name, "chapters": zipped})


@login_required(login_url="/login/")
def detail(request, question_id, subject_id):
    try:
        question = get_object_or_404(Question, pk=question_id)
        # Check if the hasChapter relationship exists. If not exists, create one.
        if not hasChapter.objects.filter(user=request.user, chapter=question.chapter_id).exists():
            haschapter = hasChapter(user=request.user, chapter=Chapter.objects.get(pk=question.chapter_id))
            haschapter.save()
        else:
            haschapter = hasChapter.objects.get(user=request.user, chapter=question.chapter_id)
    except Question.DoesNotExist:
        raise Http404("Question doesn't exist")
    return render(request, 'questions/detail.html',
                  {'question': question, 'haschapter': haschapter, 'subject_id': subject_id})


@login_required(login_url="/login/")
def answer(request, question_id, subject_id):
    question_dict = request.session['question_dict']

    question = get_object_or_404(Question, pk=question_id)
    try:
        # Save answer
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
        isCorrect = selected_choice.correct
        # If already answered this question, modify old answer, else create new
        if not hasAnswered.objects.filter(submitted_by=request.user, submitted_answer=question).exists():
            answer = hasAnswered(firstWasCorrect=isCorrect, wasCorrect=isCorrect, submitted_by=request.user, submitted_answer=question)
        else:
            answer = hasAnswered.objects.filter(submitted_by=request.user, submitted_answer=question).latest(
            'answer_attempt')
            answer.answer_attempt = answer.answer_attempt + 1
            answer.wasCorrect = isCorrect
        answer.save()

        user_hasChapter_current = hasChapter.objects.get(user=request.user, chapter=question.chapter_id)

        '''
        # Find new chapter skill rating. The rating is calculated by the formula  total correct answer / total answer
        prior_user_answers_to_current_chapter = hasAnswered.objects.filter(submitted_by=request.user,
                                                                           submitted_answer__chapter=question.chapter_id)
        answer_list = []

        for prior_answer in prior_user_answers_to_current_chapter:
            answer_list.append(prior_answer.wasCorrect)
        total_answers = len(answer_list)
        correct_answers = sum(answer_list)

        updated_skill_rating = float(correct_answers) / float(total_answers)
        '''

        weight = 0.4
        if isCorrect:
            adjustment = question.difficulty - user_hasChapter_current.skill_rating_chapter + 1

        else:
            adjustment = question.difficulty - user_hasChapter_current.skill_rating_chapter - 1
        # Adjusting with logistic function (squashing function)
        inverse_log_fun_current_rating = -math.log(1 / user_hasChapter_current.skill_rating_chapter - 1)

        if inverse_log_fun_current_rating < -2.5:
            inverse_log_fun_current_rating = -2.5
        elif inverse_log_fun_current_rating > 2.5:
            inverse_log_fun_current_rating = 2.5

        new_rating = 1 / (1 + math.exp(-(adjustment * weight + inverse_log_fun_current_rating)))

        user_hasChapter_current.skill_rating_chapter = new_rating
        user_hasChapter_current.save()

        # Get next question by selecting an unanswered question that match the current skill rating.
        # Prioritize chapters with lower skill rating.
        # The question that gives the lowest delta is the winner.

        chapter_priority = 1
        boundary_reset_chapter = 0.5
        search_new_question_attempt = 0
        while search_new_question_attempt < 2:
            delta = 1.0
            next_question_id = None
            next_question_difficulty = None
            next_chapter_difficulty = None
            for chapter in question_dict:
                # Check if the hasChapter relationship exists. If not exists, create one with default skill rating 0.5
                if not hasChapter.objects.filter(user=request.user, chapter=chapter).exists():
                    user_hasChapter = hasChapter(user=request.user, chapter=Chapter.objects.get(pk=chapter))
                    user_hasChapter.save()
                    # Get chapter skill rating
                skill_rating_chapter = hasChapter.objects.values_list('skill_rating_chapter', flat=True).get(
                    user=request.user, chapter=chapter)
                # Iterate over the chapter list and see if there is any unanswered question that gives us a lower delta.
                haschapter = hasChapter.objects.get(user=request.user, chapter=chapter)
                for question_to_be_checked in question_dict[chapter]:
                    new_delta = math.fabs(question_to_be_checked[1] - skill_rating_chapter) * (
                        skill_rating_chapter * chapter_priority)
                    if (not hasAnswered.objects.filter((Q(submitted_by=request.user) &
                                                        Q(submitted_answer=question_to_be_checked[
                                                            0])) &
                                                           (Q(answer_attempt=haschapter.chapter_attempt) | Q(wasCorrect=True))).exists()) and new_delta < delta:
                        delta = new_delta
                        next_question_id = question_to_be_checked[0]
                        next_question_difficulty = question_to_be_checked[1]
                        next_chapter_difficulty = skill_rating_chapter
                        next_haschapter = haschapter
            if next_question_id is None:

                if(not hasAnswered.objects.filter(Q(submitted_by=request.user) & Q(wasCorrect=False)).exists()):
                    ''' Code for resetting answers 
                    all_hasAnswer = hasAnswered.objects.filter(submitted_by=request.user,
                                                                           submitted_answer__chapter__part_of__name="Math")

                    #all_hasAnswer.update(wasCorrect=False)
                    '''
                    questions_chapter = {}
                    questions_chapter_answered = {}
                    questions_in_subject = {}
                    questions_in_subject_answered = {}
                    current_user = request.user
                    questions_by_user = hasAnswered.objects.all().filter(submitted_by=current_user, wasCorrect=True)

                    for i in Chapter.objects.all():
                        questions_chapter_answered[i] = 0
                        questions = Question.objects.filter(chapter=i)
                        questions_chapter[i] = len(questions)

                        for s in list(questions_by_user):
                            if s.submitted_answer.chapter == i:
                                questions_chapter_answered[i] += 1

                    for t in Subject.objects.all():
                        questions_in_subject[t] = 0
                        questions_in_subject_answered[t] = 0
                        for chapter in questions_chapter.keys():
                            if chapter.part_of == t:
                                questions_in_subject[t] += questions_chapter[chapter]

                        for chapter in questions_chapter_answered.keys():
                            if chapter.part_of == t:
                                questions_in_subject_answered[t] += questions_chapter_answered[chapter]

                    subject = []
                    subject_answered = []
                    count = []
                    for q in questions_in_subject.keys():
                        subject.append(q)
                        subject_answered.append(questions_in_subject_answered[q])
                        count.append(questions_in_subject[q])

                    zipped = zip(subject, subject_answered, count)
                    return render(request, 'questions/index.html', {'subject_list': zipped})
                else:
                    all_haschapters = hasChapter.objects.filter(user=request.user)
                    all_haschapters.update(chapter_attempt=F('chapter_attempt')+1)

            # Reset chapter questions if the users' skill rating is too low for the remaining questions (e.g failed on all the easy questions and only the hard questions remains in the question pool).
            elif abs(next_question_difficulty - next_chapter_difficulty) > boundary_reset_chapter and search_new_question_attempt<1:
                next_haschapter.chapter_attempt += 1
                next_haschapter.save()
                search_new_question_attempt += 1
            else:
                break

    except (KeyError, Choice.DoesNotExist):  # Redisplay the question voting form.

        haschapter = hasChapter.objects.get(user=request.user, chapter=Chapter.objects.get(pk=question.chapter_id))

        return render(request, 'questions/detail.html', {
            'question': question, 'subject_id': subject_id,
            'error_message': "You didn't select a choice.", 'haschapter': haschapter
        })
    else:
        return render(request, 'questions/results.html',
                      {'question': question, 'is_correct': selected_choice.is_correct,
                       'next_question': next_question_id, 'subject_id': subject_id})
