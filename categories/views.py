from .models import Category, Department
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import DetailView
from me2ushop.models import Product

from .models import Category, Department


# from django.template import RequestContext

def get_json_products(request):
    products = Product.active.all()
    json_products = serializers.serialize("json", products)
    return HttpResponse(json_products, content_type='application/javascript; charset=utf-8')


def categoriesHomePage(request):
    # print('request', request)
    page_title = 'Categories'
    site_name = 'Me2U|Market'
    template_name = 'categories.html'

    return render(request, template_name, locals())


class CategoryDetailedView(DetailView):
    model = Category
    paginate_by = 12
    template_name = 'category.html'
    query_pk_and_slug = True

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailedView, self).get_context_data(**kwargs)

        context.update({
            'page_title': str(self.get_object()),
        })

        return context


class DepartmentDetailedView(DetailView):
    model = Department
    paginate_by = 12
    template_name = 'home/category.html'
    query_pk_and_slug = True

    def get_context_data(self, **kwargs):
        context = super(DepartmentDetailedView, self).get_context_data(**kwargs)

        title = self.get_object()
        # print('obj:', title)
        page_title = str(title)
        context.update({
            'page_title': page_title
        })

        return context


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

        # print('mda:', made_in_africa)
        context.update({'made_in_africa': made_in_africa})

        return context
