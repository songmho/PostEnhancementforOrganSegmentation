__author__ = 'hanter'

from django.conf.urls import url
from . import views, apis

urlpatterns = [
    # url(r'^$', views.main_page, name='main'),
    # url(r'^$', views.index_page, name='index'),
    # url(r'^sign_in$', views.render_page, {"page": "preview.html"}, name='index'),
    url(r'^$', views.index_page, name='index'),
    url(r'^main$', views.index_page, name='main'),
    # url(r'^main2$', views.main2_page, name='main2'),
    # url(r'^$', views.IndexView.as_view(), name='index'),

    url(r'^signin$', views.render_page, name='signin'),
    # url(r'^signin$', views.signin_page, name='signin'),
    url(r'^contact_us$', views.contact_us_page, name='contact_us'),
    url(r'^signup$', views.signup_page, name='signup'),
    url(r'^find$', views.find_page, name='find'),
    url(r'^profile$', views.profile_page, name='profile'),
    url(r'^physician$', views.physician_profile_page, name='physician_profile'),
    url(r'^account$', views.account_page, name='account'),

    url(r'^archive$', views.archive_page, name='archive'),
    # url(r'^archive/upload$', views.archive_upload_page, name='archive_upload'),
    url(r'^archive/upload$', views.ArchiveUploadView.as_view(), name='archive_upload'),
    # url(r'^archive/detail/(?P<image_id>[0-9]+)$', views.medical_image_page, name='archive_detail'),
    url(r'^archive/detail/(?P<image_id>[0-9]+)$', views.ArchiveDetailView.as_view(), name='archive_detail'),

    url(r'^interpretation$', views.patient_interpretation_list_page, name='interpretation'),
    url(r'^interpretation/request$', views.patient_request_list_page, name='interpretation_request_list'),
    url(r'^interpretation/request/detail/(?P<request_id>[0-9]+)$', views.patient_interpretation_request_detail_page, name='interpretation_request_detail'),
    url(r'^interpretation/(?P<intpr_id>[0-9]+)$', views.patient_interpretation_detail_page, name='interpretation_detail'),

    url(r'^interpretations$', views.physician_interpretation_page, name='physician_interpretation'),
    url(r'^interpretations/detail/(?P<intpr_id>[0-9]+)$', views.physician_interpretation_detail_page, name='physician_interpretation_detail'),
    url(r'^interpretations/response$', views.physician_interpretation_response_page, name='interpretation_response'),
    url(r'^interpretations/search$', views.physician_interpretation_search, name='interpretation_search'),
    url(r'^interpretations/search/detail/(?P<request_id>[0-9]+)$', views.physician_request_search_detail_page, name='interpretation_search_detail'),
    url(r'^interpretations/write/(?P<request_id>[0-9]+)$', views.physician_interpretation_write, name='interpretation_write'),

    # url(r'^opinion/(?P<opinion_id>[0-9]+)/$', views.opinion, name='opinion'),
    # url(r'^user/(?P<user_name>[ a-zA-Z_-]+)/$', views.user, name='user'),
    # url(r'^template$', views.template, name='template'),

    # url(r'^test$', views.test_page, name='test'),
    url(r'^test$', views.UploadViewTest.as_view(), name='test'),


    ### for APIs ###
    url(r'^api/sessions$', apis.handle_session_mgt),
    url(r'^api/intpr_session$', apis.handle_intpr_session_mgt),
    url(r'^api/user$', apis.handle_user_mgt),
    url(r'^api/patient_profile$', apis.handle_patient_profile_mgt),
    url(r'^api/physician_profile$', apis.handle_physician_profile_mgt),
    url(r'^api/medical_image$', apis.handle_medical_image_mgt),
    url(r'^api/interpretation$', apis.handle_interpretation_mgt),
    url(r'^api/analytics$', apis.handle_analytics_mgt),
    url(r'^api/payment$', apis.handle_payment_mgt),
    url(r'^api/get_upload_progress$', apis.handle_image_uploading_progress),
    url(r'^api/image_upload$', apis.handle_multple_image_upload),

    url(r'^api/archive$', apis.handle_archive),

    url(r'^api/test$', apis.handle_test),
    url(r'^json_res/success$', views.json_response_success),

    url(r'^activate/(?P<user_id>[-._a-zA-Z0-9]+)/(?P<auth_code>[a-zA-Z0-9]+)$', views.activate_user, name='auth_email'),
    url(r'^change_password/(?P<user_id>[-._a-zA-Z0-9]+)/(?P<email>[a-zA-Z0-9]+)$', views.change_pwd, name='change_pwd'),
    url(r'^auth/(?P<user_id>[-._a-zA-Z0-9]+)/(?P<auth_code>[a-zA-Z0-9]+)$', views.auth_email_page, name='auth_email'),
    url(r'^auth/update/(?P<user_id>[-._a-z0-9]+)/(?P<auth_code>[a-zA-Z0-9]+)$', views.auth_change_email_page, name='auth_email_update'),

    url(r'^api/sign_in', apis.sign_in),
    url(r'^api/sign_up', apis.sign_up),
    url(r'^api/withdrawal', apis.withdrawal),
    url(r'^api/signout', apis.sign_out),
    url(r'^api/retrieve_user', apis.retrieve_user),
    url(r'^api/modify_user_info', apis.modify_user_info),
    url(r'^api/forgot_pwd', apis.forgot_pwd),
    url(r'^api/reset_pwd', apis.reset_pwd),

    url(r'^api/send_activate_mail', apis.send_activate_mail),
    url(r'^api/change_pwd', apis.forgot_pwd),


    url(r'^view/sign_in', views.sign_in_page),
    url(r'^view/register_image', views.register_image),
    url(r'^view/browse_image', views.browse_image),
    url(r'^view/main', views.main),
    url(r'^forgot_password', views.forgot_password),

    url(r'^api/retrieve_images', apis.retrieve_images),

    url(r'^form', views.Form),
    url(r'^upload', views.Upload),
    url(r'^api/upload', apis.upload_images),
    url(r'^api/upload_txt', apis.upload_txt),
    # url(r'^api/register_test_item', apis.register_test_item),
    # url(r'^api/invite_user', apis.invite_user),
    # url(r'^api/check_invitation_code', apis.check_invitation_code),
    # url(r'^api/generate_invitation_code', apis.generate_invitation_code),

    url(r'^', views.page_not_found_view),
]
app_name = 'miaas'
