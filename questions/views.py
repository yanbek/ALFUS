from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect, render_to_response, HttpResponseRedirect
from django.http import Http404
from .models import Choice, Question, hasAnswered, hasChapter, Chapter, Subject
from collections import defaultdict
from django.db.models import Max
from django.utils import timezone
import math
from random import randint
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .forms import ChangeEmailForm
from django.db.models import Q, F
from itertools import chain
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse
from itertools import chain



def question_difficulty_number_to_text(number):
    if number >= 0.85:
        return("Very hard"), 'red'
    elif number >= 0.65:
        return("Hard"), 'orange'
    elif number >= 0.35:
        return("Medium"), 'yellow'
    elif number >= 0.15:
        return("Easy"), 'yellowgreen'
    else:
        return("Very Easy"), 'lime'

def number_to_grade(number):
    if number == 0.5 or number == 0:
        return("Not enough information to grade yet")
    elif number >= 0.89:
        return("A")
    elif number >= 0.77:
        return("B")
    elif number >= 0.65:
        return("C")
    elif number >= 0.53:
        return("D")
    elif number >= 0.41:
        return("E")
    else:
        return("F")


def get_grade_subject(request):
    skillrating_chapters = hasChapter.objects.filter(user=request.user)
    subject_grade = {}

    for t in list(Subject.objects.all()):
        count = 0
        temp = 0
        for q in list(skillrating_chapters):
            if q.chapter.part_of == t:
                temp += q.skill_rating_chapter
                count += 1

            print("count")
        print("---------------")
        if count == 0:
            count = 1
        subject_grade[t] = number_to_grade(temp / count)
        print(subject_grade)
    return(subject_grade)


@login_required(login_url="/login/")
def feedback(request):

    answer = hasAnswered.objects.filter(submitted_by=request.user, submitted_answer=request.POST.get('question'))
    answer.update(firstWasCorrect=False)

    return render(request, 'questions/results.html',
                  {'question': request.POST.get('question'), 'is_correct': request.POST.get('is_correct'),
                   'next_question': request.POST.get('next_question'), 'subject_id': request.POST.get('subject_id'), 'single_question': request.POST.get('single_question'), 'feedback_btn_status': 'btn btn-primary', 'feedback_btn': 'disabled'})

@login_required(login_url="/login/")
def reset(request):
    all_hasAnswer = hasAnswered.objects.filter(submitted_by=request.user)
    all_hasAnswer.update(wasCorrect=False)

    all_skill = hasChapter.objects.filter(user=request.user)
    all_skill.update(skill_rating_chapter=0.5)
    return redirect("/questions/profile")


@login_required(login_url="/login/")
def change_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST,instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('/questions/profile')
        else:
            messages.error(request, "Please correct the error above.")
            return redirect('/questions/change_email')
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
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect('/questions/profile')
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'questions/change_password.html', {"form": form})


@login_required(login_url="/login/")
def profile(request):
    temp = get_grade_subject(request)
    subject = []
    grades_letter = []

    for i in temp.keys():
        subject.append(i)
        grades_letter.append(temp[i])


    zipped = zip(subject, grades_letter)

    return render(request, 'questions/profile.html', {"skills": zipped})

@login_required(login_url="/login/")
def search(request):
    try:
        all_topics = Question.objects.all()
        q = request.GET['q']
        topics = Question.objects.filter(topic_text__icontains=q)
        return render_to_response('questions/search.html', {'all_topics': all_topics,'topics': topics, 'q': q})
    except KeyError:
        return render_to_response('questions/search.html')


@login_required(login_url="/login/")
def index(request):
    zipped = get_chapters(request)
    return render(request, 'questions/index.html', {'subject_list': zipped})


@login_required(login_url="/login/")
def index_questions(request, subject_id):
    question_list = Question.objects.filter(chapter__part_of_id=subject_id)
    subject_name = Subject.objects.get(pk=subject_id)

    question_dict = defaultdict(list)
    for question in question_list:
        question_dict[question.chapter_id].append((question.id, question.difficulty))
    request.session['question_dict'] = question_dict

    next_question_id = get_next_question(request, subject_id)

    #Chapter info
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

    chapter = []
    percent = []
    grades = []

    for q in questions_in_subject.keys():
        qSet = hasChapter.objects.filter(chapter=q, user=current_user)
        if qSet:
            grades.append(number_to_grade(qSet[0].skill_rating_chapter))

        percent.append(round(float(questions_in_subject_answered[q])/float(questions_in_subject[q])*100))

        chapter.append(q)
    zipped = zip(chapter, percent, grades)
    subject_grade = get_grade_subject(request)[subject_name]

    return render(request, 'questions/index_questions.html',
                {'next_question_id': next_question_id, 'subject_id': subject_id, 'subject_name': subject_name, "chapters": zipped, 'subject_grade': subject_grade})


@login_required(login_url="/login/")
def detail(request, question_id, subject_id, single_question):
    try:
        if not question_id == 'None':
            question = get_object_or_404(Question, pk=question_id)
             # Check if the hasChapter relationship exists. If not exists, create one.
            if not hasChapter.objects.filter(user=request.user, chapter=question.chapter_id).exists():
                haschapter = hasChapter(user=request.user, chapter=Chapter.objects.get(pk=question.chapter_id))
                haschapter.save()
            else:
                haschapter = hasChapter.objects.get(user=request.user, chapter=question.chapter_id)
        else:
            return render(request, 'questions/results.html',
                          {'next_question': None,'single_question': False })
    except Question.DoesNotExist:
        raise Http404("Question doesn't exist")

    #Skill level to grade (chapter)
    grade = ""
    skill_r = haschapter.skill_rating_chapter

    grade = number_to_grade(skill_r)

    #Skill level to grade (subject)
    subject_grade = get_grade_subject(request)[haschapter.chapter.part_of]
    question_difficulty, question_difficulty_color= question_difficulty_number_to_text(question.difficulty)

    return render(request, 'questions/detail.html',
                  {'question': question, 'haschapter': haschapter, 'subject_id': subject_id, 'single_question': single_question,
                  "grade": grade, "subject_grade": subject_grade, 'question_difficulty': question_difficulty, 'question_difficulty_color' : question_difficulty_color})


@login_required(login_url="/login/")
def answer(request, question_id, subject_id, single_question):
    question = get_object_or_404(Question, pk=question_id)
    try:
        if (single_question == 'S'):
            single_question = True
        else:
            single_question = False

        # Save answer
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
        isCorrect = selected_choice.correct
        # If already answered this question, modify old answer, else create new
        if not hasAnswered.objects.filter(submitted_by=request.user, submitted_answer=question).exists():
            answer = hasAnswered(firstWasCorrect=isCorrect, wasCorrect=isCorrect, submitted_by=request.user, submitted_answer=question, answer_attempt = 1)
        else:
            answer = hasAnswered.objects.get(submitted_by=request.user, submitted_answer=question)
            haschapter = hasChapter.objects.get(user=request.user, chapter=question.chapter)
            if(answer.answer_attempt==haschapter.chapter_attempt):
                error_iscorrect = "error " + str(isCorrect)
                return render(request, 'questions/results.html',
                              {'question': question, 'subject_id': subject_id, 'single_question': single_question, 'is_correct': error_iscorrect, 'feedback_btn_status': 'btn btn-secondary', 'feedback_btn': ''})
            else:
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

        next_question_id = get_next_question(request, subject_id)


    except (Choice.DoesNotExist, KeyError) as ex:  # Redisplay the question voting form.
        haschapter = hasChapter.objects.get(user=request.user, chapter=Chapter.objects.get(pk=question.chapter_id))

        question_difficulty, question_difficulty_color = question_difficulty_number_to_text(question.difficulty)

        return render(request, 'questions/detail.html', {
            'question': question, 'subject_id': subject_id,
            'error_message': "You didn't select an answer.", 'haschapter': haschapter, 'single_question': single_question, 'question_difficulty': question_difficulty, 'question_difficulty_color' : question_difficulty_color
        })
    else:
        return render(request, 'questions/results.html',
                          {'question': question, 'is_correct': selected_choice.correct,
                           'next_question': next_question_id, 'subject_id': subject_id, 'single_question': single_question, 'feedback_btn_status': 'btn btn-secondary', 'feedback_btn': ''})



@login_required(login_url="/login/")
def get_next_question(request, subject_id):
    # Get next question by selecting an unanswered question that match the current skill rating.
    # Prioritize chapters with lower skill rating.
    # The question that gives the lowest delta is the winner.
    question_dict = request.session['question_dict']
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
                                                       (Q(answer_attempt=haschapter.chapter_attempt) | Q(
                                                           wasCorrect=True))).exists()) and new_delta < delta:
                    delta = new_delta
                    next_question_id = question_to_be_checked[0]
                    next_question_difficulty = question_to_be_checked[1]
                    next_chapter_difficulty = skill_rating_chapter
                    next_haschapter = haschapter
        if next_question_id is None:

            if (not hasAnswered.objects.filter(Q(submitted_by=request.user) & Q(wasCorrect=False) & Q(submitted_answer__chapter__part_of=subject_id)).exists()):
                #zipped = get_chapters(request)
                #return render(request, 'questions/index.html', {'subject_list': zipped})
                return next_question_id
            else:
                all_haschapters = hasChapter.objects.filter(user=request.user)
                all_haschapters.update(chapter_attempt=F('chapter_attempt') + 1)
        # Reset chapter questions if the users' skill rating is too low for the remaining questions (e.g failed on all the easy questions and only the hard questions remains in the question pool).
        elif abs(
                        next_question_difficulty - next_chapter_difficulty) > boundary_reset_chapter and search_new_question_attempt < 1:
            next_haschapter.chapter_attempt += 1
            next_haschapter.save()
            search_new_question_attempt += 1
        else:
            break
    return next_question_id



@login_required(login_url="/login/")
def get_chapters(request):
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
    return zip(subject, subject_answered, count)

@login_required(login_url="/login/")
def reset(request):
    # Reset all questions
    all_hasAnswer = hasAnswered.objects.filter(submitted_by=request.user)
    all_hasChapter = hasChapter.objects.filter(user=request.user)
    all_hasAnswer.update(wasCorrect=False)
    all_hasChapter.update(chapter_attempt=1)
    all_hasChapter.update(skill_rating_chapter=0.5)
    all_hasAnswer.update(answer_attempt=1)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

