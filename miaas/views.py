__author__ = 'hanter'

from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.http import *
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

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

default_context = {}
default_session = {
    'session_id': 1234,
    'session_start': '2016/01/27 14:06:33',
    'user_info': {
        'id': 'hanterkr',
        'user_name': 'Hanter Jung',
        'user_type': 'patient',
    }
}

def index(request):
    context = {
        'session': default_session,
    }
    return render(request, 'miaas/index.html', context)

# login reference: https://www.fir3net.com/Web-Development/Django/django.html
def signin(request):
    return render(request, 'miaas/signin.html', None)

def signout(request):
    pass

def signup(request):
    return render(request, 'miaas/signup.html', None)

def opinion(request, opinion_id):
    return HttpResponse("Hello, opinion %s." % opinion_id)

def user(request, user_name):
    return HttpResponse("Hello, user %s." % user_name)

def template(request):
    return render(request, 'miaas/template.html', None)
