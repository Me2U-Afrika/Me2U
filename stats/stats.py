import os
import base64
import codecs

from search.models import SearchTerm
from Me2U.settings import PRODUCTS_PER_ROW
import collections
from me2ushop.models import Product
from .models import ProductView


def tracking_id(request):
    try:
        return request.session['tracking_id']
    except KeyError:
        request.session['tracking_id'] = codecs.encode(os.urandom(32), 'hex').decode()

        return request.session['tracking_id']


def recommended_from_search(request):
    from search import search

    # Get the common words from the stored searches
    common_words = frequent_search_words(request)
    # print('common words:', common_words)
    category = 'All Categories'

    matching = []
    for words in range(len(common_words)):
        # print(words)
        while words < len(common_words):
            results = search.productSearched(common_words[words], category).get('products', [])
            # print('results for common:', results)

            for r in results:
                for product in r:
                    if len(matching) < PRODUCTS_PER_ROW and not product in matching:
                        matching.append(product)
            words += 1

    # print('matching found:', matching)

    # c = collections.Counter(matching)
    # for product, count in c.most_common():
    # print('%s: %7d' % (product, count))
    # most_words.append(word)
    # print('most_products:', most_words)

    # return the top three most common words in the searches

    # return most_words
    return matching


def frequent_search_words(request):
    # get the ten most recent searches from the database.
    if request.user.is_authenticated:
        searches = SearchTerm.objects.filter(user=request.user).values('q').order_by('-search_date')[0:10]
        # print(searches)
    else:
        searches = SearchTerm.objects.filter(tracking_id=tracking_id(request)).values('q').order_by('-search_date')[
                   0:10]
    # print('searches found:', searches)

    # Join all searches together into a single string
    search_string = ' '.join([search['q'] for search in searches])
    # print('q.string:', search_string)
    words = search_string.split()
    most_words = []

    c = collections.Counter(words)
    # print('common:', c)

    for word, count in c.most_common(10):
        # print('%s: %7d' % (product, count))
        most_words.append(word)
    # print('most_products:', most_words)

    # return the top three most common words in the searches

    return most_words


def log_product_view(request, product):
    # print('r', request)
    # print('p', product)

    track_id = tracking_id(request)
    # print('T', track_id)

    try:
        view = ProductView.objects.get(tracking_id=track_id, product=product)
        view.save()
    except ProductView.DoesNotExist:
        view = ProductView()
        view.product = product
        view.ip_address = request.META.get('REMOTE_ADDR')
        # print('ip', view.ip_address)
        view.tracking_id = track_id
        view.user = None
        if request.user.is_authenticated:
            view.user = request.user
        view.save()


def recommended_from_views(request):
    track_id = tracking_id(request)

    # get recently viewed products
    viewed = get_recently_viewed(request)
    # print('viewed by me:', viewed)

    # if there are previously viewed products, get other tracking ids that have viewed
    # those products also
    if viewed:
        productviews = ProductView.objects.filter(product__in=viewed).values('tracking_id')

        track_ids = [view['tracking_id'] for view in productviews]

        # if there are other tracking ides, get other products.
        if track_ids:
            all_viewed = Product.active.filter(productview__tracking_id__in=track_ids)
            # print('all_viewed:', all_viewed)
            #     if there are other products, get them, excluding the
            #      producus that the customer has already viewed.
            if all_viewed:
                other_viewed = ProductView.objects.filter(product__in=all_viewed).exclude(product__in=viewed)
                # print('others_viewed_track_ids:', other_viewed)

                if other_viewed:
                    products = Product.active.filter(productview__in=other_viewed).distinct()
                    # print('products others viewed i havent:', products)
                    return products


def get_recently_viewed(request):
    track_id = tracking_id(request)
    # print("looked up id:", track_id)
    views = ProductView.objects.filter(tracking_id=track_id).values('product_id').order_by('-date')

    product_ids = [view['product_id'] for view in views]
    # print('product_ids', product_ids)
    products = Product.active.filter(id__in=product_ids)
    # print('products:', products)
    return products


def recommended_from_other_sellers(request):
    pass
