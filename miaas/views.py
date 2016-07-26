from miaas import sample_contexts
from miaas.utils.utils import timestamp_to_date_string, get_interpretation_status
from django.http import Http404

__author__ = 'hanter'

from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from django.views.generic.edit import FormView
from .forms import UploadForm

from miaas import sample_contexts as sctx
from miaas import cloud_db, constants, cloud_db_copy, email_auth

from image_manager import ImageManager, ImageRetriever
import logging, json, time, copy
from pprint import pprint

# get db data -> 404 template, urls in tutorial #3: https://docs.djangoproject.com/en/1.9/intro/tutorial03/
# form, db class -> tutorial #4

#
# class IndexView(generic.ListView):
#     template_name = 'miaas/test.html'
#     context_object_name = 'latest_question_list'
#
#     def get_queryset(self):
#         """Return the last five published questions."""
#         return ['fdsdf', 'asdfew', 'earsdfc', '2dfa', 'asdq']

logging.basicConfig(
    format="[%(name)s][%(asctime)s] %(message)s",
    handlers=[logging.StreamHandler()],
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main2_page(request):
    context = _get_session_context(request)
    return render(request, 'miaas/main2.html', context)


def main_page(request):
    context = _get_session_context(request)
    # context = {
    #     'session': sctx.default_session,
    # }
    return render(request, 'miaas/main.html', context)


def index_page(request):
    context = _get_session_context(request)
    # context = {
    #     'session': sctx.default_session,
    # }
    return render(request, 'miaas/index.html', context)


# login reference: https://www.fir3net.com/Web-Development/Django/django.html
def signin_page(request):
    context = _get_session_context(request)
    return render(request, 'miaas/signin.html', context)

def auth_email_page(request, user_id, auth_code):
    context = {
        'user_id': user_id,
        'auth_code': auth_code
    }
    verified = email_auth.verify_auth_mail(user_id, auth_code)
    context['authenticated'] = verified

    return render(request, 'miaas/verify_auth_mail.html', context)

def auth_change_email_page(request, user_id, auth_code):
    context = {
        'user_id': user_id,
        'auth_code': auth_code
    }
    updated = email_auth.verify_and_update_auth_mail(user_id, auth_code)
    context['authenticated'] = updated

    return render(request, 'miaas/verify_change_mail.html', context)


def contact_us_page(request):
    return render(request, 'miaas/contact_us.html', None)


def signup_page(request):
    return render(request, 'miaas/signup.html', None)


def find_page(request):
    return render(request, 'miaas/find.html', None)


def account_page(request):
    db = cloud_db.DbManager()

    context = _get_session_context(request, pw_contains=True)
    return render(request, 'miaas/account.html', context)


def profile_page(request):
    context = _get_session_context(request)
    # logger.info(context)
    return render(request, 'miaas/patient_profile_v2.html', context)


def archive_upload_page(request):
    context = _get_session_context(request)
    return render(request, 'miaas/patient_medical_image_upload.html', context)


def physician_profile_page(request):
    context = _get_session_context(request)
    return render(request, 'miaas/physician_profile.html', context)


def _get_session_context(request, pw_contains=False):
    context = {}
    if 'user' in request.session.keys():
        context['user_session'] = copy.deepcopy(request.session['user'])
        if context.get('user_session') and not pw_contains:
            context['user_session'].pop('password', None)

    if 'intpr_session' in request.session.keys():
        context['intpr_session'] = request.session['intpr_session']

    # session expiry for 1 hour
    request.session.set_expiry(60*60)

    return context


####################
#  Details Pages #
####################

# patient
# def medical_image_page(request, image_id):
#     context = _get_session_context(request)
#     if request.GET.get('lastPage'):
#         context['lastPage'] = request.GET['lastPage']
#
#     if not image_id or int(image_id) < 0:
#         return archive_page(request)
#     else:
#         try:
#             db = cloud_db_copy.DbManager()
#             image, = db.retrieve_detail(db.PATIENT_IMAGE_DETAIL, image_id)
#             intpr_list = db.retrieve_list(db.IMAGE_INTPR_LIST, image_id)
#             if image['user_id'] != request.session.get('user'):
#                 return render(request, 'miaas/404.html', context="")
#             context['image'] = image
#             context['intpr_list'] = intpr_list
#         except Exception:
#             return render(request, 'miaas/404.html', context="")
#
#             # if result.get('image') and isinstance(result.get('intpr'), list):
#             #     context['image'] = result['image']
#             #     context['intpr_list'] = result['intpr']
#             # request.session['medical_image'][str(result['image']['image_id'])] = result['image']
#             # logger.info('image page(%s): %s' % (result['image']['image_id'], request.session['medical_image']))
#             # request.session['curr_image'] = result['image']
#     return render(request, 'miaas/patient_medical_image.html', context)


def patient_interpretation_detail_page(request, intpr_id):
    context = _get_session_context(request)
    if request.GET.get('lastPage'):
        context['lastPage'] = request.GET['lastPage']

    if not intpr_id or int(intpr_id) < 0:
        return patient_interpretation_list_page(request)
    if request.session.get('user'):
        try:
            db = cloud_db_copy.DbManager()
            intpr, physician, request_detail, image = db.retrieve_detail(db.PATIENT_INTPR_DETAIL, intpr_id)
            if image['patient_id'] != request.session['user']['user_id']:
                return render(request, 'miaas/404.html', context="")
            context['intpr'] = intpr
            context['physician'] = physician
            context['request_detail'] = request_detail
            context['image'] = image
        except Exception as e:
            # print e
            return render(request, 'miaas/404.html', context="")
    logger.info('interpretation_detail_page get: %s' % request.GET)
    return render(request, 'miaas/patient_interpretation_detail.html', context)


def patient_interpretation_request_detail_page(request, request_id):
    context = _get_session_context(request)
    if request.GET.get('lastPage'):
        context['lastPage'] = request.GET['lastPage']

    if not request_id or int(request_id) < 0:
        return patient_request_list_page(request)
    if request.session.get('user'):
        try:
            db = cloud_db_copy.DbManager()
            cdb = None
            request_detail, image = db.retrieve_detail(db.PATIENT_REQUEST_DETAIL, request_id)
            if image['patient_id'] != request.session['user']['user_id']:
                return patient_request_list_page(request)
            if request_detail['status'] == 0:
                cdb = cloud_db.DbManager()
                intpr_id = cdb.retrieve_interpretation_by_request_id(request_detail['request_id'])
                if intpr_id:
                    context['redirection'] = True
                    context['intpr_id'] = intpr_id
                else:
                    raise Exception()
            else:
                responses = db.retrieve_list(db.REQUEST_RESPONSE_LIST, request_detail['request_id'])
                context['image'] = image
                context['request_detail'] = request_detail
                context['responses'] = responses
        except Exception:
            return render(request, 'miaas/404.html', context="")
        finally:
            db.close()
            if cdb: cdb.close()
    logger.info('interpretation_request_detail_page get: %s' % request.GET)
    return render(request, 'miaas/patient_interpretation_request_detail.html', context)


# physician
def physician_request_search_detail_page(request, request_id):
    context = _get_session_context(request)
    if request.GET.get('lastPage'):
        context['lastPage'] = request.GET['lastPage']

    if not request_id or int(request_id) < 0:
        return physician_interpretation_search(request)
    if request.session.get('user'):
        try:
            db = cloud_db_copy.DbManager()
            request_detail, patient, image, intpr_temp = db.retrieve_detail(db.PHYSICIAN_REQUEST_DETAIL, request_id)
            if request_detail['status'] == 0:
                raise Exception()
            context['request_detail'] = request_detail
            context['patient'] = patient
            context['image'] = image
            # pprint(context)
        except Exception:
            return render(request, 'miaas/404.html', context="")

    logger.info('physician_request_search_detail_page get: %s' % request.GET)
    return render(request, 'miaas/physician_interpretation_search_detail.html', context)


def physician_interpretation_write(request, request_id):
    context = _get_session_context(request)
    if request.GET.get('lastPage'):
        context['lastPage'] = request.GET['lastPage']

    if not request_id or int(request_id) < 0:
        return physician_interpretation_response_page(request)
    if request.session.get('user'):
        try:
            db = cloud_db_copy.DbManager()
            cdb = None
            request_detail, patient, image, intpr_temp = db.retrieve_detail(db.PHYSICIAN_REQUEST_DETAIL, request_id)
            if request_detail['status'] == 0:
                cdb = cloud_db.DbManager()
                intpr_id = cdb.retrieve_interpretation_by_request_id(request_detail['request_id'])
                if intpr_id:
                    context['redirection'] = True
                    context['intpr_id'] = intpr_id
                else:
                    raise Exception()
            else:
                context['request_detail'] = request_detail
                context['patient'] = patient
                context['image'] = image
                context['intpr_temp'] = intpr_temp
        except Exception:
            return render(request, 'miaas/404.html', context="")
        finally:
            db.close()
            if cdb: cdb.close()
    logger.info('interpretation_request_detail_page get: %s' % request.GET)
    return render(request, 'miaas/physician_interpretation_write.html', context)


def physician_interpretation_detail_page(request, intpr_id):
    context = _get_session_context(request)
    if request.GET.get('lastPage'):
        context['lastPage'] = request.GET['lastPage']

    if not intpr_id or int(intpr_id) < 0:
        return physician_interpretation_page(request)
    if request.session.get('user'):
        try:
            db = cloud_db_copy.DbManager()
            intpr, patient, request_detail, image = db.retrieve_detail(db.PHYSICIAN_INTPR_DETAIL, intpr_id)
            context['intpr'] = intpr
            context['patient'] = patient
            context['request_detail'] = request_detail
            context['image'] = image
        except Exception:
            return render(request, 'miaas/404.html', context="")
    # logger.info('physician_interpretation_detail_page get: %s' % request.GET)
    return render(request, 'miaas/physician_interpretation_detail.html', context)


####################
#  List Form Pages #
####################

# patient
def patient_interpretation_list_page(request):
    context = _get_session_context(request)
    if request.GET.get('page'):
        context['page'] = request.GET['page']

    dt_list = []
    if request.session.get('user'):
        try:
            # Retrieve lists.
            db = cloud_db_copy.DbManager()
            results = db.retrieve_list(db.PATIENT_INTPR_LIST, request.session['user']['user_id'])
            for r in results:
                temp = []
                temp.append(r['request_date'])
                temp.append(r['interpret_date'])
                temp.append(r['request_subject'])
                temp.append(r['image_subject'])
                temp.append(r['image_type'])
                temp.append(r['level'])
                temp.append(r['intpr_id'])
                if len(temp):
                    dt_list.append(temp)
            # Render the page
            if len(dt_list):
                context['dt_list'] = json.dumps(dt_list)
        except Exception:
            return render(request, 'miaas/404.html', context="")
    logger.info('interpret get: %s' % request.GET)
    return render(request, 'miaas/patient_interpretation_list.html', context)


def patient_request_list_page(request):
    context = _get_session_context(request)
    if request.GET.get('page'):
        context['page'] = request.GET['page']

    dt_list = []
    if request.session.get('user'):
        try:
            # Retrieve lists.
            db = cloud_db_copy.DbManager()
            results = db.retrieve_list(db.PATIENT_REQUEST_LIST, request.session['user']['user_id'])
            for r in results:
                temp = []
                temp.append(r['request_date'])
                temp.append(r['request_subject'])
                temp.append(r['image_subject'])
                temp.append(r['image_type'])
                temp.append(r['level'])
                temp.append(get_interpretation_status(r['status']))
                temp.append(r['request_id'])
                if len(temp):
                    dt_list.append(temp)

            # Render the page
            if len(dt_list):
                context['dt_list'] = json.dumps(dt_list)
        except Exception:
            return render(request, 'miaas/404.html', context="")

    logger.info('patient_request_list_page get: %s' % request.GET)
    return render(request, 'miaas/patient_interpretation_request_list.html', context)


def archive_page(request):
    context = _get_session_context(request)
    if request.GET.get('page'):
        context['page'] = request.GET['page']

    dt_list = []
    if request.session.get('user'):
        try:
            # Retrieve lists.
            db = cloud_db_copy.DbManager()
            results = db.retrieve_list(db.PATIENT_IMAGE_LIST, request.session['user']['user_id'])
            for r in results:
                temp = []
                temp.append(r['uploaded_date'])
                temp.append(r['image_subject'])
                temp.append(r['image_type'])
                temp.append(r['recorded_date'])
                temp.append(r['intpr_num'])
                temp.append(r['image_id'])
                if len(temp):
                    dt_list.append(temp)

            # Render the page
            if len(dt_list):
                context['dt_list'] = json.dumps(dt_list)
        except Exception:
            return render(request, 'miaas/404.html', context="")

    logger.info('archive get: %s' % request.GET)
    return render(request, 'miaas/patient_archive.html', context)


# physician
def physician_interpretation_search(request):
    context = _get_session_context(request)
    if request.GET.get('page'):
        context['page'] = request.GET['page']

    dt_list = []
    if request.session.get('user'):
        try:
            # Retrieve lists.
            db = cloud_db_copy.DbManager()
            results = db.retrieve_list(db.PHYSICIAN_SEARCH_REQUEST_LIST, request.session['user']['user_id'])
            for r in results:
                temp = []
                temp.append(r['request_date'])
                temp.append(r['patient_id'])
                temp.append(r['request_subject'])
                temp.append(r['image_subject'])
                temp.append(r['image_type'])
                temp.append(r['level'])
                temp.append(r['request_id'])
                if len(temp):
                    dt_list.append(temp)
        except Exception:
            return render(request, 'miaas/404.html', context="")

        # Render the page
        if len(dt_list):
            context['dt_list'] = json.dumps(dt_list)
    logger.info('physician_interpretation_search get: %s' % request.GET)
    return render(request, 'miaas/physician_interpretation_search.html', context)


def physician_interpretation_response_page(request):
    context = _get_session_context(request)
    if request.GET.get('page'):
        context['page'] = request.GET['page']

    dt_list = []
    if request.session.get('user'):
        # Retrieve lists.
        try:
            db = cloud_db_copy.DbManager()
            results = db.retrieve_list(db.PHYSICIAN_RESPONSE_LIST, request.session['user']['user_id'])
            for r in results:
                temp = []
                temp.append(r['request_date'])
                temp.append(r['response_date'])
                temp.append(r['patient_id'])
                temp.append(r['request_subject'])
                temp.append(r['image_subject'])
                temp.append(r['image_type'])
                temp.append(r['level'])
                temp.append(get_interpretation_status(r['status']))
                temp.append(r['request_id'])
                if len(temp):
                    dt_list.append(temp)
        except Exception:
            return render(request, 'miaas/404.html', context="")

        # Render the page
        if len(dt_list):
            context['dt_list'] = json.dumps(dt_list)
    logger.info('interpretation_request_list_page get: %s' % request.GET)
    return render(request, 'miaas/physician_interpretation_response_list.html', context)


def physician_interpretation_page(request):
    context = _get_session_context(request)
    if request.GET.get('page'):
        context['page'] = request.GET['page']

    dt_list = []
    if request.session.get('user'):
        try:
            # Retrieve lists.
            db = cloud_db_copy.DbManager()
            results = db.retrieve_list(db.PHYSICIAN_INTPR_LIST, request.session['user']['user_id'])
            for r in results:
                temp = []
                temp.append(r['request_date'])
                temp.append(r['interpret_date'])
                temp.append(r['patient_id'])
                temp.append(r['image_subject'])
                temp.append(r['image_type'])
                temp.append(r['level'])
                temp.append(r['intpr_id'])
                if len(temp):
                    dt_list.append(temp)
        except Exception:
            return render(request, 'miaas/404.html', context="")
        # Render the page
        if len(dt_list):
            context['dt_list'] = json.dumps(dt_list)
    logger.info('physician_interpretation_page get: %s' % request.GET)
    return render(request, 'miaas/physician_interpretation_list.html', context)


def page_not_found_view(request):
    return render(request, 'miaas/404.html', context="")


class ArchiveUploadView(FormView):
    template_name = 'miaas/patient_medical_image_upload.html'
    form_class = UploadForm
    success_url = '/json_res/success'

    def get_context_data(self, **kwargs):
        context = _get_session_context(self.request)
        return context

    def form_valid(self, form):
        try:
            image_files = form.cleaned_data['attachments']

            if (len(image_files) <= 0 or 'image_info' not in self.request.POST):
                raise Exception('Invalid Parameters.')

            action = self.request.POST['action']
            image_info = json.loads(self.request.POST['image_info'])

            prev_timestamp = 0
            if image_info.get('timestamp'):
                prev_timestamp = image_info['timestamp']
            image_info['timestamp'] = int(round(time.time() * 1000))

            # if self.request.session['user']['user_id'] != image_info['user_id']:
            #     raise Exception('logged in user is not match with request user')
            if action != 'upload' and action != 'update':
                raise Exception('Invalid Parameters.')

            uploaded_path = None
            im = ImageManager(image_files, image_info)
            uploaded_path = im.upload_file()
            # uploaded_path = uploaded_path.encode('UTF-8')

            db = cloud_db.DbManager()

            if action == 'upload':
                try:
                    image_info['image_dir'] = uploaded_path
                    db.add_medical_image(image_info)
                except Exception as e:
                    if uploaded_path:
                        ImageManager.delete_file(uploaded_path)
                        im.delete_temp_file()
                    raise e
                # if not self.request.session.get('image_cnt'):
                #     self.request.session['image_cnt'] += 1
                return JsonResponse(dict(constants.CODE_SUCCESS))
            elif action == 'update':
                prev_path = image_info['image_dir']
                try:
                    image_info['image_dir'] = uploaded_path
                    db.update_medical_image_dir(image_info)
                except Exception as e:
                    image_info['timestamp'] = prev_timestamp
                    image_info['image_dir'] = prev_path
                    # db.update_medical_image_dir(image_info)
                    ImageManager.delete_file(uploaded_path)
                    raise e

                logger.info('remove old file: %s', prev_path)
                ImageManager.delete_file(prev_path)
                return JsonResponse(dict(constants.CODE_SUCCESS, **{'new_dir': image_info['image_dir']}))

        except Exception as e:
            logger.exception(e)
            return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': str(e)}))
        return JsonResponse(dict(constants.CODE_FAILURE, **{'msg': 'Unknown error.'}))
        # return super(UploadView, self).form_valid(form)


class ArchiveDetailView(ArchiveUploadView):
    template_name = 'miaas/patient_medical_image.html'

    def get_context_data(self, **kwargs):
        context = _get_session_context(self.request)
        if self.request.GET.get('lastPage'):
            context['lastPage'] = self.request.GET['lastPage']
        image_id = self.kwargs['image_id']

        try:
            if not image_id or int(image_id) < 0:
                context['image'] = None
            else:
                db = cloud_db.DbManager()
                result = db.retrieve_image_and_intpr(image_id)
                # logger.info(result)

                if result.get('image') and isinstance(result.get('intpr'), list):
                    context['image'] = result['image']
                    context['intpr_list'] = result['intpr']
                    pprint (result['intpr'])
        except:
            context['image'] = None
        return context


# def opinion(request, opinion_id):
#     return HttpResponse("Hello, opinion %s." % opinion_id)
#
#
# def user(request, user_name):
#     return HttpResponse("Hello, user %s." % user_name)
#
#
# def template(request):
#     return render(request, 'miaas/template.html', None)

def test_page(request):
    return render(request, 'miaas/test.html', None)


def json_response_success(request):
    return render(request, 'miaas/json_code_success.html', None)


class UploadViewTest(FormView):
    template_name = 'miaas/test.html'
    form_class = UploadForm
    success_url = '/json_res/success'

    def form_valid(self, form):
        files = form.cleaned_data['attachments']
        for file in form.cleaned_data['attachments']:
            logger.info(file)

            filepath = '%s/%s' % ('medical_images/temp', file._name)
            fp = open(filepath, 'wb')
            for chunk in file.chunks():
                fp.write(chunk)
            fp.close()

        return super(UploadViewTest, self).form_valid(form)
