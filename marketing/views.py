from django.shortcuts import render
from django.http import HttpResponse
from Me2U.settings import BASE_DIR

import os

# Create your views here.

ROBOTS_PATH = os.path.join(BASE_DIR, 'marketing/robots.txt')


def robots(request):
    return HttpResponse(open(ROBOTS_PATH).read(), 'text/plain')
