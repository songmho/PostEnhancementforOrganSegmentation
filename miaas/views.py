__author__ = 'hanter'

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views import generic

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

def index(request):
    context = {
        'has_session': False,
    }
    return render(request, 'miaas/index.html', context)

def login(request):
    return render(request, 'miaas/login.html', default_context);

def opinion(request, opinion_id):
    return HttpResponse("Hello, opinion %s." % opinion_id)

def user(request, user_name):
    return HttpResponse("Hello, user %s." % user_name)

