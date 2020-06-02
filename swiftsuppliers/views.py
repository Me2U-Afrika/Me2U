from django.shortcuts import render

from django.http import HttpResponse


def ssupplier(request):
    return render(request, 'swiftsupplier/ssupplier.html')
    # return HttpResponse('wondering')
