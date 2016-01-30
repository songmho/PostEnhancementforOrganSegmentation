__author__ = 'hanter'

from django.conf.urls import url
from . import views

app_name = 'miaas'
urlpatterns = [
    url(r'^$', views.index_page, name='index'),
    url(r'^/$', views.index_page, name='index2'),
    # url(r'^$', views.IndexView.as_view(), name='index'),

    url(r'^signin$', views.signin_page, name='signin'),
    url(r'^signup$', views.signup_page, name='signup'),
    url(r'^profile$', views.profile_page, name='profile'),

    url(r'^archive$', views.archive_page, name='archive'),
    url(r'^archive/upload$', views.archive_upload_page, name='archive_upload'),
    url(r'^archive/detail/(?P<img_num>[0-9]+)$', views.medical_image_page, name='archive_detail'),

    url(r'^interpretation$', views.interpretation_page, name='interpretation'),
    url(r'^interpretation/(?P<interpret_num>[0-9]+)$', views.interpretation_detail_page, name='interpretation_detail'),
    url(r'^interpretation/request$', views.interpretation_request_page, name='interpretation_request'),
    url(r'^interpretation/candidate/(?P<interpret_num>[0-9]+)$', views.interpretation_candidate_page, name='interpretation_candidate'),

    url(r'^opinion/(?P<opinion_id>[0-9]+)/$', views.opinion, name='opinion'),
    url(r'^user/(?P<user_name>[ a-zA-Z_-]+)/$', views.user, name='user'),
    url(r'^template$', views.template, name='template'),
]