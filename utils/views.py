from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.cache import cache
from django.urls import reverse
from django.views.generic import DetailView

# Create your views here.
from Me2U import settings
# from me2ushop.forms import DelivertoForm
from me2ushop.forms import UserLocationForm


class CachedDetailView(DetailView):
    def get_queryset(self):
        return super(CachedDetailView, self).get_queryset().select_related()

    def get_object(self, queryset=None):
        if self.request.user.is_authenticated:
            obj = None

            if not obj:
                obj = super(CachedDetailView, self).get_object(queryset)
                cache.set('%s-%s' % (self.model.__name__.lower(), self.kwargs['slug']), obj)
        else:
            obj = cache.get('%s-%s' % (self.model.__name__.lower(), self.kwargs['slug']), None)

            if not obj:
                obj = super(CachedDetailView, self).get_object(queryset)
                cache.set('%s-%s' % (self.model.__name__.lower(), self.kwargs['slug']), obj)

        return obj


from django.shortcuts import render, HttpResponse
from django.contrib.gis.geoip2 import GeoIP2


def user_location(request):
    print('we got to location from url')

    from ipware import get_client_ip
    context = {}

    client_ip, is_routable = get_client_ip(request)
    if client_ip is None:
        print('Unable to get the client\'s IP address')
    else:
        # We got the client's IP address
        if is_routable:
            # print('ip is routable')
            # print(client_ip)
            import geoip2.webservice

            # to "geolite.info"
            try:
                client = geoip2.webservice.Client(settings.GEO_ACCOUNT_ID, settings.GEO_LICENCE_KEY,
                                                  host='geolite.info')
                response = client.city(client_ip)
                country = response.country.name
                # print('response city:', response)
                request.session['country'] = country
                request.session['country_code'] = response.country.iso_code

            except Exception as e:
                print("Error IP: ", e)

    if request.method == 'POST':
        try:
            session_country = request.session['country']
            print('session_country_start:', session_country)
        except Exception as e:
            print(e)

        form = UserLocationForm(request.POST or None)
        if form.is_valid():
            country_code = form.cleaned_data.get('country')
            print('country_code', country_code)
            from django_countries import countries
            country = countries.name(country_code)
            request.session['country'] = country
            request.session['country_code'] = country_code
            print('session_country_end:', request.session['country'])

        referer = request.META['HTTP_REFERER']

        return HttpResponseRedirect(referer)

    # Order of precedence is (Public, Private, Loopback, None)

    # x_forwarded_for = request.META.get('HTTP_X_FORWARED_FOR')
    #
    # if x_forwarded_for:
    #     ip = x_forwarded_for.split(',')[0]
    # else:
    #     ip = request.META.get('REMOTE_ADDR')

    # ip = '78.31.205.137'
    # ip = '102.22.187.72'
    # ip = '41.206.127.0'

    # g = GeoIP2()
    # try:
    #     location = g.city(ip)
    #     # print('location:', location)
    #     location_country = location['country_name']
    #     location_city = location['city']
    #     print(location_city)
    #     print(location_country)
    #     context.update({'country': location_country,
    #                     'country_code': location['country_code']})
    #     return context
    #
    # except Exception as e:
    #     print(e)
