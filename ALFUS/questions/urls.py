from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /questions/
    url(r'^$', views.index, name='index'),
    url(r'^(?P<question_id>\d+)/$', views.detail, name='detail'),
    url(r'^(?P<question_id>[0-9]+)/results/$', views.answer, name='answer'),
    url(r"^login/$", views.logout_view, name='logout'),
]
