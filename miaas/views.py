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
import logging, json

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

def account_page(request):
    context = _get_session_context(request)
    return render(request, 'miaas/account.html', context)

def profile_page(request):
    context = _get_session_context(request)
    # logger.info(context)
    return render(request, 'miaas/patient_profile.html', context)

def archive_page(request):
    context = _get_session_context(request)
    # return render(request, 'miaas/archive.html', sctx.archive_context)
    return render(request, 'miaas/archive.html', context)

def archive_upload_page(request):
    context = _get_session_context(request)
    # return render(request, 'miaas/medical_image_upload.html', sctx.default_context)
    return render(request, 'miaas/medical_image_upload.html', context)

def medical_image_page(request, img_num):
    context = _get_session_context(request)
    # return render(request, 'miaas/medical_image.html', sctx.default_context)
    return render(request, 'miaas/medical_image.html', context)

def interpretation_page(request):
    context = _get_session_context(request)
    return render(request, 'miaas/interpretation.html', sctx.interpret_context)
    # return render(request, 'miaas/interpretation.html', context)

def interpretation_detail_page(request, interpret_num):
    context = _get_session_context(request)

    # context = sctx.default_context.copy()
    interpret_list = sctx.interpret_context['interpret']['interpret_list']
    sel_num = len(interpret_list)-int(interpret_num)-1
    context['status'] = interpret_list[sel_num]['status']
    context['subject'] = interpret_list[sel_num]['subject']
    context['level'] = interpret_list[sel_num]['level']
    if(context['status'] == '2' or context['status'] == 2):
        context['candidate_list'] = [
            {
                'id': 'hanterkr',
                'name': 'Han Ter Jung',
                'field': 'Heart Specialist',
                'message': 'Nulla ut ipsum turpis. Quisque ac cursus velit. Morbi nisl odio, blandit eget dignissim eget, rutrum nec leo. Phasellus vitae ante metus. In tempor leo.'
            }, {
                'id': 'khan',
                'name': 'Ku Hwan An',
                'field': 'Heart Specialist',
                'message': 'Aenean id tellus orci. Phasellus eu pulvinar turpis. Pellentesque hendrerit interdum aliquet. Ut dignissim in arcu quis tincidunt. Vestibulum quis enim eu nunc lobortis sodales.'
            }, {
                'id': 'mkdmkk',
                'name': 'Moon Kwon Kim',
                'field': 'Thoracic Specialist',
                'message': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec blandit rhoncus ultricies. Praesent viverra finibus tortor sed ultrices. Pellentesque habitant morbi tristique senectus et netus.'
            }
        ]
    return render(request, 'miaas/interpretation_detail.html', context)

def interpretation_request_page(request):
    context = _get_session_context(request)
    return render(request, 'miaas/interpretation_request.html', sctx.default_context)

def physician_info_page(request):
    context = _get_session_context(request)
    return render(request, 'miaas/physician_info.html', sctx.default_context)

def physician_profile_page(request):
    context = _get_session_context(request)
    return render(request, 'miaas/physician_profile.html', context)

def physician_interpretation_page(request):
    context = _get_session_context(request)
    return render(request, 'miaas/interpretation_physician.html', sctx.interpret_physician_context)

def physician_interpretation_search(request):
    context = _get_session_context(request)
    return render(request, 'miaas/interpretation_search.html', sctx.interpret_search_context)

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