from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
import datetime as dt
from django.contrib.auth.decorators import login_required
from .models import MaDere


# Create your views here.

def welcome(request):

    return render(request, 'Me2U_home.html')


def aboutus(request):
    return HttpResponse('Daniel Ogechi is the CEO')


# We first update our news_today view function we call the render
# function and pass in 3 arguments. The request, the template file,
# and a dictionary of values that we pass into the template. This
# dictionary is referred to as the Context in Django and contains
# the context variables that are rendered inside the template.

@login_required()
def our_drivers(request):
    # day = convert_dates(date)
    date = dt.date.today()

    context = {
        'madriver': MaDere.objects.all()
    }

    return render(request, 'MaDriversWetu.html', context)

# the convert dates function is now being taken care of by the date filter in the base html

# def convert_dates(dates):
#     # get int of the day
#     day_number = dt.date.weekday(dates)
#
#     days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', "Sunday"]
#
#     # returning day
#     day = days[day_number]
#     return day

# @login_required()
# def past_days_news(request, past_date):
#     # pass
#     try:
#         # convert data from string to url
#         date = dt.datetime.strptime(past_date, '%Y-%m-%d').date()
#
#     except ValueError:
#         # raise 404 error when valueerror is thrown
#         raise Http404()
#         # assert False
#
#     # day = convert_dates(date)
#
#     if date == dt.date.today():
#         return redirect(news_of_day)
#
#     return render(request, 'all-Me2UAfricaMain/past-Me2UAfricaMain.html', {"date": date})
