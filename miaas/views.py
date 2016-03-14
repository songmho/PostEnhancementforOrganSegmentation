from miaas import sample_contexts

__author__ = 'hanter'

from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.http import *
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from miaas import sample_contexts as sctx
from miaas import cloud_db, constants
import logging, json, time

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


def signup_page(request):
    return render(request, 'miaas/signup.html', None)


def find_page(request):
    return render(request, 'miaas/find.html', None)


def account_page(request):
    context = _get_session_context(request)
    return render(request, 'miaas/account.html', context)


def profile_page(request):
    context = _get_session_context(request)
    # logger.info(context)
    return render(request, 'miaas/patient_profile.html', context)


def archive_page(request):
    context = _get_session_context(request)
    if request.session.get('user'):
        logger.info('archive_page call db')
        now_page = request.GET.get('page')
        if not now_page or not request.session.get('images'):
            # Retrieve lists.
            db = cloud_db.DbManager()
            images = db.retrieve_medical_image(user_id=request.session['user']['user_id'])
            request.session['images'] = images
        else:
            images = request.session['images']

        image_cnt = len(images)
        if image_cnt <= 0:
            return render(request, 'miaas/archive.html', context)
        archive = {}
        request.session['image_cnt'] = image_cnt
        archive['image_cnt'] = image_cnt
        # Configure number of pages
        max_page = image_cnt // constants.CNT_CONTENTS_IN_PAGE
        if image_cnt % constants.CNT_CONTENTS_IN_PAGE > 0:
            max_page += 1
        if not now_page or now_page > max_page:
            now_page = 1
        archive['now_page'] = now_page
        archive['max_page'] = max_page
        logger.info('now_page=%s, max_page=%s' % (now_page, max_page))

        start_page = now_page - 4
        if start_page < 1: start_page = 1
        end_page = start_page + 9
        if end_page > max_page: end_page = max_page
        archive['start_page'] = start_page
        archive['end_page'] = end_page
        logger.info('start_page=%s, end_page=%s' % (start_page, max_page))

        # Render page
        offset = (now_page-1)*constants.CNT_CONTENTS_IN_PAGE
        archive['images'] = images[offset:offset+constants.CNT_CONTENTS_IN_PAGE]
        context['archive'] = archive

    logger.info('archive get: %s' % request.GET)
    # return render(request, 'miaas/archive.html', sctx.archive_context)
    return render(request, 'miaas/archive.html', context)


def archive_upload_page(request):
    context = _get_session_context(request)
    # return render(request, 'miaas/medical_image_upload.html', sctx.default_context)
    return render(request, 'miaas/medical_image_upload.html', context)


def medical_image_page(request, image_id):
    context = _get_session_context(request)
    # return render(request, 'miaas/medical_image.html', sctx.default_context)

    if not image_id or int(image_id) < 0:
        return archive_page(request)
    else:
        db = cloud_db.DbManager()
        result = db.retrieve_image_and_intpr(image_id)

        if result.get('image') and isinstance(result.get('intpr'), list):
            context['image'] = result['image']
            context['intpr_list'] = result['intpr']
            request.session['curr_image'] = result['image']

    return render(request, 'miaas/medical_image.html', context)


def interpretation_request_page(request):
    context = _get_session_context(request)
    # image_id = request.GET.get('image_id')
    #
    # db = cloud_db.DbManager()
    # image_detail = db.retrieve_medical_image_by_id(image_id)
    # context['image_detail'] = image_detail
    #
    # logger.info('interpret_request get: %s' % request.GET)

    return render(request, 'miaas/interpretation_request.html', context)
    # return render(request, 'miaas/interpretation_request.html', sctx.default_context)


def physician_info_page(request):
    context = _get_session_context(request)
    return render(request, 'miaas/physician_info.html', sctx.default_context)


def physician_profile_page(request):
    context = _get_session_context(request)
    return render(request, 'miaas/physician_profile.html', context)


def _get_session_context(request):
    context = {}
    if 'user' in request.session.keys():
        context['user_session'] = request.session['user']
        if context.get('user_session'):
            context['user_session'].pop('password', None)
    return context


def opinion(request, opinion_id):
    return HttpResponse("Hello, opinion %s." % opinion_id)


def user(request, user_name):
    return HttpResponse("Hello, user %s." % user_name)


def template(request):
    return render(request, 'miaas/template.html', None)


def test_page(request):
    return render(request, 'miaas/test.html', None)


# KH
def interpretation_request_list_page(request):
    context = _get_session_context(request)
    if request.session.get('user'):
        logger.info('interpretation_request_list_page call db')

        now_page = request.GET.get('page')
        if not now_page or not request.session.get('intpr_request_list'):
            # Retrieve lists.
            db = cloud_db.DbManager()
            intpr_request_list = db.retrieve_patient_request_list(request.session['user']['user_id'])
            request.session['intpr_request_list'] = intpr_request_list
        else:
            intpr_request_list = request.session['intpr_request_list']
        intpr_request_cnt = len(intpr_request_list)
        if intpr_request_cnt <= 0:
            render(request, 'miaas/interpretation_request_list.html', context)
        intpr_request = {}
        request.session['request_cnt'] = intpr_request_cnt
        intpr_request['request_cnt'] = intpr_request_cnt

        # Configure number of pages
        if now_page: now_page = int(now_page)
        max_page = intpr_request_cnt // constants.CNT_CONTENTS_IN_PAGE
        if intpr_request_cnt % constants.CNT_CONTENTS_IN_PAGE > 0:
            max_page += 1
        if not now_page or now_page > max_page:
            now_page = 1
        intpr_request['now_page'] = now_page
        intpr_request['max_page'] = max_page
        logger.info('now_page=%s, max_page=%s' % (now_page, max_page))

        start_page = now_page - 4
        if start_page < 1: start_page = 1
        end_page = start_page + 9
        if end_page > max_page: end_page = max_page
        intpr_request['start_page'] = start_page
        intpr_request['end_page'] = end_page
        logger.info('start_page=%s, end_page=%s' % (start_page, max_page))

        # Render page
        offset = (now_page-1)*constants.CNT_CONTENTS_IN_PAGE
        intpr_request['intpr_request_list'] = intpr_request_list[offset:offset+constants.CNT_CONTENTS_IN_PAGE]
        context['intpr_request'] = intpr_request

    logger.info('interpretation_request_list_page get: %s' % request.GET)
    return render(request, 'miaas/interpretation_request_list.html', context)


# KH
def interpretation_request_detail_page(request, request_id):
    context = _get_session_context(request)
    if request.session.get('user'):
        logger.info('interpretation_request_detail_page call db')
        # Retrieve details.
        db = cloud_db.DbManager()
        physician_response = {}
        request_detail, responses = db.retrieve_patient_request_detail(request_id)
        physician_response['responses'] = responses
        context['request_detail'] = request_detail
        context['physician_response'] = physician_response
        logger.info("Status:%s" % request_detail['status'])
    logger.info('interpretation_request_detail_page get: %s' % request.GET)
    return render(request, 'miaas/interpretation_request_detail.html', context)


# KH
def physician_interpretation_search(request):
    context = _get_session_context(request)
    if request.session.get('user'):
        logger.info('physician_interpretation_search call db')
        # Get variables to configure db query
        query_type = request.GET.get('query_type')
        request_subject = request.GET.get('request_subject')
        image_type = request.GET.get('image_type')
        # Retrieve requested list
        now_page = request.GET.get('page')
        if not now_page or not request.session.get('requested_intpr_list'):
            # Retrieve lists.
            db = cloud_db.DbManager()
            requested_intpr_list = db.retrieve_requested_intpr_list(query_type, request_subject, image_type,
                                                                    request.session['user']['user_id'])
            request.session['requested_intpr_list'] = requested_intpr_list
        else:
            requested_intpr_list = request.session['requested_intpr_list']
        requested_intpr_cnt = len(requested_intpr_list)
        if requested_intpr_cnt <= 0:
            return render(request, 'miaas/interpretation_search.html', context)
        requested_intpr = {}
        request.session['requested_intpr_cnt'] = requested_intpr_cnt
        requested_intpr['requested_intpr_cnt'] = requested_intpr_cnt

        # Configure page number
        if now_page: now_page = int(now_page)
        max_page = requested_intpr_cnt // constants.CNT_CONTENTS_IN_PAGE
        if requested_intpr_cnt % constants.CNT_CONTENTS_IN_PAGE > 0:
            max_page += 1
        if not now_page or now_page > max_page:
            now_page = 1
        requested_intpr['now_page'] = now_page
        requested_intpr['max_page'] = max_page
        logger.info('now_page=%s, max_page=%s' % (now_page, max_page))

        start_page = now_page - 4
        if start_page < 1: start_page = 1
        end_page = start_page + 9
        if end_page > max_page: end_page = max_page
        requested_intpr['start_page'] = start_page
        requested_intpr['end_page'] = end_page
        logger.info('start_page=%s, end_page=%s' % (start_page, max_page))

        # Render the page
        offset = (now_page-1)*constants.CNT_CONTENTS_IN_PAGE
        requested_intpr['requested_intpr_list'] = requested_intpr_list[offset:offset+constants.CNT_CONTENTS_IN_PAGE]
        context['requested_intpr'] = requested_intpr

    logger.info('physician_interpretation_search get: %s' % request.GET)
    return render(request, 'miaas/interpretation_search.html', context)


# KH
def physician_interpretation_response_page(request):
    context = _get_session_context(request)
    if request.session.get('user'):
        logger.info('physician_interpretation_response_page call db')
        now_page = request.GET.get('page')
        if not now_page or not request.session.get('intpr_response_list'):
            # Retrieve lists.
            db = cloud_db.DbManager()
            intpr_response_list = db.retrieve_physician_response_list(request.session['user']['user_id'])
            request.session['intpr_response_list'] = intpr_response_list
        else:
            intpr_response_list = request.session['intpr_response_list']

        intpr_response_cnt = len(intpr_response_list)
        if intpr_response_cnt <= 0:
            render(request, 'miaas/interpretation_response_list.html', context)
        intpr_response = {}
        request.session['intpr_response_cnt'] = intpr_response_cnt
        intpr_response['intpr_response_cnt'] = intpr_response_cnt
        # Configure number of pages
        if now_page: now_page = int(now_page)
        max_page = intpr_response_cnt // constants.CNT_CONTENTS_IN_PAGE
        if intpr_response_cnt % constants.CNT_CONTENTS_IN_PAGE > 0:
            max_page += 1
        if not now_page or now_page > max_page:
            now_page = 1
        intpr_response['now_page'] = now_page
        intpr_response['max_page'] = max_page
        logger.info('now_page=%s, max_page=%s' % (now_page, max_page))

        start_page = now_page - 4
        if start_page < 1: start_page = 1
        end_page = start_page + 9
        if end_page > max_page: end_page = max_page
        intpr_response['start_page'] = start_page
        intpr_response['end_page'] = end_page
        logger.info('start_page=%s, end_page=%s' % (start_page, max_page))

        # Render page
        offset = (now_page-1)*constants.CNT_CONTENTS_IN_PAGE
        intpr_response['intpr_response_list'] = intpr_response_list[offset:offset+constants.CNT_CONTENTS_IN_PAGE]
        context['intpr_response'] = intpr_response

    logger.info('interpretation_request_list_page get: %s' % request.GET)
    return render(request, 'miaas/interpretation_response_list.html', context)


# KH
def physician_interpretation_write(request, request_id):
    context = _get_session_context(request)
    if request.session.get('user'):
        logger.info('physician_interpretation_write call db')
        # Retrieve details.
        db = cloud_db.DbManager()
        request_detail = db.retrieve_request_info(request_id)
        context['request_detail'] = request_detail
        logger.info("status:%s" % request_detail['status'])
    logger.info('interpretation_request_detail_page get: %s' % request.GET)
    return render(request, 'miaas/interpretation_write.html', context)


# KH
def interpretation_page(request):
    context = _get_session_context(request)
    if request.session.get('user'):
        now_page = request.GET.get('page')
        if not now_page or not request.session.get('intpr_list'):
            # Retrieve lists.
            db = cloud_db.DbManager()
            intpr_list = db.retrieve_patient_intpr_list(request.session['user']['user_id'])
            request.session['intpr_list'] = intpr_list
        else:
            intpr_list = request.session['intpr_list']
        intpr_cnt = len(intpr_list)
        logger.info(request.session['user']['user_id'])
        logger.info('intpr_cnt=%s', intpr_cnt)
        if intpr_cnt <= 0:
            return render(request, 'miaas/interpretation.html', context)
        intpr = {}
        request.session['intpr_cnt'] = intpr_cnt
        intpr['intpr_cnt'] = intpr_cnt

        # Configure page number
        if now_page: now_page = int(now_page)
        max_page = intpr_cnt // constants.CNT_CONTENTS_IN_PAGE
        if intpr_cnt % constants.CNT_CONTENTS_IN_PAGE > 0:
            max_page += 1
        if not now_page or now_page > max_page:
            now_page = 1
        intpr['now_page'] = now_page
        intpr['max_page'] = max_page
        logger.info('now_page=%s, max_page=%s' % (now_page, max_page))
        start_page = now_page - 4
        if start_page < 1: start_page = 1
        end_page = start_page + 9
        if end_page > max_page: end_page = max_page
        intpr['start_page'] = start_page
        intpr['end_page'] = end_page
        logger.info('start_page=%s, end_page=%s' % (start_page, max_page))

        # Render the page
        offset = (now_page-1)*constants.CNT_CONTENTS_IN_PAGE
        intpr['interpret_list'] = intpr_list[offset:offset+constants.CNT_CONTENTS_IN_PAGE]
        context['interpret'] = intpr

    logger.info('interpret get: %s' % request.GET)
    return render(request, 'miaas/interpretation.html', context)


# KH
def physician_interpretation_page(request):
    context = _get_session_context(request)
    if request.session.get('user'):
        logger.info('physician_interpretation_page call db')
        now_page = request.GET.get('page')
        if not now_page or not request.session.get('physician_intpr_list'):
            # Retrieve lists.
            db = cloud_db.DbManager()
            physician_intpr_list = db.retrieve_physician_intpr_list(request.session['user']['user_id'])
            request.session['physician_intpr_list'] = physician_intpr_list
        else:
            physician_intpr_list = request.session['physician_intpr_list']

        physician_intpr_cnt = len(physician_intpr_list)
        logger.info(request.session['user']['user_id'])
        logger.info('intpr_cnt=%s', physician_intpr_cnt)
        if physician_intpr_cnt <= 0:
            return render(request, 'miaas/interpretation_physician.html', context)
        physician_intpr = {}
        request.session['physician_intpr_cnt'] = physician_intpr_cnt
        physician_intpr['physician_intpr_cnt'] = physician_intpr_cnt
        # Configure page number
        if now_page: now_page = int(now_page)
        max_page = physician_intpr_cnt // constants.CNT_CONTENTS_IN_PAGE
        if physician_intpr_cnt % constants.CNT_CONTENTS_IN_PAGE > 0:
            max_page += 1
        if not now_page or now_page > max_page:
            now_page = 1
        physician_intpr['now_page'] = now_page
        physician_intpr['max_page'] = max_page
        logger.info('now_page=%s, max_page=%s' % (now_page, max_page))

        start_page = now_page - 4
        if start_page < 1: start_page = 1
        end_page = start_page + 9
        if end_page > max_page: end_page = max_page
        physician_intpr['start_page'] = start_page
        physician_intpr['end_page'] = end_page
        logger.info('start_page=%s, end_page=%s' % (start_page, max_page))

        # Render the page
        offset = (now_page-1)*constants.CNT_CONTENTS_IN_PAGE
        physician_intpr['physician_intpr_list'] = physician_intpr_list[offset:offset+constants.CNT_CONTENTS_IN_PAGE]
        context['physician_intpr'] = physician_intpr

    logger.info('physician_interpretation_page get: %s' % request.GET)
    return render(request, 'miaas/interpretation_physician.html', context)


def interpretation_detail_page(request, intpr_id):
    context = _get_session_context(request)
    if request.session.get('user'):
        logger.info('interpretation_detail_page call db')
        # Interpretation details.
        db = cloud_db.DbManager()
        intpr_detail = db.retrieve_interpretation_detail(intpr_id)

        context['intpr_detail'] = intpr_detail

    logger.info('interpretation_detail_page get: %s' % request.GET)
    return render(request, 'miaas/interpretation_detail.html', context)


def physician_interpretation_detail_page(request, intpr_id):
    context = _get_session_context(request)
    if request.session.get('user'):
        logger.info('interpretation_detail_page call db')
        # Interpretation details.
        db = cloud_db.DbManager()
        physician_intpr_detail = db.retrieve_physician_interpretation_detail(intpr_id)

        context['physician_intpr_detail'] = physician_intpr_detail

    logger.info('physician_interpretation_detail_page get: %s' % request.GET)
    return render(request, 'miaas/interpretation_physician_detail.html', context)


def physician_request_search_detail_page(request, request_id):
    context = _get_session_context(request)
    if request.session.get('user'):
        logger.info('physician_request_search_detail_page call db')
        # Retrieve details.
        db = cloud_db.DbManager()
        request_detail = db.retrieve_request_info(request_id)
        context['request_detail'] = request_detail
        logger.info("status:%s" % request_detail['status'])
    logger.info('physician_request_search_detail_page get: %s' % request.GET)
    return render(request, 'miaas/interpretation_search_detail.html', context)
