__author__ = 'hanter'

from django.conf.urls import url
from . import views

app_name = 'miaas'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    # url(r'^$', views.IndexView.as_view(), name='index'),


    url(r'^signin', views.signin, name='signin'),
    url(r'^signup', views.signup, name='signup'),
    url(r'^opinion/(?P<opinion_id>[0-9]+)/$', views.opinion, name='opinion'),
    url(r'^user/(?P<user_name>[ a-zA-Z_-]+)/$', views.user, name='user'),
    url(r'^template$', views.template, name='template'),
]