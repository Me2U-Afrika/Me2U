from .models import SearchTerm
from me2ushop.models import Product
from django.db.models import Q

STRIP_WORDS = ['a', 'an', 'am', 'and', 'by', 'for', 'from', 'in', 'no', 'not',
               'of', 'on', 'or', 'that', 'the', 'to', 'with', 'is', ',']


def store(request, q):
    # if search term is at least three chars long, store in db
    if len(q) > 2:
        term = SearchTerm()
        term.q = q
        term.ip_address = request.META.get('REMOTE_ADDR')
        term.user = None
        if request.user.is_authenticated:
            term.user = request.user
        term.save()


# get products matching the search text
def productSearched(search_text):
    words = _prepare_words(search_text)
    print('words:', words)

    products = Product.active.all()
    print('products:', products)

    results = {'products': []}

    for word in words:
        print('word:', word)
        products = products.filter(Q(title__icontains=word) |
                                   Q(description__icontains=word) |
                                   Q(brand__icontains=word) |
                                   Q(meta_description__icontains=word) |
                                   Q(meta_keywords__icontains=word))
        if products:
            print('found:', products)
            results['products'].append(products)
    print(results)

    return results


# strip out common words, limit to 5 words
def _prepare_words(search_text):
    words = search_text.replace(' ', ',').split(',')
    for common in STRIP_WORDS:
        if common in words:
            words.remove(common)
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
