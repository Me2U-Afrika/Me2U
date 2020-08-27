from django.shortcuts import render
from .models import Category
from me2ushop.models import Product
from django.views.generic import ListView, DetailView, View
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from stats import stats
from Me2U.settings import PRODUCTS_PER_ROW
from django.http import HttpResponse
from django.core import serializers


# from django.template import RequestContext
# from me2ushop.forms import CartAddProductForm
#
#
def get_json_products(request):
    products = Product.active.all()
    json_products = serializers.serialize("json", products)
    return HttpResponse(json_products, content_type='application/javascript; charset=utf-8')


def categoriesHomePage(request):
    print('request', request)
    page_title = 'Categories'
    site_name = 'Me2U|Market'
    template_name = 'index.html'

    return render(request, template_name, locals())


class CategoryDetailedView(DetailView):
    model = Category
    paginate_by = 12
    template_name = 'category.html'
    query_pk_and_slug = True

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailedView, self).get_context_data(**kwargs)

        # c = Category.active.all()
        # print('c:', c)
        # category_list = {'c': []}
        # for c in c:
        #     p = c.product_set.all()
        #     for item in p:
        #         if item.made_in_africa:
        #             pass
        # category = item.product_categories.order_by('category_name').distinct()
        # print('categories:', category)
        # african_category = list(set(category))

        # print('cat:', african_category)

        # context['category '] = category
        # return context
        # print('category:', category)

        # print('category_list:', category_list)

        # context['c'] = category
        # print('c:', c)

        # page_title = c.category_name
        # meta_description = c.meta_description
        # meta_keywords = c.meta_keywords

        return context
    #
    # def get_queryset(self):
    #     category_slug = self.kwargs['slug']
    #     print('category:', category_slug)
    #     self.category = None
    #     if category_slug != "all":
    #         self.category = get_object_or_404(Category, slug=category_slug)
    #     if self.category:
    #         products = Product.active.all().filter(product_categories=self.category)
    #     else:
    #         products = Product.active.all()
    #     print('products qs:', products)
    #     return products.order_by('title')


class CategoryDetailedView_africa_made(DetailView):
    model = Category
    paginate_by = 12
    template_name = 'category_africa_made.html'
    query_pk_and_slug = True

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailedView_africa_made, self).get_context_data(**kwargs)

        made_in_africa = []
        categories = Category.active.all()
        # print('all:', categories)
        for category in categories:
            products = category.product_set.all()
            # print('products:', products)
            for item in products:
                if item.made_in_africa and category not in made_in_africa:
                    made_in_africa.append(category)

        print('mda:', made_in_africa)
        context.update({'made_in_africa': made_in_africa})

        return context
