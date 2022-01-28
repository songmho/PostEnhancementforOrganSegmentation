__author__ = 'hanter'

from django.conf.urls import url
from . import views, apis

app_name = 'miaas'

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
    url(r'^api/load_lirads_img', apis.step1_save_lirads_imgs),
    url(r'^api/set_img_type', apis.set_img_type),
    url(r'^api/check_extension', apis.step1_check_extension),
    url(r'^api/load_medical_img', apis.step1_load_medical_img),
    url(r"^api/load_prv_img_data_from_local", apis.step1_load_prv_img_data_from_local),
    url(r'^api/convert_color_depth', apis.step1_convert_color_depth),
    url(r"^api/load_file_list", apis.load_file_list),
    url(r"^api/segment_liver", apis.segment_liver),
    url(r"^api/load_setCT_a", apis.load_setCT_a),
    url(r"^api/segment_tumor", apis.segment_tumor),


    url(r'^api/archive$', apis.handle_archive),

    url(r'^api/test$', apis.handle_test),
    url(r'^json_res/success$', views.json_response_success),

    url(r'^activate/(?P<user_id>[-._a-zA-Z0-9]+)/(?P<auth_code>[a-zA-Z0-9]+)$', views.activate_user, name='auth_email'),
    url(r'^change_password/(?P<user_id>[-._a-zA-Z0-9]+)/(?P<email>[a-zA-Z0-9]+)$', views.change_pwd, name='change_pwd'),
    url(r'^auth/(?P<user_id>[-._a-zA-Z0-9]+)/(?P<auth_code>[a-zA-Z0-9]+)$', views.auth_email_page, name='auth_email'),
    url(r'^auth/update/(?P<user_id>[-._a-z0-9]+)/(?P<auth_code>[a-zA-Z0-9]+)$', views.auth_change_email_page, name='auth_email_update'),

    url(r'^api/sign_in', apis.sign_in),
    url(r'^api/sign_up', apis.sign_up),
    url(r'^api/change_pwd', apis.change_pwd),
    url(r'^api/modify_general_info', apis.modify_general_info),
    url(r'^api/withdraw', apis.withdraw),
    url(r'^api/signout', apis.sign_out),
    url(r'^api/retrieve_user', apis.retrieve_user),
    url(r'^api/modify_user_info', apis.modify_user_info),
    url(r'^api/forgot_pwd', apis.forgot_pwd),
    url(r'^api/reset_pwd', apis.reset_pwd),
    url(r'^api/retrieve_image_info', apis.retrieve_image_info),

    url(r'^api/add_role', apis.add_role),
    url(r'^api/modify_role', apis.modify_role),
    url(r'^api/retrieve_role', apis.retrieve_role),
    url(r'^api/remove_role', apis.remove_role),
    url(r'^api/change_role_order', apis.change_role_order),

    url(r'^api/register_profile_image', apis.register_profile_image),
    url(r'^api/send_profile', apis.send_profile),
    url(r'^api/remove_profile', apis.remove_profile),

    url(r'^api/send_activate_mail', apis.send_activate_mail),
    url(r'^api/change_pwd', apis.forgot_pwd),
    url(r'^api/get_cur_user_info', apis.get_current_user_info),

    url(r'^view/sign_in', views.sign_in_page),
    url(r'^view/browse_image_detail/(?P<img_id>[a-zA-Z0-9]+)', views.browse_image_detail),
    url(r'^view/browse_image_info/(?P<img_id>[a-zA-Z0-9]+)', views.browse_image_info),
    url(r'^view/browse_profile', views.browse_profile),
    url(r'^view/update_profile', views.update_profile),
    url(r'^view/register_image', views.register_image),
    url(r'^view/browse_image', views.browse_image),
    url(r'^view/annotate_image', views.annotate_image),
    url(r'^view/remove_image', views.remove_image),
    url(r'^view/add_role', views.add_role),

    url(r'^view/brain_abnormality_diagnosis', views.brain_abnormality_diagnosis),
    url(r'^view/liver_abnormality_diagnosis', views.liver_abnormality_diagnosis),
    url(r'^view/lung_abnormality_diagnosis', views.lung_abnormality_diagnosis),
    url(r'^view/breast_abnormality_diagnosis', views.breast_abnormality_diagnosis),
    url(r'^view/stomach_abnormality_diagnosis', views.stomach_abnormality_diagnosis),

    url(r'^view/diagnose_abnormality_ml', views.diagnose_abnormality_ml),
    url(r'^view/diagnose_abnormality', views.diagnose_abnormality),
    url(r'^view/diagnose', views.diagnosis_detail),

    url(r'^view/annotate/(?P<img_id>[a-zA-Z0-9]+)$', views.annotate),
    url(r'^view/main', views.main),
    url(r'^view/lirads_step2', views.lirads_step2),
    url(r'^view/lirads_step1', views.lirads_step1),
    url(r'^view/lirads_step3', views.lirads_step3),
    url(r'^view/lirads_step4', views.lirads_step4),
    url(r'^view/lirads_step5', views.lirads_step5),
    url(r'^view/lirads_step6', views.lirads_step6),
    url(r'^view/lirads_step7', views.lirads_step7),
    url(r'^forgot_password', views.forgot_password),

    url(r'^api/retrieve_images', apis.retrieve_images),
    url(r'^api/remove_image', apis.remove_image),

    url(r'^form', views.Form),
    url(r'^upload', views.Upload),
    url(r'^api/upload', apis.upload_images),
    url(r'^api/send_images', apis.send_images),
    url(r'^api/send_dicom/(?P<img_id>[0-9]+)/(?P<phase>[\w ]+)/(?P<img_loc>[0-9]+)$', apis.send_dicom),
    url(r'^api/get_max_img_count', apis.get_max_img_count),
    url(r'^api/upload_txt', apis.upload_txt),
    url(r'^api/load_tumor_list', apis.load_tumor_list),
    url(r"^api/load_tumor_group_list_step6", apis.load_tumor_group_list_step6),
    url(r'^api/load_tumor_group_list', apis.load_tumor_group_list),
    url(r"^api/evaluate_img_feature", apis.evaluate_img_feature),
    url(r"^api/determin_tumor_type", apis.determin_tumor_type),
    url(r"^api/compute_lirads_feature", apis.compute_lirads_feature),
    url(r"^api/get_tumor_group_data", apis.get_tumor_group_data),
    url(r"^api/get_tumor_info", apis.get_tumor_info),
    url(r"^api/predict_stage", apis.predict_stage),
    url(r"^api/initialize_diagnosis_env", apis.initialize_diagnosis_env),
    url(r"^api/post-process_liver", apis.post_process_liver),
    url(r"^api/register_diagnosis_liver", apis.register_diagnosis),
    url(r"^api/retrieve_diagnosis_liver", apis.retrieve_diagnosis),
    # url(r'^api/register_test_item', apis.register_test_item),
    # url(r'^api/invite_user', apis.invite_user),
    # url(r'^api/check_invitation_code', apis.check_invitation_code),
    # url(r'^api/generate_invitation_code', apis.generate_invitation_code),

    url(r'^', views.page_not_found_view),
]

