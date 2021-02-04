from .models import SearchTerm
from me2ushop.models import Product, Brand
from django.db.models import Q
from stats import stats

STRIP_WORDS = ['a', 'an', 'i', 'am', 'and', 'by', 'for', 'from', 'in', 'no', 'not',
               'of', 'on', 'or', 'that', 'the', 'to', 'with', 'is', ',', 'Search', 'search']


def store(request, q):
    # print('request search:', request)
    # if search term is at least three chars long, store in db
    if len(q) > 2:
        term = SearchTerm()
        term.q = q
        term.ip_address = request.META.get('REMOTE_ADDR')
        term.tracking_id = stats.tracking_id(request)
        term.user = None
        if request.user.is_authenticated:
            term.user = request.user
        term.save()


# get products matching the search text
def productSearched(search_text, category):
    words = _prepare_words(search_text)
    # print('words:', search_text)

    products = Product.active.all()
    # print('products:', products)

    results = {'products': []}

    if category == 'All Categories' or category == '':
        print('searching all categories')

        for word in words:
            products = products.filter(Q(title__icontains=word) |
                                       Q(description__icontains=word) |
                                       Q(brand_name__title__icontains=word) |
                                       Q(meta_description__icontains=word) |
                                       Q(product_categories__category_name__icontains=word) |
                                       Q(meta_keywords__icontains=word)).distinct()
            if products:
                # print('found:', products)
                results['products'].append(products)
        # print(results)

    else:
        print('we came here to exact category choice')
        for word in words:
            products = products.filter(
                Q(product_categories__category_name__iexact=category) &
                Q(title__icontains=word) |
                Q(description__icontains=word) |
                Q(brand_name__title__icontains=word) |
                Q(meta_description__icontains=word) |
                Q(meta_keywords__icontains=word)).distinct()
            if products:
                # print('found:', products)
                results['products'].append(products)
        # print(results)

    return results


# strip out common words, limit to 5 words
def _prepare_words(search_text):
    words = search_text.replace(' ', ',').split(',')
    for common in STRIP_WORDS:
        if common in words:
            words.remove(common)
    for word in words:
        if len(word) < 3:
            words.remove(word)

    return words[0:5]

# Lookup funtion with a while loop
# iterate through keywords
# count = 0
#
# while count < len(words):
#     # print(words)
#     # print(words[count])
#     products = products.filter(Q(title__icontains=words[count]) |
#                                Q(description__icontains=words[count]) |
#                                Q(brand__icontains=words[count]) |
#                                Q(meta_description__icontains=words[count]) |
#                                Q(meta_keywords__icontains=words[count]))
#
#     if products:
#         print('found:', products)
#         results['products'].append(products)
#
#     words = words[count + 1:]
#     print('sliced:', words)
#     if len(words) == 0:
#         break
