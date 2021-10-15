from django.shortcuts import render
from django.core.cache import cache
from django.views.generic import DetailView


# Create your views here.
from Me2U import settings


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
    from ipware import get_client_ip
    client_ip, is_routable = get_client_ip(request)
    if client_ip is None:
        print('Unable to get the client\'s IP address')
    else:
        # We got the client's IP address
        if is_routable:
            print('ip is routable')
            print(client_ip)
        else:
            print(client_ip)
            print('it is private')

    # Order of precedence is (Public, Private, Loopback, None)
    import geoip2.webservice

    # to "geolite.info"
    try:
        client = geoip2.webservice.Client(settings.GEO_ACCOUNT_ID, settings.GEO_LICENCE_KEY, host='geolite.info')
        response = client.city('203.0.113.0')
        country = response.country.name
        print('response city:', response)
        print('country:', country)

        return country
    except Exception as e:
        print("Error IP: ", e)

    # x_forwarded_for = request.META.get('HTTP_X_FORWARED_FOR')
    # ip = '203.0.113.0'

    # if x_forwarded_for:
    #     ip = x_forwarded_for.split(',')[0]
    # else:
    #     ip = request.META.get('REMOTE_ADDR')

    # g = GeoIP2()
    # try:
    #     location = g.city(ip)
    #     location_country = location['country_name']
    #     location_city = location['city']
    #     print(location_city)
    #     print(location_country)
    #     return '{}-{}'.format(location_country, location_city)
    #
    # except Exception as e:
    #     print(e)




