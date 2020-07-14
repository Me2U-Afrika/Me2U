from django.shortcuts import render
from django.template import RequestContext
from . import search
from django.conf import settings
from django.views.generic import ListView, DetailView, View
from django.core.paginator import Paginator, InvalidPage, EmptyPage


def search_results(request, template_name="search/results.html"):
    # get current search phrase
    q = request.GET.get('q', '')

    # get current page number. Set to 1 is missing or invalid
    try:
        page = int(request.GET.get('page', 1))

    except ValueError:
        page = 1
    # retrieve the matching products
    matching = search.productSearched(q).get('products')

    # generate the pagintor object
    paginator = Paginator(matching, settings.PRODUCTS_PER_PAGE)
    try:
        result = paginator.page(page).object_list
        for product in result:
            # print('results', product)
            results = product
            # return results
            # for item in product:
            #     print('item', item)

    except (InvalidPage, EmptyPage):
        results = paginator.page(1).object_list

    # store the search
    search.store(request, q)

    # the usual…
    page_title = 'Search Results for: ' + q
    # context_instance = RequestContext(request)
    return render(request, template_name, locals())
