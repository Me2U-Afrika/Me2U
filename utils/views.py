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
