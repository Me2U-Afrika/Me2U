from django.shortcuts import render
from django.template import RequestContext
from . import search
from django.conf import settings
from django.views.generic import ListView, DetailView, View
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from .search import _prepare_words
from Me2U.settings import PRODUCTS_PER_ROW


def search_results(request, template_name="search/results.html"):
    # get current search phrase
    q = request.GET.get('q', '')
    prepared_words = _prepare_words(q)
    # print(prepared_words)

    # get current page number. Set to 1 is missing or invalid
    try:
        page = int(request.GET.get('page', 1))

    except ValueError:
        page = 1

    matching = []
    for words in range(len(prepared_words)):
        print(prepared_words[words])
        while words < len(prepared_words):
            results = search.productSearched(prepared_words[words]).get('products', [])
            # print('results for common:', results)

            for r in results:
                for product in r:
                    if len(matching) < PRODUCTS_PER_ROW and not product in matching:
                        matching.append(product)
            words += 1

    # generate the pagintor object
    # print('matching:', matching)
    paginator = Paginator(matching, settings.PRODUCTS_PER_PAGE)
    try:
        results = paginator.page(page).object_list
        # for product in result:
        # print('results', results)
        #     results = product
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
