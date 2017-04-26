from django.conf.urls import url
from . import views
from personal import views as p_views

urlpatterns = [
    # ex: /questions/
    url(r'^$', views.index, name='index'),
    url(r'^(?P<subject_id>\d+)/$', views.index_questions, name='index_questions'),
    url(r'^(?P<subject_id>\d+)/(?P<question_id>[\w\-]+)/(?:/(?P<single_question>[a-zA-Z]+)/)?/$', views.detail, name='detail'),
    url(r'^(?P<subject_id>[0-9]+)/(?P<question_id>[0-9]+)/results/(?:/(?P<single_question>[a-zA-Z]+)/)?/$', views.answer, name='answer'),
    url(r"^logout/", p_views.logout_view, name='logout'),
    url(r"^search/$", views.search, name='search'),
    url(r"^profile/$", views.profile, name='profile'),
    url(r'^change_password', views.change_password, name='change_password'),
    url(r'^change_email/$', views.change_email, name='change_email'),
    url(r'^delete_user/$', views.del_user,name='delete_user'),
    url(r"^registration/$", views.reset, name='registration'),
    url(r"^feedback/$", views.feedback, name='feedback'),

]
