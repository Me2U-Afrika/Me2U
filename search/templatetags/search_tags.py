from django import template
from search.forms import SearchForm
import urllib.parse
from categories.models import Category, Department

register = template.Library()


@register.inclusion_tag("tags/search_box.html")
def search_box(request):
    q = request.GET.get('q', '')
    category_searched = request.GET.get('category_searched', '')
    active_departments = Department.active.all()

    form = SearchForm({
        'q': q,
        'category_searched': category_searched,
    })
    return {'form': form,
            'departments': active_departments}


@register.inclusion_tag("tags/search_menu.html")
def search_menu(request):
    q = request.GET.get('q', '')
    form = SearchForm({'q': q})
    return {'form': form}


@register.inclusion_tag('tags/pagination_links.html')
def pagination_links(request, paginator):
    raw_params = request.GET.copy()
    page = raw_params.get('page', 1)
    p = paginator.page(page)
    try:
        del raw_params['page']
    except KeyError:
        pass
    params = urllib.parse.urlencode(raw_params)
    return {'request': request,
            'paginator': paginator,
            'p': p,
            'params': params
            }
