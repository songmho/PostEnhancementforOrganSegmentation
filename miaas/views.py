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

def index_page(request):
    context = {
        'session': sctx.default_session,
    }
    return render(request, 'miaas/index.html', context)

# login reference: https://www.fir3net.com/Web-Development/Django/django.html
def signin_page(request):
    return render(request, 'miaas/signin.html', None)

def signup_page(request):
    return render(request, 'miaas/signup.html', None)

def profile_page(request):
    return render(request, 'miaas/patient_profile.html', sctx.default_context)

def archive_page(request):
    return render(request, 'miaas/archive.html', sctx.archive_context)

def archive_upload_page(request):
    return render(request, 'miaas/medical_image_upload.html', sctx.default_context)

def medical_image_page(request, img_num):
    return render(request, 'miaas/medical_image.html', sctx.default_context)

def interpretation_page(request):
    return render(request, 'miaas/interpretation.html', sctx.interpret_context)

def interpretation_detail_page(request, interpret_num):
    ctx = sctx.default_context.copy()
    interpret_list = sctx.interpret_context['interpret']['interpret_list']
    sel_num = len(interpret_list)-int(interpret_num)-1
    ctx['status'] = interpret_list[sel_num]['status']
    ctx['subject'] = interpret_list[sel_num]['subject']
    if(ctx['status'] == '2' or ctx['status'] == 2):
        ctx['candidate_list'] = [
            {
                'id': 'hanterkr',
                'name': 'Han Ter Jung',
                'message': 'Nulla ut ipsum turpis. Quisque ac cursus velit. Morbi nisl odio, blandit eget dignissim eget, rutrum nec leo. Phasellus vitae ante metus. In tempor leo.'
            }, {
                'id': 'khan',
                'name': 'Ku Hwan An',
                'message': 'Aenean id tellus orci. Phasellus eu pulvinar turpis. Pellentesque hendrerit interdum aliquet. Ut dignissim in arcu quis tincidunt. Vestibulum quis enim eu nunc lobortis sodales.'
            }, {
                'id': 'mkdmkk',
                'name': 'Moon Kwon Kim',
                'message': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec blandit rhoncus ultricies. Praesent viverra finibus tortor sed ultrices. Pellentesque habitant morbi tristique senectus et netus.'
            }
        ]
    return render(request, 'miaas/interpretation_detail.html', ctx)

def interpretation_request_page(request):
    return render(request, 'miaas/interpretation_request.html', sctx.default_context)

def interpretation_candidate_page(request, interpret_num):
    return render(request, 'miaas/interpretation_candidate.html', sctx.default_context)

def signout(request):
    pass

def opinion(request, opinion_id):
    return HttpResponse("Hello, opinion %s." % opinion_id)

def user(request, user_name):
    return HttpResponse("Hello, user %s." % user_name)

def template(request):
    return render(request, 'miaas/template.html', None)
