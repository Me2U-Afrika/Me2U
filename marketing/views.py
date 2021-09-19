from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from Me2U.settings import BASE_DIR
from .forms import EmailForm
from .models import MarketingEmails, FAQ, FAQCategory

import os
import json

# Create your views here.

ROBOTS_PATH = os.path.join(BASE_DIR, 'marketing/robots.txt')


def robots(request):
    return HttpResponse(open(ROBOTS_PATH).read(), 'text/plain')


from django.views.decorators.cache import never_cache


@never_cache
def email_signup(request):
    if request.method == "POST":
        postdata = request.POST.copy()
        form = EmailForm(postdata)
        if form.is_valid():
            email = form.cleaned_data['email']
            marketing_email, created = MarketingEmails.objects.get_or_create(email=email)
            request.session['marketing_email_added'] = True
            return HttpResponse('Success %s' % marketing_email)
        if form.errors:
            json_data = json.dumps(form.errors)
            return HttpResponseBadRequest(json_data, content_type='application/json')

    elif request.method == "GET":
        form = EmailForm
        context = {
            'form': form
        }
        return render(request, "tags/modal.html", context)

    else:
        raise Http404


def FAQs(request):
    q_category = FAQCategory.objects.all()

    return render(request, 'marketing/FAQs.html', locals())
