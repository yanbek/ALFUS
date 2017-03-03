from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^contact/$', views.contact, name='contact'),
    # url(r'^user/(\w+)/$', views.profile, name="profile"),
    url(r"^login/$", views.login_view, name="login")
]
