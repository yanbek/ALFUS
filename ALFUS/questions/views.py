from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.utils import timezone
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404

from .forms import AnswerForm
from .models import Choice, Question



def index(request):
    template_name = 'questions/index.html'


    question_list = Question.objects.filter(
                    pub_date__lte=timezone.now()
                    ).order_by('-pub_date')[:5]

    context = RequestContext(request, {'question_list' : question_list})
    return HttpResponse(template_name.render(context))


def detail(request, question_id):
    try:
        question = Question.objects.get(pk = question_id)
    except Question.DoesNotExist:
        raise Http404("Question doesn't exist")
    return render(request, 'questions/detail.html', {'question': question})



    # def get_queryset(self):
    #     """
    #     Excludes any questions that aren't published yet.
    #     """
    #     return Question.objects.filter(pub_date__lte=timezone.now())
    #

def result(request, choice, question_id):
    question = get_object_or_404(Question, pk = question_id)
    return render(request, 'questions/results.html', {'question': question, 'choice' : choice})


def answer(request, question_id):
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

        # form = AnswerForm(question, selected_choice)

        # See  Avoiding race conditions using F()
        # https://docs.djangoproject.com/en/1.9/ref/models/expressions/#avoiding-race-conditions-using-f
        ##selected_choice.correct += 1
        ##selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('questions:results', args=(
             selected_choice,question_id
        )))


