from Me2U.settings import PRODUCTS_PER_ROW
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render
from stats import stats

from . import search
from .search import _prepare_words


def search_results(request, template_name="home/search_results.html"):
    # get current search phrase
    print(request)
    q = request.GET.get('q', '')
    category = request.GET.get('category_searched', '')
    # print('name:', category)
    prepared_words = _prepare_words(q)
    # print(prepared_words)

    # get current page number. Set to 1 is missing or invalid
    try:
        page = int(request.GET.get('page', 1))

    except ValueError:
        page = 1

    matching = []
    for words in range(len(prepared_words)):
        # print(prepared_words[words])
        while words < len(prepared_words):
            results = search.productSearched(prepared_words[words], category).get('products', [])
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
    matching_count = len(matching)
    print('matching count:', matching_count)
    search.store(request, q)

    # recent views
    # recent_views = stats.get_recently_viewed(request)
    # if recent_views:
    #     recently_viewed = recent_views

    # recommended from previous search
    search_recored = stats.recommended_from_search(request)
    if search_recored:
        search_recored = search_recored


    # the usual…
    if category != '':
        page_title = 'Search Results for: ' + q + 'in' + category
    else:
        page_title = 'Search Results for: ' + q
    # context_instance = RequestContext(request)
    return render(request, template_name, locals())
