from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /questions/
    url(r'^$', views.IndexView.as_view(), name='index'),
    # ex: /questions/5/
    # the 'name' value as called by the {% url %} template tag
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    # ex: /polls/5/results/
    url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(),
        name='results'),
    # ex: /questions/5/vote/
    url(r'^(?P<question_id>[0-9]+)/answer/$', views.answer, name='answer'),
]