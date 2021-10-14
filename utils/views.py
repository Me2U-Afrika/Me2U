from django.shortcuts import render
from django.core.cache import cache
from django.views.generic import DetailView


# Create your views here.

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
    x_forwarded_for = request.META.get('HTTP_X_FORWARED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    g = GeoIP2()
    try:
        location = g.city(ip)
        location_country = location['country_name']
        location_city = location['city']
        print(location_city)
        print(location_country)
        return '{}-{}'.format(location_country, location_city)

    except Exception as e:
        print(e)



